[CmdletBinding()]
param([string]$Root)
$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
if(!$Root){$Root=Read-Host 'Strata 설치 폴더 [./runtime]';if([string]::IsNullOrWhiteSpace($Root)){$Root='./runtime'}}
$Root=$ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Root.Trim().Trim('"'))
$py=Join-Path $Root '.venv/Scripts/python.exe'
if(!(Test-Path -LiteralPath $py)){throw '해당 설치 폴더의 Python을 찾지 못했습니다. IQ3_XXS라면 ./runtime-IQ3_XXS를 지정하세요.'}
& $py (Join-Path $PSScriptRoot 'scripts/export_opencode_provider.py') --root $Root
if($LASTEXITCODE -ne 0){throw 'provider 복사용 파일 생성 실패. 위 오류를 확인하세요.'}
Write-Host 'clients/Local/provider-entry.txt를 기존 config.json의 provider 안에 붙여넣으세요. LAN용은 clients/LAN에 있습니다.'
