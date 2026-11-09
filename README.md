# Strata Local 설치

Windows · RAM 96GB · NVIDIA GPU 메모리 16GB 이상을 기준으로 준비한 설치기입니다. 모델은 모두 **SC117**이며 기본 API 포트는 **18765**입니다.

## 1. 모델을 NVMe에 준비

인터넷 되는 Windows PC에 NVMe를 연결하고 저장소를 clone하거나 `git pull`로 갱신합니다. Python 3.11 x64를 설치한 뒤 **Prepare-Models.cmd**를 실행하세요. 준비 작업에는 추론용 GPU가 필요하지 않습니다.

- 다운로드 폴더: NVMe의 원하는 폴더. 예: `X:\strata-assets`. 상대경로도 됩니다.
- 모델 선택 **1** 또는 Enter: **SC117 IQ3_S + IQ3_XXS** 두 종류.
- 모델 선택 **2**: **IQ2_XS까지 세 종류**.
- 모델 선택 **3**: 기존 **IQ3_S만**.
- 모델 선택 **4**: **IQ3_XXS만**.
- 이미지 입력: 사용할 예정이면 **Y**.
- 프록시: 사용하지 않으면 Enter.

모델·공통 MTP·이미지 인코더는 Hugging Face, 엔진은 GitHub에서 받습니다. 모델마다 pack까지 생성하고 검증한 뒤 **Files ready**가 나오면 완료입니다. 중단되면 같은 폴더와 선택으로 다시 실행하세요.

| 준비할 SC117 모델 | 이미지 포함 실행용 파일 예상 합계 | 준비 시작 전 권장 여유 공간 |
| --- | ---: | ---: |
| 1번: IQ3_S + IQ3_XXS | 165.8GB | 180GB 이상 |
| 2번: 위 두 종류 + IQ2_XS | 235.8GB | 250GB 이상 |
| 3번: IQ3_S만 | 88.1GB | 105GB 이상 |
| 4번: IQ3_XXS만 | 80.4GB | 95GB 이상 |

pack 용량은 추정치이며 준비용 Python 환경·임시 파일은 별도입니다. 3종을 준비한다면 여유 있게 500GB급 NVMe를 권장합니다. 공통 엔진·MTP·이미지 인코더는 한 번만 저장합니다.

## 2. 사용할 PC에 NVMe 연결

NVMe를 사용할 PC에 연결합니다. 드라이브 문자가 바뀌어도 됩니다. 저장소 코드도 해당 PC에 준비하세요. 실행용 파일은 다시 다운로드하지 않습니다.

[Python 3.11 Windows installer (64-bit)](https://www.python.org/downloads/release/python-3119/)와 NVIDIA 드라이버 **580.65 이상**을 직접 설치합니다. 저장소 폴더의 PowerShell에서 다음 두 줄을 직접 실행하세요.

```powershell
py -3.11 -m venv .\prereqs
.\prereqs\Scripts\python.exe -m pip install nvidia-cuda-runtime==13.0.96 nvidia-cublas==13.0.2.14
```

Python·CUDA 및 설치 중 Python 패키지 설치는 모델 준비와 별개입니다. NVMe의 .prepare-venv는 대상 PC에서 재사용하지 않습니다.

## 3. Install.cmd 실행

- 준비한 파일 폴더: NVMe의 실제 경로. 예: `E:\strata-assets`.
- 모델: **IQ3_S / IQ3_XXS / IQ2_XS** 중 준비한 것을 선택.
- 설치 폴더: 기본값 사용. 모델마다 별도 폴더가 제안됩니다.
- Python / CUDA 경로: 2단계대로 준비했다면 Enter.
- 컨텍스트: 모르면 **192**.
- LAN: 다른 PC도 접속하면 **Y**, 이 PC만 쓰면 **N**.
- OpenCode 자동 병합: 이 PC의 OpenCode와 연결하려면 **Y**. 기존 MCP는 보존합니다.

설치가 끝나면 모델명이 붙은 바탕화면 **Strata Local IQ3_S Start / Stop** 등의 바로가기를 사용합니다. OpenCode를 다시 열고 해당 SC117 모델을 선택하세요. OpenCode 프로그램은 별도 설치입니다.

## 모델 두 종류를 비교하려면

Install.cmd를 모델마다 한 번씩 실행해 별도 설치 폴더를 만드세요. **기존 모델을 Stop한 뒤 다음 모델을 Start**하세요. 기본 포트를 함께 사용하므로 한 번에 하나만 실행합니다. OpenCode 설정은 각 설치 폴더의 `clients/Local/opencode.json` 또는 `clients/LAN/opencode.json`에 있습니다. 실행하는 모델의 JSON을 사용하세요.

자동 시작은 사용할 모델 하나에만 설정하세요. 모델을 바꿔 설치해도 이미 설치한 실행 폴더를 덮어쓰지 않습니다.

## 파일 폴더를 나중에 옮기려면

Strata를 Stop → 다운로드 폴더 전체 이동 → **Change-Assets.cmd**에서 설치 폴더와 새 파일 폴더 지정 → Start 순서입니다. API 키와 모델·OpenCode 설정은 유지합니다.

[파일 목록](docs/ASSETS.ko.md) · [Python/CUDA](docs/PREREQUISITES.ko.md) · [OpenCode](docs/OPENCODE.ko.md) · [연결 진단](docs/NETWORK.ko.md) · [검증 범위](docs/VALIDATION.ko.md) · [라이선스](THIRD_PARTY_NOTICES.md)

이미 1번으로 준비한 데이터는 업데이트 후에도 그대로 사용합니다. 다시 다운로드하거나 폴더를 옮길 필요가 없습니다. 같은 폴더에서 4번만 재실행해도 기존 IQ3_S 데이터는 삭제하지 않습니다.

회사 OpenCode가 기존 config.json의 provider(단수)를 쓰는 경우: Export-OpenCode-Provider.cmd를 실행하고 해당 Strata 설치 폴더를 지정하세요. 생성된 clients/Local/provider-entry.txt를 기존 provider 객체 안에 추가하면 됩니다. LAN용은 clients/LAN에 있습니다. 기존 $schema·다른 공급자·MCP는 유지합니다. [복사 방법](docs/OPENCODE.ko.md)
