[CmdletBinding()]
param([string]$SettingsPath = (Join-Path $PSScriptRoot 'settings.local.json'), [switch]$UseSettings, [switch]$PlanOnly)
$ErrorActionPreference = 'Stop'
function Ask([string]$Label,[string]$Default) { $v=Read-Host "$Label [$Default]"; if([string]::IsNullOrWhiteSpace($v)){return $Default};return $v.Trim().Trim('"') }
function Yes([string]$Label,[bool]$Default) { $d=if($Default){'Y'}else{'N'};while($true){$v=Ask "$Label (Y/N)" $d;if($v -match '^[Yy]$'){return $true};if($v -match '^[Nn]$'){return $false};Write-Host 'Y 또는 N을 입력하세요.'} }
if (!$UseSettings) {
    Write-Host 'Strata Local setup — Python 3.11 x64, CUDA 13 runtime and NVIDIA driver 580.65+ must be installed manually.'
    $example=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'settings.example.json') -Raw | ConvertFrom-Json
    if(Test-Path -LiteralPath $SettingsPath){$s=Get-Content -LiteralPath $SettingsPath -Raw|ConvertFrom-Json}else{$s=$example}
    $guess='';try{$guess=(& py -3.11 -c 'import sys;print(sys.executable)' 2>$null | Select-Object -Last 1)}catch{}
    if($guess){$s.python_exe=$guess}
    $s.python_exe=Ask '직접 설치한 Python 3.11 실행 파일 경로' $s.python_exe
    $s.cuda_dir=Ask '직접 준비한 CUDA DLL 폴더 (cudart64_13.dll 위치)' $s.cuda_dir
    $s.install_root=Ask '설치 폴더 (이 Git 저장소 바깥)' (Join-Path $env:LOCALAPPDATA 'StrataLocal')
    $base=Ask '자산 기본 폴더 (하위 경로는 각각 수정 가능)' 'E:\StrataAssets'
    foreach($g in @('models','pack','mtp','engine')){$s.paths.$g=Ask "$g folder" (Join-Path $base $g)}
    $s.images=Yes 'CPU 이미지 입력 사용 (8스레드)' $true
    if($s.images){$s.paths.vision=Ask '이미지 인코더 mmproj 폴더' (Join-Path $base 'vision')}
    $choice=Ask '컨텍스트 64 / 128 / 192 / 256 (96GB RAM·16GB GPU 검증값: 192)' '192'
    if($choice -notin @('64','128','192','256')){throw 'Invalid context choice'};$s.context=[int]$choice*1024
    $s.lan=Yes '다른 LAN PC에서 접속 허용' $false
    $s.advertise_host=''
    if($s.lan){$ip='';try{$ip=(Get-NetIPConfiguration|Where-Object IPv4DefaultGateway|Select-Object -First 1).IPv4Address.IPAddress}catch{};$s.advertise_host=Ask '실제 서버 LAN IPv4 주소 또는 호스트명' $ip}
    $s.port=[int](Ask 'API 포트' '8188')
    $s.copy_assets=Yes '대용량 파일을 설치 폴더로 복사 (약 82GiB). N=원래 경로 계속 사용' $true
    $s.wheels=Ask '오프라인 Python wheels 폴더 (빈칸=일반 패키지 PyPI 다운로드)' ''
    $s.merge_opencode=Yes '이 사용자 OpenCode 설정에 자동 병합 (백업·기존 MCP 보존)' $false
    $s.shortcuts=Yes '바탕화면 Strata Local 시작·중지 바로가기 생성' $true
    $s.startup=Yes 'Windows 로그인 시 자동 시작' $false
    $parent=Split-Path -Parent $SettingsPath;New-Item -ItemType Directory -Path $parent -Force|Out-Null
    [IO.File]::WriteAllText($SettingsPath,($s|ConvertTo-Json -Depth 12),[Text.UTF8Encoding]::new($false))
}
$s=Get-Content -LiteralPath $SettingsPath -Raw|ConvertFrom-Json
& $s.python_exe (Join-Path $PSScriptRoot 'scripts\strata_local.py') plan --settings $SettingsPath
if($LASTEXITCODE -ne 0){throw 'Preflight failed. See docs/ASSETS.ko.md and docs/PREREQUISITES.ko.md.'}
if($PlanOnly){return}
if(!(Yes '위 설정으로 설치할까요?' $true)){return}
& $s.python_exe (Join-Path $PSScriptRoot 'scripts\strata_local.py') install --settings $SettingsPath
if($LASTEXITCODE -ne 0){throw 'Install failed; no other service was stopped. Inspect the output and installation folder.'}
Write-Host "OpenCode JSON: $($s.install_root)\clients\Local\opencode.json"
if($s.lan){Write-Host "LAN JSON: $($s.install_root)\clients\LAN\opencode.json. Run scripts\Enable-LAN-Firewall.ps1 as administrator if needed."}
if(Yes '지금 새 모델을 시작할까요? (다른 GPU 모델과 동시 실행 주의)' $false){
    & (Join-Path $s.install_root '.venv\Scripts\python.exe') (Join-Path $s.install_root 'manager.py') start --root $s.install_root
    if($LASTEXITCODE -ne 0){throw 'Start did not become ready. Check logs/server.log.'}
}