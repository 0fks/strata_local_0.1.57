# Strata Local 설치

이 폴더를 원하는 위치에 놓고, 아래 순서대로 진행하세요. **경로는 이 폴더 기준의 상대경로**를 사용합니다.

필요한 PC: **Windows · RAM 96GB · NVIDIA GPU 메모리 16GB 이상 · 여유 디스크 약 100GB**.

## 1. Python과 CUDA 준비

[Python 3.11 Windows installer (64-bit)](https://www.python.org/downloads/release/python-3119/)를 직접 설치합니다. NVIDIA 드라이버는 **580.65 이상**이 필요합니다.

이 저장소 폴더에서 PowerShell을 열고 다음 두 줄을 직접 실행하세요. CUDA 파일은 `./prereqs`에 준비됩니다.

```powershell
py -3.11 -m venv .\prereqs
.\prereqs\Scripts\python.exe -m pip install nvidia-cuda-runtime==13.0.96 nvidia-cublas==13.0.2.14
```

## 2. Prepare-Models.cmd 실행

**`Prepare-Models.cmd`를 더블클릭**합니다.

- 파일을 받을 폴더: 기본값 **`../strata-assets`** (clone 폴더 바깥). `D:\strata-assets`처럼 다른 드라이브 경로도 입력할 수 있습니다.
- 이미지 입력: 사용하면 **Y**, 텍스트만 쓰면 **N**.

모델·엔진을 다운로드하고 실행에 필요한 파일을 자동 생성합니다. **GGUF는 hf-mirror, MTP는 ModelScope를 사용합니다. 실제 GGUF 전송은 Hugging Face CDN으로 연결될 수 있습니다.** 약 90GB와 준비용 임시 공간이 필요해 시간이 걸립니다. 중단됐다면 같은 폴더를 선택해 다시 실행하세요.

접속 시간 초과(WinError 10060)가 나면 [다운로드 연결 안내](docs/NETWORK.ko.md)를 보세요.

## 3. Install.cmd 실행

**`Install.cmd`를 더블클릭**하고 아래처럼 선택하세요.

| 질문 | 선택 방법 |
| --- | --- |
| Python / CUDA 경로 | 1단계대로 준비했다면 Enter |
| 설치 폴더 | 기본 `./runtime` 또는 원하는 상대경로 |
| 다운로드한 파일 폴더 | 2단계에서 정한 경로 |
| 이미지 입력 | 2단계와 같은 선택 |
| 컨텍스트 | 모르면 **192** |
| LAN 접속 | 이 PC만 쓰면 **N**, 다른 PC도 접속하면 **Y** |
| OpenCode 자동 병합 | 이 PC의 OpenCode와 연결하려면 **Y** |
| 바탕화면 바로가기 | **Y** |
| 로그인 자동 시작 | 원하면 **Y** |

대괄호 안 기본값이 맞으면 **Enter만 누르면 됩니다.**

## 4. 사용하기

설치가 끝나면 바탕화면 **Strata Local Start**로 켜고 **Strata Local Stop**으로 끕니다.

OpenCode를 완전히 종료했다가 다시 열고 **SC117 IQ3_S** 모델을 선택하세요. LAN 연결용 설정은 설치 폴더의 `clients/LAN/opencode.json`에 생성됩니다.

다운로드한 파일 폴더는 설치 후에도 계속 사용하므로 삭제하지 마세요. OpenCode 프로그램 자체는 별도로 설치해야 합니다.

[다운로드 경로·파일 목록](docs/ASSETS.ko.md) · [Python/CUDA 상세](docs/PREREQUISITES.ko.md) · [OpenCode 연결](docs/OPENCODE.ko.md)

## 다운로드 위치를 나중에 바꾸려면

1. **Strata Local Stop**으로 중지합니다.
2. 다운로드 폴더 전체를 새 위치로 옮깁니다. 예: `D:\strata-assets` → `E:\strata-assets`.
3. **`Change-Assets.cmd`**를 더블클릭하고 설치 폴더와 새 파일 폴더를 입력합니다.
4. 파일 검사가 끝나면 **Strata Local Start**로 다시 켭니다.

이 도구는 파일을 직접 이동하지 않고 새 경로를 연결합니다. API 키·모델 설정·OpenCode 설정은 유지하고 변경 전 설정을 백업합니다. 실행 중이거나 파일이 부족하면 변경을 거부합니다. 상대경로와 다른 드라이브의 전체 경로를 모두 사용할 수 있습니다.

---

이 배포본은 SC117 IQ3_S 전용입니다. 원본 Strata 소스와 라이선스를 보존하며 API 키는 설치할 때 새로 생성합니다. [라이선스](THIRD_PARTY_NOTICES.md) · [검증 범위](docs/VALIDATION.ko.md) · [관리자용 업데이트 절차](docs/UPDATING.ko.md)