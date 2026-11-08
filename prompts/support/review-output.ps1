param([Parameter(Mandatory=$true)][string]$Id,[Parameter(Mandatory=$true)][string]$Notes)
$ErrorActionPreference='Stop'
$taskRoot='D:\work\doudizhu-image'
$taskOut=Join-Path $taskRoot 'designs\ui\support'
$taskChecks=Get-Content -LiteralPath (Join-Path $taskRoot 'prompts\support\support-checks.json') -Raw | ConvertFrom-Json
$taskCheck=$taskChecks|Where-Object id -eq $Id
$taskVersion=if($taskCheck.selectedVersion){$taskCheck.selectedVersion}else{'v1'}
$taskScope=Get-Content -LiteralPath (Join-Path $taskRoot 'docs\UI_SCOPE.json') -Raw|ConvertFrom-Json
$taskPage=$taskScope.pages|Where-Object id -eq $Id
$taskRecordPath=Join-Path $taskOut ($Id+'-'+$taskVersion+'.generation.json')
$taskRecord=Get-Content -LiteralPath $taskRecordPath -Raw|ConvertFrom-Json
$taskRecord.inspection.status='design_ready_user_review'
$taskRecord.inspection.notes=@($Notes)
$taskRecord.inspection|Add-Member -NotePropertyName reviewedAt -NotePropertyValue ([DateTimeOffset]::Now.ToString('o')) -Force
$taskRecord|ConvertTo-Json -Depth 15|Set-Content -LiteralPath $taskRecordPath -Encoding utf8
$taskStates=foreach($taskState in $taskPage.requiredStates){
 $taskRendered=$taskCheck.renderedStates -contains $taskState
 $taskMeaning=switch -Regex($taskState){
  '不足' {'显示缺少的资源及原因，主动作禁用或打开资源补充说明，不误显示成功。';break}
  '结果|保存|已保存|提交结果' {'凭真实操作回执展示结果；成功更新列表/数量/状态，失败保留当前输入并可重试。';break}
  '确认|切换确认' {'显示对象与数量/影响，提供明确确认和取消；取消不改变当前状态。';break}
  '空|未上榜' {'显示空态说明及可用返回/前往入口，不残留上次详情或无效操作。';break}
  '过期|结束' {'标注到期时间与不可操作原因，禁止再次领取或使用。';break}
  '已领|已签|已使用' {'用勾记和文字表达完成态，动作禁用，不能重复领取或使用。';break}
  '未到|未达' {'用锁定/进度明确条件，未达到时奖励动作禁用。';break}
  '可领|可签|可购买|可兑换' {'突出主动作，操作中防重复；以真实回执更新完成态并显示奖励/消耗明细。';break}
  '编辑|自己' {'提供编辑或输入控件，保留取消与保存语义；输入按约束校验，提交前不改变已保存值。';break}
  '他人' {'显示对方公开信息，隐藏编辑自身资料入口，社交动作按关系状态启用。';break}
  '在线|离线' {'以状态圆点和文字共同表达；离线不提供即时加入，邀请状态以回执为准。';break}
  '申请' {'列出申请人和同意/拒绝；处理后更新关系，空申请显示空态。';break}
  '刷新中' {'显示加载反馈并防重复刷新，失败保留已有内容并允许重试。';break}
  '开关' {'使用开/关文字与位置双重反馈；按设置范围即时预览或保存后生效。';break}
  '滑块' {'显示当前百分比并可拖动；支持0到100，保存或取消遵循设置页约定。';break}
  '目录|详情|新手步骤' {'目录选中与正文同步，步骤有前后导航与退出入口；当前页保持可读留白。';break}
  '维护' {'展示服务维护说明和预计恢复信息，登录入口禁用，提供公告或重试。';break}
  '更新' {'展示当前与目标版本、进度、暂停/继续和稍后；必要更新完成后才进入游戏。';break}
  '下载失败' {'保留已下载进度和失败原因，提供重试与取消，不重置成功资源。';break}
  '满级' {'显示满级状态与已获得奖励，隐藏无意义经验升级动作。';break}
  default {'正文、选中项与主动作一致；操作中显示反馈，成功/失败遵循页面流程。'}
 }
 [ordered]@{state=$taskState;coverage=if($taskRendered){'rendered'}else{'specified_only'};renderedIn=if($taskRendered){$taskRecord.file}else{$null};copySource='实际动态文案由产品/服务回执提供，图中数值为设计示意';behavior=$taskMeaning;sharedDesignCandidate=if(-not $taskRendered){@('50-shared-dialogs','51-common-components')}else{@()}}
}
[ordered]@{schemaVersion=1;id=$Id;title=$taskPage.title;primaryImage=$taskRecord.file;status='design_ready_user_review';requiredStates=$taskPage.requiredStates;states=@($taskStates);listCommonStates=@('正常','选中','空态','加载','失败');actionCommonStates=@('可操作','处理中','成功','不可操作及原因');commonStateCoverage='共用图板依赖尚待协调者最终核验，未单独画出的状态仍为specified_only，不以说明冒充图像';dynamicText='昵称、数量、价格、期限、进度、奖励、订单/反馈结果由产品配置与真实回执提供；当前均为示例';implementationBoundary='本文件是视觉与交互规范，不是客户端/服务器/支付/发送功能的完成证明';inspectionNotes=@($Notes)}|ConvertTo-Json -Depth 12|Set-Content -LiteralPath (Join-Path $taskOut ($Id+'.states.json')) -Encoding utf8
$taskRows=@()
foreach($taskItem in $taskChecks){
 $taskItemVersion=if($taskItem.selectedVersion){$taskItem.selectedVersion}else{'v1'}
 $taskGenPath=Join-Path $taskOut ($taskItem.id+'-'+$taskItemVersion+'.generation.json')
 if(Test-Path -LiteralPath $taskGenPath){
  $taskGen=Get-Content -LiteralPath $taskGenPath -Raw|ConvertFrom-Json
  if($taskGen.inspection.status -eq 'design_ready_user_review'){
   $taskRows+=('| '+$taskItem.id+' | '+$taskItem.title+' | ['+$taskItem.id+'-'+$taskItemVersion+'.png]('+$taskItem.id+'-'+$taskItemVersion+'.png) | '+$taskGen.width+'×'+$taskGen.height+' | [记录]('+$taskItem.id+'-'+$taskItemVersion+'.generation.json) · [状态]('+$taskItem.id+'.states.json) | 首版待用户确认 |')
  }
 }
}
$taskReadme=@(
 '# 配套 UI 批次',
 '',
 ('已生成并看图检查 '+$taskRows.Count+' / 15 项。全部使用宿主内置 image_gen，模型与质量目标读取项目配置，实际未披露值记录为 null。'),
 '',
 '| ID | 页面 | 成图 | 原生尺寸 | 来源与状态 | 评审状态 |',
 '|---|---|---|---|---|---|---|'
)+$taskRows+@(
 '',
 '图片为独立完整窗口，未缩放或程序重绘。提示词位于 ../../../prompts/support/，每次实际附带两张主风格参考；涉及角色时附三人设定图。',
 '',
 '每页 states.json 明确 rendered 与 specified_only。未单独生成的空态、失败、维护及结果等状态不冒称已经绘制；共享组件依赖由协调者最终核验映射。视觉自检不是用户批准，也不是客户端与服务器接入验收。'
)
$taskReadme -join [Environment]::NewLine|Set-Content -LiteralPath (Join-Path $taskOut 'README.md') -Encoding utf8
[ordered]@{reviewed=$Id;ready=$taskRows.Count;total=15}|ConvertTo-Json

