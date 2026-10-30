param([Parameter(Mandatory=$true)][string]$Id,[string]$Version='v1')
$ErrorActionPreference = 'Stop'
$taskRoot = 'D:\work\doudizhu-image'
$taskOut = Join-Path $taskRoot 'designs\ui\support'
$taskReceiptName = if($Version -eq 'v1'){$Id}else{$Id+'-'+$Version}
$taskReceiptPath = Join-Path $taskOut ("receipts\" + $taskReceiptName + ".receipt.json")
$taskReceipt = Get-Content -LiteralPath $taskReceiptPath -Raw | ConvertFrom-Json
$taskSource = [regex]::Match($taskReceipt.output_hint, 'as (.+?\.png) by default\.').Groups[1].Value
if (-not $taskSource -or -not (Test-Path -LiteralPath $taskSource)) { throw '工具返回的原生图片文件未找到' }
$taskTarget = Join-Path $taskOut ($Id + '-'+$Version+'.png')
if (Test-Path -LiteralPath $taskTarget) { throw "不覆盖既有图片：$taskTarget" }
Copy-Item -LiteralPath $taskSource -Destination $taskTarget
Add-Type -AssemblyName System.Drawing
$taskImg = [System.Drawing.Image]::FromFile($taskTarget)
$taskWidth = $taskImg.Width
$taskHeight = $taskImg.Height
$taskPixelFormat = $taskImg.PixelFormat.ToString()
$taskImg.Dispose()
$taskScope = Get-Content -LiteralPath (Join-Path $taskRoot 'docs\UI_SCOPE.json') -Raw | ConvertFrom-Json
$taskPage = $taskScope.pages | Where-Object id -eq $Id
$taskConfig = Get-Content -LiteralPath (Join-Path $taskRoot 'config\image-generation.json') -Raw | ConvertFrom-Json
$taskPromptPath = Join-Path $taskRoot ("prompts\support\" + $Id + '-'+$Version+'.txt')
$taskReferences = foreach($taskRef in $taskReceipt.submittedArguments.referenced_image_paths) {
 [ordered]@{file=$taskRef.Replace('\','/').Replace('D:/work/doudizhu-image/',''); sha256=(Get-FileHash -LiteralPath $taskRef -Algorithm SHA256).Hash.ToLower(); role='实际附带风格或人物参考'}
}
$taskGeneration = [ordered]@{
 schemaVersion=1; file=('designs/ui/support/'+$Id+'-'+$Version+'.png'); sha256=(Get-FileHash -LiteralPath $taskTarget -Algorithm SHA256).Hash.ToLower()
 generatedAt=$taskReceipt.recordedAt; generatedAtEvidence='工具返回后记录的UTC完成时间代理；非模型内部时间'
 width=$taskWidth; height=$taskHeight; format='PNG'
 nativeResolution=[ordered]@{width=$taskWidth;height=$taskHeight}; exportOperation='byte-identical-copy; no resize or redraw'
 requestedResolution=[ordered]@{width=2560;height=1080;note='提示词目标；工具未提供尺寸选择器'}
 tool='image_gen.imagegen'; route='builtin'; callId=$null; resultId=$null
 configSnapshot=$taskConfig
 submittedParameters=[ordered]@{model=$null;quality=$null;transparent_background=$false;referenced_image_paths=$taskReceipt.submittedArguments.referenced_image_paths}
 actualModel=$taskReceipt.actualModel; actualQuality=$taskReceipt.actualQuality
 unverifiedReason='宿主管理，工具未披露／无可核实元数据；无型号与质量选择器，配置不能证明实际锁定Sunburst/max'
 prompt=("prompts/support/"+$Id+'-'+$Version+'.txt'); promptSha256=(Get-FileHash -LiteralPath $taskPromptPath -Algorithm SHA256).Hash.ToLower()
 references=$taskReferences; evidence=[ordered]@{receipt=("designs/ui/support/receipts/"+$taskReceiptName+'.receipt.json');sourcePath=$taskSource;toolReturnKeys=$taskReceipt.toolReturnKeys}
 inspection=[ordered]@{status='awaiting_visual_review'; notes=@();pixelFormat=$taskPixelFormat}
}
$taskGeneration | ConvertTo-Json -Depth 15 | Set-Content -LiteralPath (Join-Path $taskOut ($Id+'-'+$Version+'.generation.json')) -Encoding utf8
[ordered]@{id=$Id;file=$taskTarget;width=$taskWidth;height=$taskHeight;sha256=$taskGeneration.sha256} | ConvertTo-Json

