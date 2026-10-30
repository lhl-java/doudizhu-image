param([Parameter(Mandatory=$true)][string]$LayoutPath)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$taskRoot = 'D:\work\doudizhu-image'
$taskLayout = Get-Content -LiteralPath $LayoutPath -Raw | ConvertFrom-Json
$taskSourcePath = Join-Path $taskRoot $taskLayout.source
$taskSource = [System.Drawing.Bitmap]::FromFile($taskSourcePath)
$taskCanvas = New-Object System.Drawing.Bitmap($taskSource.Width,$taskSource.Height,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$taskGraphics = [System.Drawing.Graphics]::FromImage($taskCanvas)
$taskGraphics.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceOver
$taskGraphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$taskGraphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
$taskGraphics.DrawImageUnscaled($taskSource,0,0)
$taskSources = [System.Collections.Generic.List[object]]::new()
$taskSources.Add([ordered]@{ file=$taskLayout.source; sha256=(Get-FileHash -LiteralPath $taskSourcePath -Algorithm SHA256).Hash.ToLower(); record=($taskLayout.source -replace '\.png$','.generation.json'); role='原生生成整屏底图，不放大' })
function Draw-TaskNineSlice([System.Drawing.Graphics]$TargetGraphics,[System.Drawing.Image]$Sprite,[int[]]$SourceRect,[int[]]$DestRect,[int]$Border) {
  $taskSX=@($SourceRect[0],($SourceRect[0]+$Border),($SourceRect[0]+$SourceRect[2]-$Border))
  $taskSY=@($SourceRect[1],($SourceRect[1]+$Border),($SourceRect[1]+$SourceRect[3]-$Border))
  $taskSW=@($Border,($SourceRect[2]-2*$Border),$Border)
  $taskSH=@($Border,($SourceRect[3]-2*$Border),$Border)
  $taskDX=@($DestRect[0],($DestRect[0]+$Border),($DestRect[0]+$DestRect[2]-$Border))
  $taskDY=@($DestRect[1],($DestRect[1]+$Border),($DestRect[1]+$DestRect[3]-$Border))
  $taskDW=@($Border,($DestRect[2]-2*$Border),$Border)
  $taskDH=@($Border,($DestRect[3]-2*$Border),$Border)
  for($taskRow=0;$taskRow -lt 3;$taskRow++) { for($taskCol=0;$taskCol -lt 3;$taskCol++) {
    $taskFrom=[System.Drawing.Rectangle]::new($taskSX[$taskCol],$taskSY[$taskRow],$taskSW[$taskCol],$taskSH[$taskRow])
    $taskTo=[System.Drawing.Rectangle]::new($taskDX[$taskCol],$taskDY[$taskRow],$taskDW[$taskCol],$taskDH[$taskRow])
    $TargetGraphics.DrawImage($Sprite,$taskTo,$taskFrom,[System.Drawing.GraphicsUnit]::Pixel)
  } }
}
try {
  $taskAllTrays=@()
  if($taskLayout.tray) {$taskAllTrays+=@($taskLayout.tray)}
  if($taskLayout.trays) {$taskAllTrays+=@($taskLayout.trays)}
  foreach($taskTray in $taskAllTrays) {
    $taskPanelFile='assets/ui/controls/panel.png'
    $taskPanel=[System.Drawing.Image]::FromFile((Join-Path $taskRoot $taskPanelFile))
    try {
      if($taskTray.fillRect) { $taskGraphics.DrawImage($taskPanel,[System.Drawing.Rectangle]::new([int]$taskTray.fillRect[0],[int]$taskTray.fillRect[1],[int]$taskTray.fillRect[2],[int]$taskTray.fillRect[3]),200,70,180,130,[System.Drawing.GraphicsUnit]::Pixel) }
      Draw-TaskNineSlice $taskGraphics $taskPanel ([int[]]$taskTray.sourceRect) ([int[]]$taskTray.rect) ([int]$taskTray.border)
    } finally { $taskPanel.Dispose() }
    $taskSources.Add([ordered]@{file=$taskPanelFile;sha256=(Get-FileHash -LiteralPath (Join-Path $taskRoot $taskPanelFile) -Algorithm SHA256).Hash.ToLower();record='assets/ui/controls/panel.derivation.json';role='手牌托盘，原生框角九宫格排版，不新增绘画细节'})
  }
  foreach($taskElement in $taskLayout.elements) {
    $taskSpritePath=Join-Path $taskRoot $taskElement.file
    $taskSprite=[System.Drawing.Image]::FromFile($taskSpritePath)
    try { $taskGraphics.DrawImage($taskSprite,[System.Drawing.Rectangle]::new([int]$taskElement.rect[0],[int]$taskElement.rect[1],[int]$taskElement.rect[2],[int]$taskElement.rect[3]),0,0,$taskSprite.Width,$taskSprite.Height,[System.Drawing.GraphicsUnit]::Pixel) } finally {$taskSprite.Dispose()}
    $taskSources.Add([ordered]@{file=$taskElement.file;sha256=(Get-FileHash -LiteralPath $taskSpritePath -Algorithm SHA256).Hash.ToLower();record=($taskElement.file -replace '\.png$','.derivation.json');role=$taskElement.role})
  }
  foreach($taskGroup in $taskLayout.cardGroups) {
    $taskCount=$taskGroup.cards.Count
    $taskHeight=[int]$taskGroup.rect[3]
    $taskWidth=[int][Math]::Round($taskHeight * 216.0/282.0)
    $taskStep=if($taskCount -gt 1) {($taskGroup.rect[2]-$taskWidth)/($taskCount-1)} else {0}
    for($taskIndex=0;$taskIndex -lt $taskCount;$taskIndex++) {
      $taskCardFile='assets/ui/cards/'+$taskGroup.cards[$taskIndex]+'.png'
      $taskCard=[System.Drawing.Image]::FromFile((Join-Path $taskRoot $taskCardFile))
      $taskX=[int][Math]::Round($taskGroup.rect[0]+$taskIndex*$taskStep)
      $taskY=[int]$taskGroup.rect[1]
      if($taskGroup.selectedIndexes -contains $taskIndex) {$taskY-=[int]$taskGroup.selectionLift}
      if(($taskGroup.selectedIndexes -contains $taskIndex) -and $taskGroup.selectionAsset) {
        $taskSelection=[System.Drawing.Image]::FromFile((Join-Path $taskRoot $taskGroup.selectionAsset))
        try {$taskGraphics.DrawImage($taskSelection,[System.Drawing.Rectangle]::new(($taskX-5),($taskY-5),($taskWidth+10),($taskHeight+10)),0,0,$taskSelection.Width,$taskSelection.Height,[System.Drawing.GraphicsUnit]::Pixel)}finally{$taskSelection.Dispose()}
        $taskSources.Add([ordered]@{file=$taskGroup.selectionAsset;sha256=(Get-FileHash -LiteralPath (Join-Path $taskRoot $taskGroup.selectionAsset) -Algorithm SHA256).Hash.ToLower();record=($taskGroup.selectionAsset -replace '\.png$','.derivation.json');role='原生生成的玉绿选中框，缩小排版'})
      }
      try { $taskGraphics.DrawImage($taskCard,[System.Drawing.Rectangle]::new($taskX,$taskY,$taskWidth,$taskHeight),0,0,$taskCard.Width,$taskCard.Height,[System.Drawing.GraphicsUnit]::Pixel) } finally {$taskCard.Dispose()}
      $taskSources.Add([ordered]@{file=$taskCardFile;sha256=(Get-FileHash -LiteralPath (Join-Path $taskRoot $taskCardFile) -Algorithm SHA256).Hash.ToLower();record=($taskCardFile -replace '\.png$','.derivation.json');role='正确点数和花色的独立动态牌面层，缩小排版，不新增原生细节'})
    }
  }
  foreach($taskText in $taskLayout.textOverlays) {
    $taskTextRect=[System.Drawing.RectangleF]::new([single]$taskText.rect[0],[single]$taskText.rect[1],[single]$taskText.rect[2],[single]$taskText.rect[3])
    if($taskText.backgroundColor -or $taskText.backgroundSamplePixel) {
      $taskFillColor=if($taskText.backgroundSamplePixel){$taskSource.GetPixel([int]$taskText.backgroundSamplePixel[0],[int]$taskText.backgroundSamplePixel[1])}else{[System.Drawing.ColorTranslator]::FromHtml($taskText.backgroundColor)}
      $taskFillBrush=[System.Drawing.SolidBrush]::new($taskFillColor)
      try {$taskGraphics.FillRectangle($taskFillBrush,$taskTextRect)}finally{$taskFillBrush.Dispose()}
    }
    $taskFontFamily=if($taskText.font){$taskText.font}else{'Microsoft YaHei'}
    $taskFont=[System.Drawing.Font]::new($taskFontFamily,[single]$taskText.size,[System.Drawing.FontStyle]::Regular,[System.Drawing.GraphicsUnit]::Pixel)
    $taskInk=[System.Drawing.SolidBrush]::new([System.Drawing.ColorTranslator]::FromHtml($taskText.color))
    $taskStringFormat=[System.Drawing.StringFormat]::new()
    $taskStringFormat.Alignment=[System.Drawing.StringAlignment]::Center
    $taskStringFormat.LineAlignment=[System.Drawing.StringAlignment]::Center
    try {$taskGraphics.TextRenderingHint=[System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit;$taskGraphics.DrawString($taskText.text,$taskFont,$taskInk,$taskTextRect,$taskStringFormat)}finally{$taskStringFormat.Dispose();$taskInk.Dispose();$taskFont.Dispose()}
  }
  $taskOutput=Join-Path $taskRoot $taskLayout.output
  $taskCanvas.Save($taskOutput,[System.Drawing.Imaging.ImageFormat]::Png)
  $taskRecord=[ordered]@{
    schemaVersion=1;file=$taskLayout.output;sha256=(Get-FileHash -LiteralPath $taskOutput -Algorithm SHA256).Hash.ToLower()
    generatedAt=[DateTimeOffset]::UtcNow.ToString('o');timestampMeaning='UI组合导出时间，不是新模型生成时间'
    width=$taskCanvas.Width;height=$taskCanvas.Height;format='PNG';tool='System.Drawing native UI composition';route='derived'
    operation='layered-ui-composition: original native artwork + generated panel/identity skins + deterministic card components and native dynamic text, only when specified in layout'
    nativeArtworkResolution=@{width=$taskSource.Width;height=$taskSource.Height};exportResolution=@{width=$taskCanvas.Width;height=$taskCanvas.Height}
    actualModel=$null;actualQuality=$null;submittedParameters=@{model=$null;quality=$null}
    unverifiedReason='本图为UI素材组合导出，未再次调用生成模型；每个生成源的实际型号质量跟随derivedFrom记录，未披露仍为null'
    derivedFrom=@($taskSources);layout=($LayoutPath.Replace($taskRoot+'\','').Replace('\','/'));cardGroups=$taskLayout.cardGroups;textOverlays=$taskLayout.textOverlays
    visualReview=@{status='pending_visual_review';note='待检查组合导出，不能将原稿待修问题自动视为通过'}
  }
  $taskRecord | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath ($taskOutput -replace '\.png$','.generation.json') -Encoding utf8
  [ordered]@{file=$taskLayout.output;width=$taskCanvas.Width;height=$taskCanvas.Height;groups=@($taskLayout.cardGroups | ForEach-Object { @{role=$_.role;count=$_.cards.Count} })} | ConvertTo-Json -Depth 5
} finally { $taskGraphics.Dispose();$taskCanvas.Dispose();$taskSource.Dispose() }

