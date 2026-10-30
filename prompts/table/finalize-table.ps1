param(
  [Parameter(Mandatory=$true)][string]$Id,
  [Parameter(Mandatory=$true)][string]$SourcePath
)
$ErrorActionPreference = 'Stop'
$taskRoot = 'D:\work\doudizhu-image'
$taskBatch = Join-Path $taskRoot 'designs\ui\table'
New-Item -ItemType Directory -Path $taskBatch -Force | Out-Null
$taskTarget = Join-Path $taskBatch ($Id + '-v1.png')
if (Test-Path -LiteralPath $taskTarget) { throw "目标已存在，避免覆盖：$taskTarget" }
Copy-Item -LiteralPath $SourcePath -Destination $taskTarget
Add-Type -AssemblyName System.Drawing
$taskImage = [System.Drawing.Image]::FromFile($taskTarget)
try { $taskWidth = $taskImage.Width; $taskHeight = $taskImage.Height; $taskPixelFormat = $taskImage.PixelFormat.ToString() } finally { $taskImage.Dispose() }
$taskScope = Get-Content -LiteralPath (Join-Path $taskRoot 'docs\UI_SCOPE.json') -Raw | ConvertFrom-Json
$taskPage = $taskScope.pages | Where-Object id -eq $Id
$taskReceiptPath = Join-Path $taskBatch ($Id + '-v1.receipt.json')
$taskReceipt = Get-Content -LiteralPath $taskReceiptPath -Raw | ConvertFrom-Json
$taskConfig = Get-Content -LiteralPath (Join-Path $taskRoot 'config\image-generation.json') -Raw | ConvertFrom-Json
$taskPromptRelative = 'prompts/table/' + $Id + '-v1.txt'
$taskPromptPath = Join-Path $taskRoot $taskPromptRelative
$taskReferences = @(
  @{ file = 'references/style/01-mail-event.png'; role = '首要风格参考：玉绿米白暖金、纸绢、云纹、角色画法' },
  @{ file = 'references/style/team-ui-v2.png'; role = '首要风格参考：标题、卡片、按钮、留白与头像' },
  @{ file = 'designs/ui/lobby-ui-v1.png'; role = '本项目大厅同源风格' },
  @{ file = 'designs/characters/characters-trio-v1.png'; role = '本项目三人角色身份与画法' }
) | ForEach-Object { [ordered]@{ file = $_.file; sha256 = (Get-FileHash -LiteralPath (Join-Path $taskRoot $_.file) -Algorithm SHA256).Hash.ToLower(); role = $_.role; usage = 'actually-attached-to-imagegen' } }
$taskRecordedAt = [DateTimeOffset]::UtcNow
$taskRecord = [ordered]@{
  schemaVersion = 1
  file = $taskPage.output
  sha256 = (Get-FileHash -LiteralPath $taskTarget -Algorithm SHA256).Hash.ToLower()
  generatedAt = $taskReceipt.finished.current_time
  generatedAtEvidence = '工具返回后UTC时钟，作为完成时间代理；不是模型内部时间'
  recordedAt = [TimeZoneInfo]::ConvertTime($taskRecordedAt, [TimeZoneInfo]::FindSystemTimeZoneById('Eastern Standard Time')).ToString('o')
  width = $taskWidth
  height = $taskHeight
  format = 'PNG'
  nativeResolution = @{ width = $taskWidth; height = $taskHeight }
  exportOperation = 'byte-identical-copy-no-resize'
  requestedResolution = @{ width = 2560; height = 1080; evidence = '提示词目标，工具无尺寸选择器，实际以上方实测为准' }
  tool = 'image_gen.imagegen'
  route = 'builtin'
  configSnapshot = $taskConfig
  submittedParameters = @{ model = $null; quality = $null; transparent_background = $false; referenced_image_paths = @($taskReferences | ForEach-Object { Join-Path $taskRoot $_.file }) }
  actualModel = $taskReceipt.returnedModel
  actualQuality = $taskReceipt.returnedQuality
  unverifiedReason = '宿主管理，工具未披露／无可核实元数据；配置和提示词不能作为实际分支或质量的证据'
  evidence = @{ receipt = ('designs/ui/table/' + $Id + '-v1.receipt.json'); hostOutputFile = $SourcePath; toolReturnedKeys = $taskReceipt.keys; metadataInspection = 'System.Drawing读取实际尺寸和像素格式，未验证C2PA'; pixelFormat = $taskPixelFormat }
  prompt = $taskPromptRelative
  promptSha256 = (Get-FileHash -LiteralPath $taskPromptPath -Algorithm SHA256).Hash.ToLower()
  references = $taskReferences
  visualReview = @{ status = 'pending_visual_review'; note = '稍后逐图实际查看后记录'; }
}
$taskRecord | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $taskBatch ($Id + '-v1.generation.json')) -Encoding utf8
[ordered]@{ id = $Id; file = $taskPage.output; width = $taskWidth; height = $taskHeight; sha256 = $taskRecord.sha256 } | ConvertTo-Json

