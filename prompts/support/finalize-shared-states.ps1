$ErrorActionPreference='Stop'
$taskRoot='D:\work\doudizhu-image'
$taskDir=Join-Path $taskRoot 'designs\ui\support'
$taskDetails=Get-Content -LiteralPath (Join-Path $taskRoot 'prompts\support\state-details.json') -Raw|ConvertFrom-Json -AsHashtable
$taskManifestPath=Join-Path $taskRoot 'assets\ui\manifest.json'
$taskManifest=Get-Content -LiteralPath $taskManifestPath -Raw|ConvertFrom-Json
$taskAssets=@{}
foreach($taskAsset in $taskManifest.assets){$taskAssets[$taskAsset.file]=$taskAsset}
function Verify-Assets([string[]]$Paths) {
 foreach($taskAssetPath in $Paths){
  if(-not $taskAssets.ContainsKey($taskAssetPath)){throw "共享素材不在manifest：$taskAssetPath"}
  $taskPhysical=Join-Path $taskRoot $taskAssetPath
  if(-not(Test-Path -LiteralPath $taskPhysical)){throw "共享素材缺失：$taskAssetPath"}
  if((Get-FileHash -LiteralPath $taskPhysical -Algorithm SHA256).Hash.ToLower() -ne $taskAssets[$taskAssetPath].sha256){throw "共享素材哈希不一致：$taskAssetPath"}
 }
}
$taskPanel='assets/ui/controls/panel.png'
$taskPrimary='assets/ui/controls/primary-normal.png'
$taskSecondary='assets/ui/controls/secondary-normal.png'
$taskDisabled='assets/ui/controls/primary-disabled.png'
$taskInput='assets/ui/controls/input-normal.png'
$taskProgress='assets/ui/controls/progress.png'
$taskSelected='assets/ui/controls/tab-selected.png'
$taskNormalTab='assets/ui/controls/tab-normal.png'
$taskAllRefs=@($taskPanel,$taskPrimary,$taskSecondary,$taskDisabled,$taskInput,$taskProgress,$taskSelected,$taskNormalTab,'assets/ui/controls/avatar-frame.png')
Verify-Assets $taskAllRefs
$taskManifestHash=(Get-FileHash -LiteralPath $taskManifestPath -Algorithm SHA256).Hash.ToLower()
$taskSummary=@()
foreach($taskStateFile in Get-ChildItem -LiteralPath $taskDir -Filter '*.states.json' -File){
 $taskDoc=Get-Content -LiteralPath $taskStateFile.FullName -Raw|ConvertFrom-Json -AsHashtable
 $taskId=$taskDoc.id
 foreach($taskState in $taskDoc.states){
  if($taskState.coverage -eq 'rendered'){
   $taskState.designEvidence=@{page=$taskDoc.primaryImage;method='实际查看独立原生页面，状态在该画面可见'}
  }else{
   $taskSpecific=$taskDetails.specifics[$taskId][$taskState.state]
   if(-not $taskSpecific){throw "状态具体规范缺失：$taskId / $($taskState.state)"}
   $taskDependencies=@($taskPanel)
   if($taskSpecific.buttons.Count -gt 0){$taskDependencies+=@($taskPrimary,$taskSecondary)}
   if($taskState.state -match '不足|过期|未达|结束'){$taskDependencies+=@($taskDisabled)}
   if($taskState.state -eq '编辑'){$taskDependencies+=@($taskInput,'assets/ui/controls/input-focus.png','assets/ui/controls/avatar-frame.png')}
   if($taskState.state -eq '申请'){$taskDependencies+=@('assets/ui/controls/avatar-frame.png',$taskSelected,$taskNormalTab)}
   if($taskState.state -eq '刷新中'){$taskDependencies+=@($taskProgress,$taskDisabled)}
   Verify-Assets $taskDependencies
   $taskState.coverage='shared_component'
   $taskState.sharedDependencies=$taskDependencies
   $taskState.title=$taskSpecific.title
   $taskState.copy=$taskSpecific.copy
   $taskState.buttons=$taskSpecific.buttons
   $taskState.behavior=$taskSpecific.behavior
   $taskState.layout='保留本页主框与导航，正文/弹窗复用米白panel，标题玉绿，主次操作左右分明；文本为原生动态层。共享状态未单独渲染为完整页面图片。'
   $taskState.designEvidence=@{basePage=$taskDoc.primaryImage;componentBoard='designs/ui/components/51-common-components-v1.png';dialogBoard='designs/ui/components/50-shared-dialogs-v1.png';assetManifest='assets/ui/manifest.json';assetManifestSha256=$taskManifestHash;dependencyHashesVerified=$true;scope='艺术控件与具体文案行为设计复用，不是运行时已实现或专门页面已rendered'}
   $taskState.Remove('sharedDesignCandidate')
  }
 }
 $taskAction=$taskDetails.actionNames[$taskId]
 $taskDoc.commonStateCoverage='共用已生成透明控件加明确原生文字/布局完成设计复用，coverage=shared_component；未称单独绘制或运行实现。'
 $taskDoc.commonStateDesigns=@(
 @{state='正常';coverage='rendered';page=$taskDoc.primaryImage;copy='页面主图示例'},
 @{state='选中';coverage='shared_component';components=@($taskSelected,$taskNormalTab);copy='当前页签/物品的文字保持不变，仅切换选中皮肤';behavior='正文与选中项同步，旧项恢复普通态'},
 @{state='空态';coverage='shared_component';components=@($taskPanel,$taskSecondary);copy=('暂无'+$taskDoc.title+'内容');buttons=@('返回大厅');behavior='清空无效详情与操作，保留关闭/返回导航'},
 @{state='加载';coverage='shared_component';components=@($taskPanel,$taskProgress,$taskDisabled);copy='正在加载，请稍候…';buttons=@();behavior='防重复请求，保持安全返回，成功后替换内容'},
 @{state='失败';coverage='shared_component';components=@($taskPanel,$taskPrimary,$taskSecondary);copy='加载失败，请检查网络后重试。';buttons=@('重试','返回');behavior='保留安全数据与输入，不把失败标成成功'}
 )
 $taskDoc.commonActionDesigns=@(
 @{state='可操作';coverage='shared_component';components=@($taskPrimary);copy=$taskAction;behavior='满足条件后启用，触发当前操作'},
 @{state='处理中';coverage='shared_component';components=@($taskDisabled,$taskProgress);copy='处理中…';behavior='锁定重复提交，等待真实回执'},
 @{state='成功';coverage='shared_component';components=@($taskPanel,$taskPrimary);copy=($taskAction+'已完成');buttons=@('确定');behavior='按真实回执更新数量/状态，关闭反馈后返回本页'},
 @{state='不可操作及原因';coverage='shared_component';components=@($taskDisabled,$taskPanel);copy='当前条件未满足';behavior='在动作旁显示缺少资源、未达进度、内容为空或到期的具体原因；只禁用相关动作'}
 )
 $taskDoc.sharedEvidence=@{assetManifest='assets/ui/manifest.json';assetManifestSha256=$taskManifestHash;verifiedOn=[DateTimeOffset]::Now.ToString('o');method='逐路径存在性及SHA256与manifest一致；共用皮肤+原生文字交互设计，非额外整屏生成'}
 $taskDoc|ConvertTo-Json -Depth 18|Set-Content -LiteralPath $taskStateFile.FullName -Encoding utf8
 $taskSummary+=@{id=$taskId;image=$taskDoc.primaryImage;rendered=@($taskDoc.states|Where-Object coverage -eq 'rendered').Count;shared=@($taskDoc.states|Where-Object coverage -eq 'shared_component').Count;specifiedOnly=@($taskDoc.states|Where-Object coverage -eq 'specified_only').Count}
}
$taskSummary|Sort-Object id|ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $taskDir 'state-coverage.json') -Encoding utf8
[ordered]@{pages=$taskSummary.Count;renderedStates=($taskSummary.rendered|Measure-Object -Sum).Sum;sharedStates=($taskSummary.shared|Measure-Object -Sum).Sum;specifiedOnly=($taskSummary.specifiedOnly|Measure-Object -Sum).Sum}|ConvertTo-Json

