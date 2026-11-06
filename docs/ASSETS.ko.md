# 모델 파일 준비하기

**이미 정상 작동하는 Strata PC가 있다면 다운로드하지 말고 복사하세요.** 아래 폴더들을 외장 SSD나 NAS에 보관하면 됩니다.

## 기존 PC에서 복사하는 방법

외장 SSD에 `StrataAssets` 폴더를 만들고 아래처럼 넣으세요. **왼쪽 폴더 안의 내용을 오른쪽 폴더로 복사**하면 됩니다.

| 기존 PC의 위치 | 외장 SSD에서 만들 폴더 |
| --- | --- |
| `D:\Local_Provider\Strata-data\models\SC117-IQ3_S\IQ3_S` | `StrataAssets\models` |
| `D:\Local_Provider\Strata-data\packs\sc117_iq3_s` | `StrataAssets\pack` |
| `D:\Local_Provider\Strata-data\models\SC117-IQ2_XS\strata\rt` | `StrataAssets\mtp` |
| `D:\Local_Provider\Strata-data\vision\SC117` | `StrataAssets\vision` |
| `D:\Git\Strata\engine-0.1.57` | `StrataAssets\engine` |

이 경로는 현재 운영 PC의 배치입니다. 다른 곳에 설치했으면 실제 파일이 있는 위치에서 복사하세요. `mtp`는 기존 경로에 IQ2_XS가 적혀 있어도 필요한 파일입니다. 이미지를 사용하지 않을 경우 `vision`은 생략할 수 있습니다.

다섯 폴더를 합쳐 약 **88GB**입니다. 새 PC에서 Install.cmd를 실행하고 이 경로를 지정하세요. 원래 폴더를 그대로 연결해서 사용할 수도 있지만, 외장 SSD를 나중에 빼려면 설치 화면에서 **파일 복사 Y**를 선택하세요.

## Hugging Face에 접속할 수 없으면?

- **기존 파일이 있음:** 위 방법으로 복사하면 됩니다. Hugging Face 접속 불필요.
- **다른 PC에서는 접속 가능:** 그 PC에서 받은 파일을 외장 SSD/NAS로 옮기세요.
- **파일도 없고 어느 PC에서도 다운로드 불가:** 이 저장소만으로 모델을 만들어낼 수는 없습니다. 원본 또는 동일 파일의 신뢰할 수 있는 배포처·보관본이 필요합니다.

알 수 없는 미러에서 이름만 같은 파일을 받으면 호환성을 보장할 수 없습니다. 설치기는 준비된 파일의 크기와 SHA-256을 기준 목록과 대조합니다. 원본이 사라지는 상황까지 대비하려면 **지금 정상 작동하는 파일 전체를 별도 보관**하세요.

## 파일을 새로 받을 때 참고

모델 출처: [SC117 GGUF 저장소](https://huggingface.co/SC117/Qwen3.8-Flash-Next-GSQ-RCO-abliterated-GGUF)

고정 revision: `eec4e10a2c29b440a2ae85591fa11569ce752963`.

| 폴더 | 필요한 내용 |
| --- | --- |
| models | `Qwen3.8-Flash-Next-GSQ-RCO-abliterated-IQ3_S-00001-of-00002.gguf`와 `...-00002-of-00002.gguf` 두 파일. 같은 폴더에 배치 |
| pack | dense.bin, index.txt, native_experts.txt, conversions.json, compat-bf16.json, tokenizer 폴더 전체 |
| mtp | dense.bin, dense.txt, experts.bin, draft_vocab.bin |
| vision | mmproj-Qwen3.8-Flash-Next-BF16.gguf |
| engine | strata.exe, strata-vision.exe, strata_kq.dll, cublas64_13.dll, cublasLt64_13.dll, BUILD.json, engine-component.json |

pack과 MTP는 GGUF 두 파일만 받았다고 자동으로 준비되는 것이 아닙니다. **처음 사용하는 분은 위 기존 PC의 준비된 폴더를 통째로 복사하는 방법을 사용하세요.**

엔진은 [0.1.57 CUDA13 공식 패키지](https://github.com/Niko1221/Strata/releases/download/v0.2.11/strata-engine-0.1.57-windows-x86_64-cuda-cuda13.tar.gz)를 받아 압축을 풀어도 됩니다. 선택한 engine 폴더 바로 아래에 위 실행 파일들이 있어야 합니다.

파일별 정확한 크기·해시는 `manifests/assets.json`에 있습니다. 다른 모델·양자화 파일은 이 설치 프로필에서 사용할 수 없습니다. 일반 safetensors 파일을 이 GGUF 대신 넣을 수는 없습니다.

## 완전 오프라인용 Python 패키지 준비 (필요한 경우만)

인터넷이 되는 Windows PC의 저장소 폴더에서 실행하세요. `PythonExe`는 직접 설치한 Python 3.11 경로로 바꿉니다.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Prepare-Wheels.ps1 -PythonExe C:\Path\To\Python311\python.exe -Destination E:\StrataAssets\wheels
```

Python·드라이버·CUDA 설치 파일은 별도로 준비합니다. 이 저장소와 모든 준비물을 함께 보관하면 원본 다운로드 서버에 의존하지 않고 재설치할 수 있습니다.