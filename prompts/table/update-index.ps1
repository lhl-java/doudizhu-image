$ErrorActionPreference='Stop'
$taskRoot='D:\work\doudizhu-image'
$taskScope=Get-Content -LiteralPath (Join-Path $taskRoot 'docs\UI_SCOPE.json') -Raw | ConvertFrom-Json
$taskRows=[System.Collections.Generic.List[string]]::new()
$taskRows.Add('# 牌局 UI 批次')
$taskRows.Add('')
$taskRows.Add('独占 11–22、53–55，共 15 项。画风沿用两张指定参考与本项目大厅、三人角色。每项独立整屏，逐图记录实际入口与来源。')
$taskRows.Add('')
$taskRows.Add('| 页面 | 选用成图 | 实际尺寸 | 状态 | 来源类型 |')
$taskRows.Add('|---|---|---|---|---|')
$taskEntries=@()
foreach($taskPage in @($taskScope.pages | Where-Object batch -eq 'table')) {
  $taskStatePath=Join-Path $taskRoot $taskPage.stateSpec
  $taskState=if(Test-Path -LiteralPath $taskStatePath) {Get-Content -LiteralPath $taskStatePath -Raw | ConvertFrom-Json} else {$null}
  $taskOutput=if($taskState) {$taskState.primaryVisual} else {$taskPage.output}
  $taskGeneration=if($taskState) {$taskState.generation} else {$taskPage.generation}
  $taskExists=Test-Path -LiteralPath (Join-Path $taskRoot $taskOutput)
  $taskRecord=if(Test-Path -LiteralPath (Join-Path $taskRoot $taskGeneration)) {Get-Content -LiteralPath (Join-Path $taskRoot $taskGeneration) -Raw | ConvertFrom-Json} else {$null}
  $taskStatus=if($taskRecord) {$taskRecord.visualReview.status} else {'pending'}
  $taskDimensions=if($taskRecord) {"$($taskRecord.width) × $($taskRecord.height)"} else {'—'}
  $taskRoute=if($taskRecord) {$taskRecord.route} else {'—'}
  $taskFilename=[System.IO.Path]::GetFileName($taskOutput)
  $taskRows.Add("| $($taskPage.id) · $($taskPage.title) | [$taskFilename]($taskFilename) | $taskDimensions | $taskStatus | $taskRoute |")
  $taskEntries+=@([pscustomobject][ordered]@{id=$taskPage.id;title=$taskPage.title;output=$taskOutput;generation=$taskGeneration;stateSpec=$taskPage.stateSpec;exists=$taskExists;status=$taskStatus;route=$taskRoute;width=if($taskRecord){$taskRecord.width}else{$null};height=if($taskRecord){$taskRecord.height}else{$null};note=if($taskRecord){$taskRecord.visualReview.note}else{'生成中或待落盘'}})
}
$taskRows.Add('')
$taskRows.Add('每页旁置 .states.json 逐项说明 requiredStates。rendered 表示当前选用画面已看图；shared_component 表示已有同源公共皮肤、牌面和原生动态文字层可复用的状态规范，不表示每种变体都有独立 AI 截图，也不表示客户端已实现。')
$taskRows.Add('')
$taskRows.Add('带 v2/v3 的 UI 组合稿把原生生成牌桌作为底图，再排版同源面板、身份徽章和正确点数牌面；记录 route=derived、derivedFrom、布局 JSON 与缩小/九宫格操作，不冒称新模型原生细节。原始源图的待修历史不改写。')
$taskRows.Add('')
$taskRows.Add('静态牌局均为视觉示意，玩法回执、发牌合法性、实时计时、自动操作、联网与最终业务规则由客户端/服务端接入验证。')
$taskRows.Add('')
$taskRows.Add('实际提示词及复现辅助脚本在 ../../../prompts/table/。生成目标为配置中的 GPT Image 2.5/max；当前工具未披露实际型号/质量，各源记录均保留 null 及理由。')
$taskRows | Set-Content -LiteralPath (Join-Path $taskRoot 'designs\ui\table\README.md') -Encoding utf8
[ordered]@{schemaVersion=1;batch='table';updatedAt=[DateTimeOffset]::UtcNow.ToString('o');total=$taskEntries.Count;ready=@($taskEntries | Where-Object status -eq 'design_ready_user_review').Count;pages=$taskEntries} | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $taskRoot 'designs\ui\table\manifest.json') -Encoding utf8
$taskEntries | Select-Object id,status,output | ConvertTo-Json -Depth 5

