# 직접 설치할 프로그램

이 도구는 Python·CUDA·드라이버를 자동 설치하지 않습니다. 설치 마법사가 만드는 가상환경에는 Strata 일반 Python 의존성만 설치합니다.

| 구성 | 기준 |
| --- | --- |
| Windows | 10/11 x64, 현재 검증 Windows 11 |
| Python | **3.11 x64**, 운영 검증 3.11.8. 다른 major/minor는 이 도구가 거부 |
| NVIDIA 드라이버 | **580.65 이상**, 운영 검증 617.42 |
| CUDA | **13.0 계열** |
| CUDA Python runtime 패키지 | 운영 검증 `nvidia-cuda-runtime==13.0.96` |
| cuBLAS | 운영 검증 `nvidia-cublas==13.0.2.14`, 고정 엔진 폴더에도 포함 |
| 메모리 | 이 IQ3_S 프로필은 96GB 기준. 90GiB 미만은 자동 설치 거부 |
| GPU | RTX 5070 Ti 16GB 검증. 다른 GPU는 별도 확인 필요 |
| SSD | 자산 복사 약 82.1GiB + 소스·가상환경·여유 공간. 이중 보관 공간도 계산 |

Python은 python.org, 드라이버와 CUDA Toolkit은 NVIDIA의 공식 배포물에서 직접 준비합니다. CUDA Toolkit 13.0을 이미 설치했다면 `cudart64_13.dll`이 있는 실제 `bin` 또는 `bin\x64` 폴더를 마법사에 지정하세요.

운영 PC와 동일한 DLL 버전을 별도 환경에 직접 준비하는 방법도 있습니다:

```powershell
py -3.11 -m venv C:\StrataPrereqs
C:\StrataPrereqs\Scripts\python.exe -m pip install nvidia-cuda-runtime==13.0.96 nvidia-cublas==13.0.2.14
```

이 경우 CUDA 경로는 다음입니다:

```text
C:\StrataPrereqs\Lib\site-packages
vidia\cu13\bin\x86_64
```

CUDA 경로에 cudart64_13.dll이 없으면 사전 검사가 실패합니다. DLL 이름으로 CUDA 13 계열을 확인하며 파일 세부 버전을 자동 비교하지는 않습니다. 정확한 재현을 원하면 위 고정 패키지 버전을 사용하세요. NVIDIA 드라이버 없이 CUDA DLL만 준비해서는 모델을 실행할 수 없습니다.

완전 오프라인 설치라면 Python 설치 프로그램·CUDA/드라이버 설치 파일 또는 패키지 wheels도 직접 별도 보관해야 합니다. Strata 일반 의존성 wheels는 인터넷이 되는 Windows x64/Python 3.11 PC에서 아래 도구로 준비할 수 있습니다.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Prepare-Wheels.ps1 -PythonExe C:\Path\To\Python311\python.exe -Destination E:\StrataAssets\wheels
```

마법사에서 이 wheels 폴더를 지정하면 일반 의존성 설치도 PyPI를 사용하지 않습니다. CUDA 패키지는 이 helper의 자동 설치 대상이 아닙니다. pip 자체는 Python/venv에 포함된 것을 사용합니다.

Windows Smart App Control이 엔진을 차단할 수 있습니다. 이 설치기는 보안 설정을 바꾸거나 차단을 우회하지 않습니다. 공식 배포·해시와 차단 원인을 확인한 후 사용자가 별도로 결정해야 합니다.
