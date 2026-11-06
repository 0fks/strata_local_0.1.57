[CmdletBinding()]
param([string]$Root,[string]$AssetsPath)
$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
if(!$Root){$Root=Read-Host 'Strata 설치 폴더 [./runtime]';if([string]::IsNullOrWhiteSpace($Root)){$Root='./runtime'}}
$Root=$ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Root.Trim().Trim('"'))
if(!$AssetsPath){$AssetsPath=Read-Host '파일을 옮긴 새 폴더 (예: D:\strata-assets 또는 ../strata-assets)'}
if([string]::IsNullOrWhiteSpace($AssetsPath)){throw '새 폴더를 입력하세요.'}
$AssetsPath=$ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($AssetsPath.Trim().Trim('"'))
$py=Join-Path $Root '.venv/Scripts/python.exe'
if(!(Test-Path -LiteralPath $py)){throw '설치 폴더를 찾을 수 없습니다.'}
Write-Host 'Strata를 먼저 중지하고 파일을 새 위치로 옮겨 두세요. 이 도구는 파일을 이동하지 않고 새 경로를 검사·연결합니다.'
& $py (Join-Path $PSScriptRoot 'scripts/strata_local.py') rebind --root $Root --assets $AssetsPath
if($LASTEXITCODE -ne 0){throw '경로 변경에 실패했습니다. 위 오류를 확인하세요.'}
Write-Host '이제 바탕화면의 Strata Local Start로 다시 시작하세요.'