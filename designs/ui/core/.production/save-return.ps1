param([Parameter(Mandatory=$true)][ValidatePattern('^([0-9]{2})-[a-z-]+$')][string]$Id)
$ErrorActionPreference = 'Stop'
$projectRoot = 'D:\work\doudizhu-image'
$coreDirectory = 'D:\work\doudizhu-image\designs\ui\core'
$receiptPath = Join-Path $coreDirectory ('.production\receipts\' + $Id + '-v1.receipt.json')
$receipt = Get-Content -LiteralPath $receiptPath -Raw -Encoding UTF8 | ConvertFrom-Json
$imagePath = Join-Path $coreDirectory ($Id + '-v1.png')
$promptPath = Join-Path $projectRoot ('prompts\core\' + $Id + '-v1.txt')
if (Test-Path -LiteralPath $imagePath) { throw 'Image target exists; use new version for retry.' }
Copy-Item -LiteralPath $receipt.hostOutputFile -Destination $imagePath
$started = ([string]$receipt.startedAtUtc).Replace(' UTC','Z').Replace(' ','T')
$finished = ([string]$receipt.receivedAtUtc).Replace(' UTC','Z').Replace(' ','T')
& 'D:\work\doudizhu-image\designs\ui\core\.production\record-generation.ps1' -ImagePath $imagePath -PromptPath $promptPath -ReceiptPath $receiptPath -RequestedWidth 2560 -RequestedHeight 1080 -StartedAtUtc $started -FinishedAtUtc $finished
$recordPath = Join-Path $coreDirectory ($Id + '-v1.generation.json')
$record = Get-Content -LiteralPath $recordPath -Raw -Encoding UTF8 | ConvertFrom-Json
$record | Add-Member -NotePropertyName pageId -NotePropertyValue $Id
$record | Add-Member -NotePropertyName userApproval -NotePropertyValue $false
$record.status = 'pending_visual_review'
$record | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $recordPath -Encoding UTF8

