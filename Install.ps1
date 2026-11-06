[CmdletBinding()]
param([string]$SettingsPath=(Join-Path $PSScriptRoot 'settings.local.json'),[switch]$UseSettings,[switch]$PlanOnly)
$ErrorActionPreference='Stop'
Set-Location -LiteralPath $PSScriptRoot
$SettingsPath=$ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($SettingsPath)
function Ask($label,$default){$v=Read-Host "$label [$default]";if([string]::IsNullOrWhiteSpace($v)){return $default};return $v.Trim().Trim('"')}
function Yes($label,$default){$d=if($default){'Y'}else{'N'};while($true){$v=Ask "$label (Y/N)" $d;if($v -match '^[Yy]$'){return $true};if($v -match '^[Nn]$'){return $false};Write-Host 'Y 또는 N 입력'}}
if(!$UseSettings){
 $s=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'settings.example.json') -Raw|ConvertFrom-Json
 if(Test-Path -LiteralPath $SettingsPath){$s=Get-Content -LiteralPath $SettingsPath -Raw|ConvertFrom-Json}
 Write-Host '경로는 이 설정 파일이 있는 폴더를 기준으로 해석합니다. 기본값이 맞으면 Enter를 누르세요.'
 $s.python_exe=Ask '준비한 Python 실행 파일' $s.python_exe
 $s.cuda_dir=Ask 'CUDA DLL 폴더' $s.cuda_dir
 $s.install_root=Ask '설치 폴더' './runtime'
 $base=Ask '다운로드한 파일 폴더' '../strata-assets'
 foreach($g in @('models','pack','mtp','engine','vision')){$s.paths.$g=Join-Path $base $g}
 if(Test-Path -LiteralPath (Join-Path $base 'prepared.json')){$prepared=Get-Content -LiteralPath (Join-Path $base 'prepared.json') -Raw|ConvertFrom-Json;$s.images=$prepared.images}
 $s.images=Yes '이미지 입력 사용 (CPU)' $s.images
 $ctx=Ask '컨텍스트 64 / 128 / 192 / 256 (검증값 192)' '192';if($ctx -notin @('64','128','192','256')){throw '컨텍스트 선택 오류'};$s.context=[int]$ctx*1024
 $s.lan=Yes '다른 LAN PC에서 접속 허용' $false;$s.advertise_host=''
 if($s.lan){$ip='';try{$ip=(Get-NetIPConfiguration|Where-Object IPv4DefaultGateway|Select-Object -First 1).IPv4Address.IPAddress}catch{};$s.advertise_host=Ask '서버의 실제 LAN IP 또는 호스트명' $ip}
 $s.port=[int](Ask '포트' '8188');$s.copy_assets=$false
 $s.merge_opencode=Yes '이 PC의 OpenCode 설정에 자동 병합 (MCP 보존·백업)' $true
 $s.shortcuts=Yes '바탕화면 시작·중지 바로가기 생성' $true
 $s.startup=Yes '로그인 시 자동 시작' $false
 [IO.File]::WriteAllText($SettingsPath,($s|ConvertTo-Json -Depth 12),[Text.UTF8Encoding]::new($false))
}
$s=Get-Content -LiteralPath $SettingsPath -Raw|ConvertFrom-Json
$py=$s.python_exe;if(![IO.Path]::IsPathRooted($py)){$py=Join-Path (Split-Path -Parent $SettingsPath) $py}
if(!(Test-Path -LiteralPath $py)){throw 'Python 준비가 필요합니다. README의 1단계를 진행하세요.'}
& $py (Join-Path $PSScriptRoot 'scripts/strata_local.py') plan --settings $SettingsPath
if($LASTEXITCODE -ne 0){throw '파일 준비가 필요합니다. Prepare-Models.cmd를 실행하거나 docs/ASSETS.ko.md를 보세요.'}
if($PlanOnly){return}
if(!(Yes '위 설정으로 설치할까요?' $true)){return}
& $py (Join-Path $PSScriptRoot 'scripts/strata_local.py') install --settings $SettingsPath
if($LASTEXITCODE -ne 0){throw '설치 실패. 위 오류 내용을 확인하세요.'}
$root=$s.install_root;if(![IO.Path]::IsPathRooted($root)){$root=Join-Path (Split-Path -Parent $SettingsPath) $root}
Write-Host "설치 완료. OpenCode JSON: $root\clients"
if(Yes '지금 Strata를 시작할까요?' $true){& (Join-Path $root '.venv/Scripts/python.exe') (Join-Path $root 'manager.py') start --root $root;if($LASTEXITCODE -ne 0){throw '시작 상태와 logs/server.log를 확인하세요.'}}