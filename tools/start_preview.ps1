param([int]$Port = 8771, [ValidateSet('art','design','states')][string]$View = 'art')
$ErrorActionPreference = 'Stop'
$taskRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$taskRuntime = 'C:\Users\luyua\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (-not (Test-Path -LiteralPath $taskRuntime)) { $taskRuntime = (Get-Command python -ErrorAction Stop).Source }
$taskPage = @{ art='runtime/art-preview.html'; design='preview/index.html'; states='preview/states.html' }[$View]
$taskUrl = "http://127.0.0.1:$Port/$taskPage"
$taskExisting = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($taskExisting) {
    $taskResponse = Invoke-WebRequest -Uri $taskUrl -TimeoutSec 5
    if ($taskResponse.Content -notmatch '斗地主') { throw "端口 $Port 已被其他服务使用" }
    Write-Output $taskUrl
    exit 0
}
$taskLogRoot = Join-Path $taskRoot '.work\preview'
New-Item -ItemType Directory -Path $taskLogRoot -Force | Out-Null
$taskProcess = Start-Process -FilePath $taskRuntime -ArgumentList @('-m','http.server',"$Port",'--bind','127.0.0.1','--directory',('"' + $taskRoot + '"')) -WindowStyle Hidden -RedirectStandardOutput (Join-Path $taskLogRoot 'stdout.log') -RedirectStandardError (Join-Path $taskLogRoot 'stderr.log') -PassThru
@{ pid = $taskProcess.Id; url = $taskUrl; root = $taskRoot } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskLogRoot 'server.json') -Encoding utf8
Write-Output $taskUrl
