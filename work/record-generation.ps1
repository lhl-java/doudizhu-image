[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$ImagePath,
    [Parameter(Mandatory = $true)][string]$PromptPath,
    [Parameter(Mandatory = $true)][string]$ReceiptPath,
    [ValidateRange(1, 100000)][int]$RequestedWidth,
    [ValidateRange(1, 100000)][int]$RequestedHeight,
    [string]$StartedAtUtc,
    [string]$FinishedAtUtc
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$projectRoot = 'D:\work\doudizhu-image'
$projectPrefix = $projectRoot.TrimEnd('\') + '\'

function Resolve-ProjectFile([string]$Candidate) {
    if (-not [System.IO.Path]::IsPathRooted($Candidate)) {
        throw "必须提供绝对路径：$Candidate"
    }
    $resolved = [System.IO.Path]::GetFullPath($Candidate)
    if (-not $resolved.StartsWith($projectPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "文件须位于项目目录内：$resolved"
    }
    if (-not (Test-Path -LiteralPath $resolved -PathType Leaf)) {
        throw "文件不存在：$resolved"
    }
    return $resolved
}

function Get-RelativeProjectPath([string]$Absolute) {
    return $Absolute.Substring($projectPrefix.Length).Replace('\', '/')
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Convert-UtcTimestamp([string]$Value) {
    if ([string]::IsNullOrWhiteSpace($Value)) { return $null }
    if ($Value -notmatch '(Z|[+-]\d\d:\d\d)$') {
        throw "时间必须带时区（例如 2026-10-26T20:15:00Z）：$Value"
    }
    return ([DateTimeOffset]::Parse($Value, [Globalization.CultureInfo]::InvariantCulture)).ToUniversalTime().ToString('o')
}

$imageFile = Resolve-ProjectFile $ImagePath
$promptFile = Resolve-ProjectFile $PromptPath
$receiptFile = Resolve-ProjectFile $ReceiptPath
$sidecar = Join-Path ([System.IO.Path]::GetDirectoryName($imageFile)) (([System.IO.Path]::GetFileNameWithoutExtension($imageFile)) + '.generation.json')
if (Test-Path -LiteralPath $sidecar) { throw "记录已存在，不覆盖：$sidecar" }

$configPath = Join-Path $projectRoot 'config\image-generation.json'
$manifestPath = Join-Path $projectRoot 'references\style\manifest.json'
$config = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
$manifest = @(Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json)
$receipt = Get-Content -LiteralPath $receiptFile -Raw -Encoding UTF8 | ConvertFrom-Json
$promptText = Get-Content -LiteralPath $promptFile -Raw -Encoding UTF8
$started = Convert-UtcTimestamp $StartedAtUtc
$finished = Convert-UtcTimestamp $FinishedAtUtc
$recordedAt = [DateTimeOffset]::UtcNow.ToString('o')
if ($finished) {
    $generationTime = $finished
    $timeSource = 'caller-provided-response-received-at'
    $timeNote = '以调用方提供的工具返回接收时间代理生成完成时间；不是模型内部生成时间。'
} else {
    $generationTime = $recordedAt
    $timeSource = 'sidecar-record-created-at'
    $timeNote = '未提供工具返回接收时间，以本记录创建时间代理；不是已核实的模型生成时间。'
}

$references = @()
foreach ($relative in @('references/style/01-mail-event.png', 'references/style/team-ui-v2.png')) {
    $referencePath = Resolve-ProjectFile (Join-Path $projectRoot $relative)
    $entries = @($manifest | Where-Object { $_.file -eq $relative })
    if ($entries.Count -ne 1) { throw "参考清单必须包含唯一记录：$relative" }
    $actualHash = Get-Sha256 $referencePath
    $expectedHash = ([string]$entries[0].sha256).ToLowerInvariant()
    if ($actualHash -ne $expectedHash) { throw "参考图哈希与 manifest 不一致：$relative" }
    $references += [ordered]@{
        file = $relative
        absolutePath = $referencePath
        sha256 = $actualHash
        role = [string]$entries[0].role
        usage = 'actual-style-reference-attached-to-image-generation'
        manifest = 'references/style/manifest.json'
        manifestSha256 = $expectedHash
        manifestHashMatched = $true
    }
}

# Decode the existing file for inspection only. No bitmap is written or transformed.
Add-Type -AssemblyName System.Drawing
$bitmap = $null
$lock = $null
try {
    $bitmap = [System.Drawing.Bitmap]::FromFile($imageFile)
    $width = $bitmap.Width
    $height = $bitmap.Height
    $rawFormatGuid = $bitmap.RawFormat.Guid.ToString()
    $format = switch ($rawFormatGuid) {
        'b96b3caf-0728-11d3-9d7b-0000f81ef32e' { 'PNG' }
        'b96b3cae-0728-11d3-9d7b-0000f81ef32e' { 'JPEG' }
        'b96b3cb0-0728-11d3-9d7b-0000f81ef32e' { 'GIF' }
        'b96b3cb1-0728-11d3-9d7b-0000f81ef32e' { 'TIFF' }
        'b96b3cab-0728-11d3-9d7b-0000f81ef32e' { 'BMP' }
        'b96b3cb5-0728-11d3-9d7b-0000f81ef32e' { 'ICO' }
        default { 'UNKNOWN' }
    }
    $sourcePixelFormat = $bitmap.PixelFormat.ToString()
    $hasAlphaChannel = (([int]$bitmap.PixelFormat -band [int][System.Drawing.Imaging.PixelFormat]::Alpha) -ne 0)
    $sourceMayContainAlpha = $hasAlphaChannel -or (($bitmap.Flags -band 2) -ne 0)
    $hasNonOpaquePixels = $false
    $alphaScanMethod = 'source-format-reports-no-alpha'
    if ($sourceMayContainAlpha) {
        $rect = New-Object System.Drawing.Rectangle(0, 0, $width, $height)
        $lock = $bitmap.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::ReadOnly, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
        $rowBytes = New-Object byte[] ($width * 4)
        :Rows for ($y = 0; $y -lt $height; $y++) {
            $rowPointer = [IntPtr]::Add($lock.Scan0, ($y * $lock.Stride))
            [System.Runtime.InteropServices.Marshal]::Copy($rowPointer, $rowBytes, 0, $rowBytes.Length)
            for ($x = 3; $x -lt $rowBytes.Length; $x += 4) {
                if ($rowBytes[$x] -lt 255) {
                    $hasNonOpaquePixels = $true
                    break Rows
                }
            }
        }
        $alphaScanMethod = 'read-only-decoded-pixel-alpha-scan-stops-at-first-nonopaque-pixel'
    }
} finally {
    if ($null -ne $lock -and $null -ne $bitmap) { $bitmap.UnlockBits($lock) }
    if ($null -ne $bitmap) { $bitmap.Dispose() }
}

$unverifiedReason = '宿主管理，工具未披露／无可核实元数据。当前内置 image_gen.imagegen 接口没有 model、quality 选择器，配置只表示用户目标；不能据此声称实际锁定 GPT Image 2.5 Sunburst 或 max。未检查或验证 C2PA。'
$record = [ordered]@{
    schemaVersion = 1
    file = Get-RelativeProjectPath $imageFile
    absolutePath = $imageFile
    sha256 = Get-Sha256 $imageFile
    generatedAt = $generationTime
    generatedAtEvidence = [ordered]@{ isProxy = $true; source = $timeSource; explanation = $timeNote }
    recordedAt = $recordedAt
    startedAtUtc = $started
    finishedAtUtc = $finished
    width = $width
    height = $height
    format = $format
    nativeResolution = [ordered]@{ width = $width; height = $height }
    exportResolution = [ordered]@{ width = $width; height = $height; operation = 'byte-identical-copy-of-generated-output-no-resize-or-redraw' }
    requestedResolution = [ordered]@{
        width = $(if ($PSBoundParameters.ContainsKey('RequestedWidth')) { $RequestedWidth } else { $null })
        height = $(if ($PSBoundParameters.ContainsKey('RequestedHeight')) { $RequestedHeight } else { $null })
        note = '提示词中的尺寸目标；内置工具无独立尺寸选择参数，实际尺寸以上方实测值为准。'
    }
    transparency = [ordered]@{
        requestedTransparentBackground = $false
        sourcePixelFormat = $sourcePixelFormat
        hasAlphaChannel = $hasAlphaChannel
        hasNonOpaquePixels = $hasNonOpaquePixels
        fullyOpaque = -not $hasNonOpaquePixels
        inspectionMethod = $alphaScanMethod
    }
    tool = 'image_gen.imagegen'
    route = 'builtin'
    callId = $null
    resultId = $null
    configSnapshot = $config
    submittedParameters = [ordered]@{
        model = $null
        quality = $null
        transparent_background = $false
        referenced_image_paths = @($references | ForEach-Object { $_.absolutePath })
        prompt = $receipt.submittedArguments.prompt
    }
    actualModel = $null
    actualQuality = $null
    unverifiedReason = $unverifiedReason
    prompt = Get-RelativeProjectPath $promptFile
    promptSha256 = Get-Sha256 $promptFile
    references = $references
    evidence = [ordered]@{
        receipt = Get-RelativeProjectPath $receiptFile
        receiptSha256 = Get-Sha256 $receiptFile
        returnedEvidence = $receipt
        metadataInspection = 'System.Drawing 只读检查实际尺寸、格式和透明度；未验证 C2PA，未从配置推断实际模型或质量。'
        rawFormatGuid = $rawFormatGuid
    }
    status = '首版待用户确认'
    visualQA = [ordered]@{ status = '待实际看图检查'; inspectedAt = $null; findings = @() }
}

$json = $record | ConvertTo-Json -Depth 100
# CreateNew is atomic: even a concurrent writer cannot be overwritten.
$stream = [System.IO.File]::Open($sidecar, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
$writer = $null
try {
    $writer = New-Object System.IO.StreamWriter($stream, (New-Object System.Text.UTF8Encoding($false)))
    $writer.Write($json)
    $writer.Write([Environment]::NewLine)
} finally {
    if ($null -ne $writer) { $writer.Dispose() } else { $stream.Dispose() }
}

[pscustomobject]@{
    record = $sidecar
    image = $imageFile
    width = $width
    height = $height
    format = $format
    sha256 = $record.sha256
    fullyOpaque = $record.transparency.fullyOpaque
    status = $record.status
} | ConvertTo-Json -Depth 5
