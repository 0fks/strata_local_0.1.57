# 다운로드 연결 오류

SC117 모델·이미지·MTP는 Hugging Face에서, 엔진은 GitHub에서 받습니다. ModelScope를 사용하지 않습니다.

Check-Downloads.cmd는 Python 패키지를 설치하지 않고 기본 두 모델과 공통 파일의 실제 일부 데이터를 검사합니다. 실패한 서버는 FAIL 줄에 표시됩니다. 세 모델을 모두 검사하려면 Prepare-Models.ps1 -Probe에서 2를 선택하세요.

다운로드가 중단되면 같은 폴더·선택으로 다시 실행합니다. 가능한 경우 이어받고 SHA-256을 검사합니다. 이미 검증된 공통 파일은 다시 받지 않습니다.

회사망 변경 없이 인터넷 되는 PC에서 NVMe에 준비할 수 있습니다. Files ready가 나오면 사용할 PC로 옮겨 Install.cmd에서 실제 경로와 모델을 선택하세요. Python·CUDA·패키지 준비는 별도입니다.

## SSL 인증서 검증 실패

SSLCertVerificationError는 timeout과 다릅니다. Python이 서버가 제시한 인증서의 신뢰 체인·유효기간 등을 검증하지 못했다는 뜻입니다.

먼저 git pull 후 Prepare-Models.cmd를 같은 폴더로 다시 실행하세요. 준비 환경의 certifi를 최신으로 갱신하고 Windows 기본 신뢰 인증서에 공개 CA 목록을 추가합니다. 인증서 검증과 호스트명 검증은 유지합니다.

계속 실패하면 새 로그의 verify_code와 상세 사유를 확인하세요. PC 날짜·시간 오류, 백신 HTTPS 검사, 프록시의 사용자 지정 인증서, 누락된 중간 인증서 등을 구분해야 합니다. 공개 CA 갱신이 모든 원인을 해결하지는 않습니다.

신뢰할 수 있는 관리자나 보안 프로그램 제공자로부터 받은 PEM CA 인증서가 필요한 환경에서는 다음처럼 추가할 수 있습니다. 임의의 인증서를 추가하지 마세요.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Prepare-Models.ps1 -CAFile .\trusted-ca.pem
```

CA 경로·프록시·개인 인증서는 저장소에 커밋하지 않습니다. 일반 다운로드 설정에서는 별도 CA 파일이 필요하지 않습니다.

## STEP 3 IQ3_S/pack 검사 실패

17019e6까지의 설치기는 compat-bf16.json에 기록된 절대경로까지 원본 PC의 바이트 해시와 비교해 정상 pack을 잘못 거부할 수 있었습니다. 최신 버전은 경로·줄바꿈·JSON 표현 차이를 정규화하고 실제 내용과 가중치는 계속 검사합니다.

git pull 후 같은 다운로드 폴더와 모델 선택으로 Prepare-Models.cmd를 다시 실행하세요. 정상 GGUF·엔진은 해시 확인 후 재사용하고, 기존 정상 pack도 재사용합니다. 대용량 모델을 삭제하거나 다시 다운로드할 필요는 없습니다. 파일 확인에는 시간이 걸릴 수 있습니다.

## Install 실행 직후 Join-Path의 Path가 비었다는 오류

param의 SettingsPath 기본값 계산 시 PSScriptRoot가 비어 발생할 수 있습니다. 모델 폴더의 E: → F: 변경과는 별개입니다. git pull로 갱신 후 Install.cmd를 실행하세요. 최신 설치기는 매개변수 처리 후 설치기 경로와 기본 설정 경로를 계산합니다. assets 데이터나 Python 환경을 삭제할 필요는 없습니다.
