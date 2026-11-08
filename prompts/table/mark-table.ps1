param([Parameter(Mandatory=$true)][string]$Id,[Parameter(Mandatory=$true)][string]$Note,[string]$Status='design_ready_user_review',[string]$Version='v1')
$ErrorActionPreference='Stop'
$taskRoot='D:\work\doudizhu-image'
$taskRecordRelative='designs/ui/table/'+$Id+'-'+$Version+'.generation.json'
$taskPath=Join-Path $taskRoot $taskRecordRelative
$taskRecord=Get-Content -LiteralPath $taskPath -Raw | ConvertFrom-Json
$taskRecord.visualReview.status=$Status
$taskRecord.visualReview.note=$Note
$taskRecord | ConvertTo-Json -Depth 14 | Set-Content -LiteralPath $taskPath -Encoding utf8
$taskStatePath=Join-Path $taskRoot ('designs/ui/table/'+$Id+'.states.json')
$taskState=Get-Content -LiteralPath $taskStatePath -Raw | ConvertFrom-Json
$taskState.status=$Status
$taskState.primaryVisual='designs/ui/table/'+$Id+'-'+$Version+'.png'
$taskState.generation=$taskRecordRelative
$taskState.renderedStateVerification=$Note
foreach($taskVariant in $taskState.states) {
  $taskVariant.coverage=$taskVariant.plannedCoverage
  if($taskVariant.plannedCoverage -eq 'rendered') {$taskVariant.artwork=$taskState.primaryVisual}
  $taskVariant.verification='rendered为当前已看图布局；shared_component为已有同源素材与原生动态层的复用规范，不表示已生成每个变体截图或已实现客户端'
}
$taskState | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $taskStatePath -Encoding utf8

