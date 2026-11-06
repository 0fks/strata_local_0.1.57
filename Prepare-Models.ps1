[CmdletBinding()]
param([string]$AssetsPath,[switch]$Probe,[string]$Mirror='https://huggingface.co',[string]$Proxy,[int]$Timeout=25)
$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
if(!$AssetsPath){$AssetsPath=Read-Host '파일을 받을 폴더 [../strata-assets]';if([string]::IsNullOrWhiteSpace($AssetsPath)){$AssetsPath='../strata-assets'}}
$AssetsPath=$ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($AssetsPath)
$root=[IO.Path]::GetFullPath($PSScriptRoot)
if($AssetsPath -eq $root){throw '다운로드용 하위 폴더를 지정하세요. 예: ./assets'}
foreach($n in @('vendor','scripts','docs','tests','manifests','.git','prereqs')){$reserved=Join-Path $root $n;if($AssetsPath -eq $reserved -or $AssetsPath.StartsWith($reserved+'\',[StringComparison]::OrdinalIgnoreCase)){throw '소스 폴더에 다운로드할 수 없습니다.'}}
if(!$Probe){New-Item -ItemType Directory -Path $AssetsPath -Force|Out-Null;[IO.File]::WriteAllText((Join-Path $AssetsPath '.gitignore'),"*`n!.gitignore`n",[Text.UTF8Encoding]::new($false))}

$images=Read-Host '이미지 입력 파일도 받기? (Y/N) [Y]'
if(!$Proxy){$Proxy=Read-Host 'HTTP 프록시 주소 (사용하지 않으면 Enter)'}
Write-Host 'SC117 IQ3_S GGUF 2개를 Hugging Face에서 받습니다. MTP는 ModelScope에서 받습니다.'

if($Probe){$py='py';$prefix=@('-3.11')}else{
 $venv=Join-Path $AssetsPath '.prepare-venv';$py=Join-Path $venv 'Scripts/python.exe'
 if(!(Test-Path -LiteralPath $py)){& py -3.11 -m venv $venv;if($LASTEXITCODE -ne 0){throw 'Python 3.11 x64를 먼저 직접 설치하세요.'}}
 & $py -m pip install -r (Join-Path $PSScriptRoot 'vendor/strata/requirements.txt');if($LASTEXITCODE -ne 0){throw '준비 패키지 설치 실패'};$prefix=@()
}
$call=@($prefix)+@((Join-Path $PSScriptRoot 'scripts/prepare_models.py'),'--assets',$AssetsPath,'--mirror',$Mirror,'--timeout',[string]$Timeout)
if($Proxy){$call+=@('--proxy',$Proxy)}
if($images -match '^[Nn]$'){$call+='--no-images'}
if($Probe){$call+='--probe'}
& $py @call
if($LASTEXITCODE -ne 0){throw '다운로드/준비 실패. 위 오류를 확인하고 같은 폴더로 재실행하세요.'}