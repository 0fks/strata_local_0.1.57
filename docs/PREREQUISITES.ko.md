# 처음 한 번만 준비하세요

Python과 CUDA는 사용자가 직접 준비합니다. 이미 준비했다면 중복 설치할 필요가 없습니다.

## 1. Python 3.11 / 64비트

1. [Python 공식 다운로드](https://www.python.org/downloads/release/python-3119/)를 엽니다.
2. 아래 Files 목록에서 **Windows installer (64-bit)**를 받습니다. 32-bit·ARM64·embeddable은 고르지 마세요.
3. 설치 화면에서 **Add python.exe to PATH**를 체크하고 설치합니다.

이 도구는 Python 3.11 계열을 사용합니다. 기존 PC에서 검증한 버전은 3.11.8이며, 링크의 3.11.9 설치 프로그램도 같은 3.11 계열입니다. 링크가 최신 보안 패치라는 뜻은 아닙니다.

## 2. NVIDIA 드라이버

[NVIDIA 공식 드라이버](https://www.nvidia.com/Download/index.aspx)에서 그래픽카드에 맞는 드라이버를 설치합니다. 필요한 버전은 **580.65 이상**, 기존 검증 버전은 **617.42**입니다.

## 3. CUDA 실행 파일

이미 CUDA Toolkit 13.0이 있다면 `cudart64_13.dll`이 있는 폴더를 설치 화면에 지정하면 됩니다.

없다면 **PowerShell을 열고 아래 두 줄을 차례대로 직접 실행**하세요. 기존 PC와 같은 버전의 CUDA 실행 파일을 `C:\StrataPrereqs`에 준비합니다.

```powershell
py -3.11 -m venv C:\StrataPrereqs
C:\StrataPrereqs\Scripts\python.exe -m pip install nvidia-cuda-runtime==13.0.96 nvidia-cublas==13.0.2.14
```

설치 화면에서 CUDA 폴더를 물으면 **아래 경로를 복사해서 붙여넣으세요.**

```text
C:\StrataPrereqs\Lib\site-packages\nvidia\cu13\bin\x86_64
```

이제 저장소 폴더의 **Install.cmd**를 실행하면 됩니다.

## 인터넷이 전혀 없는 PC라면

Python·드라이버·CUDA 설치 파일과 일반 Python 패키지도 인터넷이 되는 PC에서 미리 준비해야 합니다. 모델 파일만 복사해 두는 것과 완전 오프라인 설치는 다릅니다.

일반 Python 패키지는 저장소의 `scripts/Prepare-Wheels.ps1`로 준비할 수 있습니다. 준비한 wheels 폴더를 마법사에 지정하면 PyPI에 접속하지 않습니다. 자세한 명령은 [파일 준비 안내](ASSETS.ko.md)를 참고하세요.

이 설치기는 Windows 보안 설정을 자동 변경하지 않습니다. Windows가 엔진 실행을 차단하면 차단 내용을 확인한 후 사용자가 판단해야 합니다.