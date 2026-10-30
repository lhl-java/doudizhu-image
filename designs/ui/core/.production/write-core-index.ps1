# Build core-only summaries after all page QA writers have finished.
[CmdletBinding()]
param()
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../../..'))
$coreDir=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
if ($coreDir -ne [IO.Path]::GetFullPath((Join-Path $root 'designs/ui/core'))) { throw 'Unexpected script location.' }
$now=[DateTimeOffset]::UtcNow.ToString('o')
function Full-Path([string]$path) {
    $full=[IO.Path]::GetFullPath((Join-Path $root $path))
    if (-not $full.StartsWith($root+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) {throw "Path escapes project: $path"}
    return $full
}
function Read-Json([string]$path) {
    $full=Full-Path $path
    if (!(Test-Path -LiteralPath $full -PathType Leaf)) {throw "Missing: $path"}
    return Get-Content -LiteralPath $full -Raw | ConvertFrom-Json -AsHashtable
}
function Hash([string]$path) { return (Get-FileHash -LiteralPath (Full-Path $path) -Algorithm SHA256).Hash.ToLowerInvariant() }
function Link([string]$path) { return [IO.Path]::GetRelativePath($coreDir,(Full-Path $path)).Replace('\','/') }
function Cell([string]$text) { return $text.Replace('|','\|').Replace([string][char]13,' ').Replace([string][char]10,' ') }
function Png-Size([string]$path) {
    $stream=[IO.File]::OpenRead((Full-Path $path))
    try {
        $bytes=[byte[]]::new(24)
        if($stream.Read($bytes,0,24)-ne 24){throw "PNG header too short: $path"}
        if([BitConverter]::ToString($bytes,0,8)-ne '89-50-4E-47-0D-0A-1A-0A'){throw "Not PNG: $path"}
        $w=[byte[]]$bytes[16..19];[Array]::Reverse($w)
        $h=[byte[]]$bytes[20..23];[Array]::Reverse($h)
        return [ordered]@{width=[BitConverter]::ToUInt32($w,0);height=[BitConverter]::ToUInt32($h,0)}
    } finally {$stream.Dispose()}
}
function Check-Dependency($dep,[string]$owner) {
    if (!$dep.output) {throw "No dependency output: $owner"}
    $actual=Hash $dep.output
    if (!$dep.sha256 -or $actual-ne $dep.sha256) {throw "Dependency hash mismatch: $owner / $($dep.output)"}
    if ($dep.verifiedFiles-ne $true) {throw "Unverified dependency: $owner / $($dep.output)"}
    $recordPath=if($dep.generation){$dep.generation}elseif($dep.derivation){$dep.derivation}else{$null}
    if($recordPath){$record=Read-Json $recordPath;if($record.sha256-ne $actual){throw "Dependency record mismatch: $owner"}}
}
$scope=Read-Json 'docs/UI_SCOPE.json'
$pages=@($scope.pages|Where-Object{$_.batch-eq 'core'}|Sort-Object{$_.id})
$expectedIds=@('01-launch-login','02-lobby','03-classic-select','04-stakes-select','05-matchmaking','06-friend-room-entry','07-create-room','08-join-room','09-room-waiting','10-invite-friends','56-offline','57-hero-skills','58-season-shop')
if($pages.Count-ne 13 -or (@($pages.id)-join ',')-ne ($expectedIds-join ',')){throw 'Assigned core IDs differ from 13-page contract.'}
$entries=[Collections.Generic.List[object]]::new()
$stateEntries=[Collections.Generic.List[object]]::new()
$extras=[Collections.Generic.List[object]]::new()
$counts=[ordered]@{requiredTotal=0;rendered=0;shared_component=0;specified_only=0}
foreach($page in $pages){
    $g=Read-Json $page.generation
    $s=Read-Json $page.stateSpec
    $pngHash=Hash $page.output
    $size=Png-Size $page.output
    if($g.file-ne $page.output -or $g.sha256-ne $pngHash){throw "PNG/record mismatch: $($page.id)"}
    if($g.width-ne $size.width -or $g.height-ne $size.height){throw "Native size mismatch: $($page.id)"}
    if($null-ne $g.actualModel -or $null-ne $g.actualQuality -or $null-ne $g.submittedParameters.model -or $null-ne $g.submittedParameters.quality){throw "Unknown model/quality changed: $($page.id)"}
    if($g.status-ne 'design_ready_user_review' -or $s.status-ne 'design_ready_user_review'){throw "Page QA not ready: $($page.id)"}
    if($g.userApproval-ne $false -or $s.userApproval-ne $false){throw "Unexpected approval: $($page.id)"}
    if(!$g.visualQA.inspectedAt -or !$s.visualQA.inspectedAt){throw "Missing visual inspection: $($page.id)"}
    if((Hash $g.prompt)-ne $g.promptSha256){throw "Prompt mismatch: $($page.id)"}
    if((Hash $g.evidence.receipt)-ne $g.evidence.receiptSha256){throw "Receipt mismatch: $($page.id)"}
    if((@($page.requiredStates)-join '|')-ne (@($s.requiredStates)-join '|')){throw "requiredStates mismatch: $($page.id)"}
    if($s.states.Count-ne $page.requiredStates.Count){throw "State count mismatch: $($page.id)"}
    $pc=[ordered]@{requiredTotal=$page.requiredStates.Count;rendered=0;shared_component=0;specified_only=0}
    foreach($name in $page.requiredStates){
        $matches=@($s.states|Where-Object{$_.name-eq $name})
        if($matches.Count-ne 1){throw "Missing/duplicate state: $($page.id) / $name"}
        $st=$matches[0]
        if($st.coverage-notin @('rendered','shared_component','specified_only')){throw "Unknown coverage: $($page.id) / $name"}
        if($st.status-ne 'design_ready_user_review'){throw "State not ready: $($page.id) / $name"}
        if($st.coverage-eq 'rendered'){
            if(!$st.image){throw "Rendered without image: $($page.id) / $name"}
            if(!$st.evidence -or $st.evidence.imageSha256-ne (Hash $st.image)){throw "Rendered evidence mismatch: $($page.id) / $name"}
        }
        if($st.coverage-eq 'shared_component'){
            if(@($st.dependencies).Count-eq 0){throw "Shared without dependency: $($page.id) / $name"}
            if(@($st.copy).Count-eq 0 -or @($st.behavior).Count-eq 0){throw "Shared lacks copy/behavior: $($page.id) / $name"}
            foreach($dep in $st.dependencies){Check-Dependency $dep "$($page.id) / $name"}
        }
        $pc[$st.coverage]++;$counts[$st.coverage]++;$counts.requiredTotal++
        $stateEntries.Add([ordered]@{
            pageId=$page.id;title=$page.title;state=$name;coverage=$st.coverage;status=$st.status
            image=$st.image;stateSpec=$page.stateSpec;copy=$st.copy;behavior=$st.behavior
            disabledReasons=$st.disabledReasons;dependencies=$st.dependencies;evidence=$st.evidence
            visibleInMainImage=($st.coverage-eq 'rendered');implementationStatus='specified_only_not_implemented'
        })
    }
    foreach($extra in $s.supplementalStates){$extras.Add([ordered]@{pageId=$page.id;name=$extra.name;coverage=$extra.coverage;status=$extra.status})}
    $entries.Add([ordered]@{
        pageId=$page.id;title=$page.title;output=$page.output;sha256=$pngHash
        generation=$page.generation;generationSha256=(Hash $page.generation)
        stateSpec=$page.stateSpec;stateSpecSha256=(Hash $page.stateSpec)
        prompt=$g.prompt;promptSha256=$g.promptSha256
        nativeResolution=$size;exportResolution=$g.exportResolution;requestedResolution=$g.requestedResolution
        status=$g.status;visualQA=$g.visualQA;userApproval=$false
        actualModel=$g.actualModel;actualQuality=$g.actualQuality;coverage=$pc
    })
}
if($counts.requiredTotal-ne 44){throw "Expected 44 required states, found $($counts.requiredTotal)."}
if($counts.specified_only-gt 0){throw "Required states still specified_only: $($counts.specified_only)."}
$coverage=[ordered]@{
    schemaVersion=1;batch='core';updatedAt=$now;scopeSource='docs/UI_SCOPE.json';scopeSha256=(Hash 'docs/UI_SCOPE.json')
    counts=$counts;requiredStateDesignCoverageComplete=$true
    semantics=[ordered]@{
        rendered='该必要状态已在完整主图可见；多个状态可同屏，不表示每态一张独立PNG。'
        shared_component='实际核验既有图板/控件/牌桌及哈希，写明原生文案、按钮、行为、禁用原因；没有另画该整屏状态，没有实现客户端。'
        specified_only='仅说明，不能计为完成视觉设计覆盖。'
    }
    offline56=[ordered]@{
        mainImage='designs/ui/core/56-offline-v1.png'
        independentlyRenderedRequiredStates=@('可开始')
        noIndependentPngFor=@('进行中','暂停','结束')
        reuse=@('designs/ui/table/14-play-turn-v2.png','designs/ui/components/50-shared-dialogs-v1.png','designs/ui/components/51-common-components-v1.png','designs/ui/components/52-card-and-effects-v1.png')
        specification='designs/ui/core/56-offline.states.json'
    }
    states=@($stateEntries.ToArray())
    supplementalStates=[ordered]@{includedInRequiredCount=$false;note='补充规格单列，不增加或替代scope的44个必要状态，不把纯实现说明算作成图。';items=@($extras.ToArray())}
}
$result=[ordered]@{
    schemaVersion=1;batch='core';updatedAt=$now
    scope=[ordered]@{source='docs/UI_SCOPE.json';sha256=(Hash 'docs/UI_SCOPE.json');assignedPages=$pages.Count;wholeProjectPages=$scope.pages.Count;pageIds=@($pages.id)}
    status='design_ready_user_review';userApproval=$false
    mainImages=[ordered]@{required=$pages.Count;present=$entries.Count;visuallyReviewed=$entries.Count;nativePngs=$entries.Count}
    necessaryStateCoverage=$counts;stateCoverageFile='designs/ui/core/state-coverage.json'
    delivery='本批13张独立核心主页面、逐图来源记录、提示词与44必要状态设计覆盖；只报告core，不代表全项目60项或客户端全部完成。'
    actualModel=$null;actualQuality=$null
    modelEvidence='宿主管理，工具未披露实际模型/质量；generation内配置为用户目标，不作为实际运行证明。'
    nativeOutputPolicy='按PNG原生尺寸和逐图记录核对；导出为字节一致复制，未放大冒充原生。'
    boundaries=@('所有页面待用户评审，设计QA不是用户批准。','共享状态不是另画的整屏PNG。','客户端/服务器/真实登录/社交发送/支付/兑换接入不在本批美术声明内。','原image项目只读；本脚本不操作Git、上传或根索引。')
    validation=[ordered]@{status='passed';provenanceAudit='designs/ui/core/validation.json';checks=@('13个scope core IDs与文件齐全','PNG哈希/真实原生尺寸匹配generation','prompt与receipt哈希匹配','44必要状态逐字对齐scope，无重复遗漏','共享依赖实际文件哈希及来源记录匹配','QA和用户未批准状态一致','实际型号与质量未知字段保留')}
    pages=@($entries.ToArray())
}
$md=[Collections.Generic.List[string]]::new()
$md.Add('# 核心界面批次交付索引')
$md.Add('')
$md.Add("核验时间：$now。本批覆盖全量 $($scope.pages.Count) 项中的 **$($pages.Count) 个核心主界面**（01–10、56–58）；范围见 [UI_SCOPE.json](../../../docs/UI_SCOPE.json)，只报告 core 批次。")
$md.Add('')
$md.Add("独立主图 **$($entries.Count)/$($pages.Count)**，逐图记录、提示词和实际视觉检查齐全。必要状态 **$($counts.requiredTotal)/$($counts.requiredTotal)** 已有设计覆盖：实绘 rendered **$($counts.rendered)**，共享组件 shared_component **$($counts.shared_component)**，仅规格 specified_only **$($counts.specified_only)**。")
$md.Add('')
$md.Add('shared_component 指已核验既有图板、控件或牌桌，并定义具体原生文案、按钮、行为和禁用原因；它不是另外绘制的状态整屏，也不是已接入的客户端。多个 rendered 状态可同时出现在同一张主图。')
$md.Add('')
$md.Add('所有页面均为 design_ready_user_review，userApproval=false。设计复核通过，不代表用户已批准。数值、昵称、技能和期限为本项目设计示意，未声称逐屏实测腾讯当前客户端。')
$md.Add('')
$md.Add('提示词画布目标为 2560×1080；下表按 PNG 头实测原生尺寸，未用放大替代原生细节。使用宿主内置 image_gen；实际型号和质量未披露，记录保留 null。配置中的 GPT Image 2.5 Sunburst / max 仅为用户目标。')
$md.Add('')
$md.Add('| 页面 | 主图 | 原生尺寸 | 生成记录 | 状态规格 | 提示词 | QA | R/S/O |')
$md.Add('|---|---|---|---|---|---|---|---|')
foreach($e in $entries){
    $md.Add("| $($e.pageId) · $(Cell $e.title) | [PNG]($(Link $e.output)) | $($e.nativeResolution.width)×$($e.nativeResolution.height) | [generation]($(Link $e.generation)) | [states]($(Link $e.stateSpec)) | [prompt]($(Link $e.prompt)) | $(Cell $e.visualQA.status) | $($e.coverage.rendered)/$($e.coverage.shared_component)/$($e.coverage.specified_only) |")
}
$md.Add('')
$md.Add('R/S/O = rendered / shared_component / specified_only。')
$md.Add('')
$md.Add('## 状态复用与交付边界')
$md.Add('')
$md.Add('56 单机练习主图只实绘可开始的难度选择页。进行中、暂停、结束没有独立 PNG：进行中复用 [14 三人牌桌](../table/14-play-turn-v2.png) 与 [52 牌面](../components/52-card-and-effects-v1.png)，暂停与结束复用 [50 通用弹窗](../components/50-shared-dialogs-v1.png)、[51 通用组件](../components/51-common-components-v1.png)及其透明切片。离线标题、电脑身份、暂停、再练一局与不结算金豆等原生文案及行为见 [56 状态规格](56-offline.states.json)。')
$md.Add('')
$md.Add('58 的可兑、不足、已兑在主图同屏可见；到期复用公共空态、禁用按钮及原生到期说明，没有另画到期整屏。其他共享状态的逐项来源、区域、哈希和文案见各页 states 或 [状态覆盖汇总](state-coverage.json)。')
$md.Add('')
$md.Add('页面静态图和状态规范不等于可运行界面。客户端、服务器、真实认证、社交发送、支付、兑换与动态动画接入均不在本批美术完成声明内。supplementalStates 为额外交互规格，单独列于汇总，不计入 44 个必要状态。')
$md.Add('')
$md.Add('## 可追溯汇总')
$md.Add('')
$md.Add('- [batch-result.json](batch-result.json)：13 页文件、哈希、尺寸、QA与范围统计。')
$md.Add('- [state-coverage.json](state-coverage.json)：44 个必要状态的实际覆盖与共享依赖，补充规格单列。')
$md.Add('- [validation.json](validation.json)：13张PNG与宿主源图、提示词、回执、四张实际参考图的独立哈希核验。')
$md.Add('- [索引生成脚本](.production/write-core-index.ps1)：从现存 scope、PNG、generation、states 和 prompt 重建本批汇总，只写 core 目录。')
$md.Add('- [初版大厅支持参考](../lobby-ui-v1.png)与[三人角色稿](../../characters/characters-trio-v1.png)继续保留；本批全功能大厅为02独立新图。')
$md.Add('')
$md.Add('本次脚本核验真实文件、原生尺寸、PNG/提示词/回执哈希、必要状态名与共享依赖哈希。图像内容的实际视觉核验记录保存在各 generation 和 states，不由脚本推断。')
$markdown=$md -join [Environment]::NewLine
foreach($match in [regex]::Matches($markdown,'\]\(([^)]+)\)')){
    $target=$match.Groups[1].Value
    if($target-match '^[a-z]+://'){continue}
    if($target-in @('batch-result.json','state-coverage.json')){continue}
    $full=[IO.Path]::GetFullPath((Join-Path $coreDir $target))
    if(!(Test-Path -LiteralPath $full -PathType Leaf)){throw "README link missing: $target"}
}
# Mutations are limited to these three core batch files.
$coverage|ConvertTo-Json -Depth 70|Set-Content -LiteralPath (Join-Path $coreDir 'state-coverage.json') -Encoding utf8
$result|ConvertTo-Json -Depth 70|Set-Content -LiteralPath (Join-Path $coreDir 'batch-result.json') -Encoding utf8
$markdown|Set-Content -LiteralPath (Join-Path $coreDir 'README.md') -Encoding utf8
[pscustomobject]@{batch='core';pages=$entries.Count;requiredStates=$counts.requiredTotal;rendered=$counts.rendered;shared_component=$counts.shared_component;specified_only=$counts.specified_only;status=$result.status;updatedAt=$now}

