# Python과 CUDA 직접 준비

## Python

[Python 3.11 공식 페이지](https://www.python.org/downloads/release/python-3119/)의 **Windows installer (64-bit)**를 설치하세요. 32-bit·ARM64·embeddable은 선택하지 않습니다. 설치 화면에서 **Add python.exe to PATH**를 체크하세요.

이 도구는 Python 3.11 x64를 사용합니다. 모델 운용 검증은 3.11.8에서 했으며 링크는 같은 계열의 Windows 설치 프로그램 3.11.9입니다. 최신 보안 패치라는 뜻은 아닙니다.

## NVIDIA 드라이버

[NVIDIA 공식 배포](https://www.nvidia.com/Download/index.aspx)에서 자신의 그래픽카드에 맞는 **580.65 이상** 버전을 설치하세요. 검증한 버전은 617.42입니다.

## CUDA

저장소 폴더에서 PowerShell을 열고 직접 실행합니다:

```powershell
py -3.11 -m venv .\prereqs
.\prereqs\Scripts\python.exe -m pip install nvidia-cuda-runtime==13.0.96 nvidia-cublas==13.0.2.14
```

그러면 기본 설정의 아래 상대경로를 그대로 사용할 수 있습니다.

- Python: `./prereqs/Scripts/python.exe`
- CUDA: `./prereqs/Lib/site-packages/nvidia/cu13/bin/x86_64`

Python·CUDA·드라이버는 설치 도구가 자동 설치하지 않습니다. 일반 Python 의존성은 다운로드/설치 도구가 PyPI에서 준비합니다. Windows가 엔진을 차단하더라도 이 도구가 보안 설정을 자동 변경하거나 우회하지는 않습니다.