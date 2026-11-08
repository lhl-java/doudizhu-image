$ErrorActionPreference='Stop'
$taskRoot='D:\work\doudizhu-image'
$taskManifest=Get-Content -LiteralPath (Join-Path $taskRoot 'designs\ui\table\manifest.json') -Raw | ConvertFrom-Json
$taskScope=Get-Content -LiteralPath (Join-Path $taskRoot 'docs\UI_SCOPE.json') -Raw | ConvertFrom-Json
$taskFailures=[System.Collections.Generic.List[string]]::new()
$taskSourceCount=0
$taskReferenceCount=0
foreach($taskPage in $taskManifest.pages) {
  $taskImagePath=Join-Path $taskRoot $taskPage.output
  $taskRecordPath=Join-Path $taskRoot $taskPage.generation
  $taskStatePath=Join-Path $taskRoot $taskPage.stateSpec
  if(-not(Test-Path -LiteralPath $taskImagePath -PathType Leaf) -or -not(Test-Path -LiteralPath $taskRecordPath -PathType Leaf) -or -not(Test-Path -LiteralPath $taskStatePath -PathType Leaf)) {$taskFailures.Add('缺文件 '+$taskPage.id);continue}
  $taskRecord=Get-Content -LiteralPath $taskRecordPath -Raw | ConvertFrom-Json
  if((Get-FileHash -LiteralPath $taskImagePath -Algorithm SHA256).Hash.ToLower() -ne $taskRecord.sha256) {$taskFailures.Add('成图哈希 '+$taskPage.id)}
  $taskState=Get-Content -LiteralPath $taskStatePath -Raw | ConvertFrom-Json
  $taskExpected=($taskScope.pages | Where-Object id -eq $taskPage.id).requiredStates
  if(Compare-Object @($taskExpected) @($taskState.states.name)) {$taskFailures.Add('状态清单 '+$taskPage.id)}
  foreach($taskSource in @($taskRecord.derivedFrom | Where-Object {$null -ne $_ -and $_.file})) {
    $taskSourceCount++
    if(-not(Test-Path -LiteralPath (Join-Path $taskRoot $taskSource.file) -PathType Leaf)) {$taskFailures.Add('来源缺失 '+$taskPage.id+' '+$taskSource.file)}
    elseif((Get-FileHash -LiteralPath (Join-Path $taskRoot $taskSource.file) -Algorithm SHA256).Hash.ToLower() -ne $taskSource.sha256) {$taskFailures.Add('来源哈希 '+$taskPage.id+' '+$taskSource.file)}
    if($taskSource.record -and -not(Test-Path -LiteralPath (Join-Path $taskRoot $taskSource.record) -PathType Leaf)) {$taskFailures.Add('来源记录 '+$taskPage.id+' '+$taskSource.record)}
  }
  foreach($taskReference in @($taskRecord.references | Where-Object {$null -ne $_ -and $_.file})) {
    $taskReferenceCount++
    if(-not(Test-Path -LiteralPath (Join-Path $taskRoot $taskReference.file) -PathType Leaf)) {$taskFailures.Add('参考缺失 '+$taskPage.id+' '+$taskReference.file)}
    elseif((Get-FileHash -LiteralPath (Join-Path $taskRoot $taskReference.file) -Algorithm SHA256).Hash.ToLower() -ne $taskReference.sha256) {$taskFailures.Add('参考哈希 '+$taskPage.id+' '+$taskReference.file)}
  }
}
$taskValidation=[ordered]@{
  batch='table';checkedAt=[DateTimeOffset]::UtcNow.ToString('o');selectedPages=$taskManifest.pages.Count
  ready=@($taskManifest.pages | Where-Object status -eq 'design_ready_user_review').Count
  selectedHashes='checked';requiredStates='checked';directSourceHashEntries=$taskSourceCount;referenceHashEntries=$taskReferenceCount
  failures=@($taskFailures);status=if($taskFailures.Count -eq 0){'passed'}else{'failed'}
  limit='文件/哈希/状态映射核验及本批逐图视觉检查，不代表客户端、逐状态截图或完整牌局合法性验收'
}
$taskValidation | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath (Join-Path $taskRoot 'designs\ui\table\validation.json') -Encoding utf8
$taskValidation | ConvertTo-Json -Depth 7
if($taskFailures.Count -gt 0){exit 1}

