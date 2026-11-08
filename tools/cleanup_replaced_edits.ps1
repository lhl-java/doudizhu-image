$ErrorActionPreference='Stop'
$taskRoot=[System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$taskScope=Get-Content -LiteralPath (Join-Path $taskRoot 'docs/UI_SCOPE.json') -Raw | ConvertFrom-Json
$taskTargets=@(
    @{ Id='27-tournament-detail'; Batch='modes' },
    @{ Id='29-tournament-result'; Batch='modes' },
    @{ Id='42-leaderboard'; Batch='support' },
    @{ Id='59-achievements-growth'; Batch='support' }
)
$taskLog=@()
foreach($taskEntry in $taskTargets) {
    $taskPrefix='designs/ui/'+$taskEntry.Batch+'/'+$taskEntry.Id
    $taskOldRelative=$taskPrefix+'-v1.png'
    $taskNewRelative=$taskPrefix+'-v2.png'
    $taskSelected=$taskScope.pages | Where-Object { $_.id -eq $taskEntry.Id }
    if($taskSelected.output -ne $taskNewRelative) { throw ('未选定v2，不删除：'+$taskEntry.Id) }
    $taskOldPath=[System.IO.Path]::GetFullPath((Join-Path $taskRoot $taskOldRelative))
    $taskNewPath=[System.IO.Path]::GetFullPath((Join-Path $taskRoot $taskNewRelative))
    if(-not $taskOldPath.StartsWith($taskRoot+[System.IO.Path]::DirectorySeparatorChar,[System.StringComparison]::OrdinalIgnoreCase)) { throw '目标越界' }
    $taskOldRecordPath=$taskOldPath.Replace('.png','.generation.json')
    $taskNewRecordPath=$taskNewPath.Replace('.png','.generation.json')
    $taskOldRecord=Get-Content -LiteralPath $taskOldRecordPath -Raw | ConvertFrom-Json
    $taskNewRecord=Get-Content -LiteralPath $taskNewRecordPath -Raw | ConvertFrom-Json
    $taskNewHash=(Get-FileHash -LiteralPath $taskNewPath -Algorithm SHA256).Hash.ToLower()
    if($taskNewHash -ne $taskNewRecord.sha256) { throw '新成品哈希不一致' }
    if(Test-Path -LiteralPath $taskOldPath) {
        $taskOldHash=(Get-FileHash -LiteralPath $taskOldPath -Algorithm SHA256).Hash.ToLower()
        if($taskOldHash -ne $taskOldRecord.sha256) { throw '旧稿哈希不一致，停止' }
        Remove-Item -LiteralPath $taskOldPath
    }
    $taskRemoved=[ordered]@{ status='removed_superseded_image'; replacedBy=$taskNewRelative; retainedGenerationRecord=$taskOldRecordPath.Substring($taskRoot.Length+1).Replace('\','/'); removedAt=[DateTimeOffset]::UtcNow.ToString('o'); reason='成品v2已落盘、选用并核验；依用户素材保留规则删除替代图片，保留历史来源文字与哈希。' }
    $taskOldRecord | Add-Member -NotePropertyName imageRemoved -NotePropertyValue $true -Force
    $taskOldRecord | Add-Member -NotePropertyName retention -NotePropertyValue $taskRemoved -Force
    foreach($taskReference in $taskNewRecord.references) {
        if(($taskReference.file -eq $taskOldRelative) -or ($taskReference.path -eq $taskOldRelative)) {
            $taskReference | Add-Member -NotePropertyName imageRemoved -NotePropertyValue $true -Force
            $taskReference | Add-Member -NotePropertyName retainedRecord -NotePropertyValue ($taskPrefix+'-v1.generation.json') -Force
        }
    }
    if($taskNewRecord.editedFrom) { $taskNewRecord.editedFrom | Add-Member -NotePropertyName imageRemoved -NotePropertyValue $true -Force }
    $taskOldRecord | ConvertTo-Json -Depth 50 | Set-Content -LiteralPath $taskOldRecordPath -Encoding utf8
    $taskNewRecord | ConvertTo-Json -Depth 50 | Set-Content -LiteralPath $taskNewRecordPath -Encoding utf8
    $taskLog += [ordered]@{ file=$taskOldRelative; sha256=$taskOldRecord.sha256; selected=$taskNewRelative; selectedSha256=$taskNewHash; action='deleted-image-only-retained-generation-metadata' }
}
[ordered]@{ recordedAt=[DateTimeOffset]::UtcNow.ToString('o'); removedImageCount=$taskLog.Count; files=$taskLog; retainedPurpose='已选组合图所需的当前背景和组件源仍是有效制作资源；本次只清理四张AI编辑前替代稿。' } | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath (Join-Path $taskRoot 'docs/CLEANUP_20261026.json') -Encoding utf8
$taskLog | ConvertTo-Json -Depth 5

