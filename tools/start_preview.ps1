param([int]$Port = 8771, [ValidateSet('art','design','states')][string]$View = 'art')
$ErrorActionPreference = 'Stop'
$taskRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$taskServer = Join-Path $PSScriptRoot 'serve_preview.py'
$taskRuntime = 'C:\Users\luyua\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (-not (Test-Path -LiteralPath $taskRuntime)) { $taskRuntime = (Get-Command python -ErrorAction Stop).Source }
$taskPage = @{ art='runtime/art-preview.html'; design='preview/index.html'; states='preview/states.html' }[$View]
$taskUrl = "http://127.0.0.1:$Port/$taskPage"
$taskExisting = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($taskExisting) {
    $taskResponse = Invoke-WebRequest -Uri $taskUrl -TimeoutSec 5
    $taskMarker = if ($View -eq 'art') { 'src="art-preview.js"' } else { 'src="catalog.js"' }
    if (-not $taskResponse.Content.Contains($taskMarker)) { throw "端口 $Port 已被其他服务使用" }
    if ($View -eq 'art') {
        $taskModule = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/runtime/table-art.mjs" -Method Head -TimeoutSec 5
        if ($taskModule.Headers['Content-Type'] -notmatch 'javascript') {
            throw "端口 $Port 上的旧预览服务无法加载 JavaScript 模块。请用 -Port 8772 启动。"
        }
    }
    Write-Output $taskUrl
    exit 0
}
$taskLogRoot = Join-Path $taskRoot '.work\preview'
New-Item -ItemType Directory -Path $taskLogRoot -Force | Out-Null
$taskProcess = Start-Process -FilePath $taskRuntime -ArgumentList @(('"' + $taskServer + '"'), "$Port") -WindowStyle Hidden -RedirectStandardOutput (Join-Path $taskLogRoot 'stdout.log') -RedirectStandardError (Join-Path $taskLogRoot 'stderr.log') -PassThru
@{ pid = $taskProcess.Id; url = $taskUrl; root = $taskRoot } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskLogRoot 'server.json') -Encoding utf8
Write-Output $taskUrl
