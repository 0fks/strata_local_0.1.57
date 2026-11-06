# 별도로 준비할 대용량 파일

아래 파일은 Git에 포함하지 않습니다. 마법사에서 각 폴더 경로를 직접 지정할 수 있어 반드시 한 자산 폴더로 모을 필요는 없습니다. 파일명은 원래대로 유지하세요. 검증 기준은 `manifests/assets.json`의 크기·SHA-256입니다.

```text
E:\StrataAssets  models\  IQ3_S GGUF 두 샤드를 같은 폴더에
  pack\    sc117_iq3_s pack의 내용 (tokenizer 폴더 포함)
  mtp\     MTP rt의 내용
  vision\  mmproj (이미지 사용 시에만 필수)
  engine\  0.1.57 CUDA13 엔진 패키지 내용
  wheels\  오프라인 일반 Python 패키지 (선택)
```

## 필수 모델

- `Qwen3.8-Flash-Next-GSQ-RCO-abliterated-IQ3_S-00001-of-00002.gguf` — 55,063,448,064 bytes
- `Qwen3.8-Flash-Next-GSQ-RCO-abliterated-IQ3_S-00002-of-00002.gguf` — 28,800,138,432 bytes

출처: https://huggingface.co/SC117/Qwen3.8-Flash-Next-GSQ-RCO-abliterated-GGUF
고정 revision: `eec4e10a2c29b440a2ae85591fa11569ce752963`.
둘 다 필요하며, 다른 양자화·분할 파일과 섞으면 안 됩니다.

## 필수 pack / MTP

- pack: `dense.bin` (1,538,035,200 bytes), `index.txt`, `native_experts.txt`, `conversions.json`, `compat-bf16.json`, `tokenizer/` 전체.
- MTP: `dense.bin` (116,099,072 bytes), `dense.txt`, `experts.bin` (707,788,800 bytes), `draft_vocab.bin` (425,196 bytes).

이 pack은 위 SC117 모델로 준비한 것입니다. 기존 검증된 복사본을 보관하세요. 원본이 사라졌을 때도 쉽게 설치하려면 모델뿐 아니라 pack과 MTP도 함께 백업해야 합니다. MTP는 이전 서버에서 IQ2_XS 이름의 경로에 있었지만 IQ3_S에서도 사용하는 공유 데이터입니다. `.done`, `.verified.json` 파일은 이 설치기의 필수 항목이 아닙니다.

## 이미지 사용 시

- `mmproj-Qwen3.8-Flash-Next-BF16.gguf` — 907,542,944 bytes.
- 기존 검증된 파일과 manifest의 SHA-256이 같아야 합니다.
- 이미지를 끄면 vision 폴더는 검사·복사·서버 설정에서 제외됩니다.

## 엔진

0.1.57 Windows x64 CUDA13 패키지 전체를 준비합니다:
https://github.com/Niko1221/Strata/releases/download/v0.2.11/strata-engine-0.1.57-windows-x86_64-cuda-cuda13.tar.gz

압축 SHA-256:
`0cdf191f0fb39b90edbb902f4d096b90f2ee90a4542deb8aef24985b22407c0f`

압축 해제 후 지정한 engine 폴더 바로 아래에 `strata.exe`, `strata-vision.exe`, `strata_kq.dll`, `cublas64_13.dll`, `cublasLt64_13.dll`, `BUILD.json`, `engine-component.json`이 있어야 합니다. tar 내부 구조에 따라 중간 폴더를 제거하거나 마법사에 실제 하위 폴더를 지정하세요. 검증된 기존 엔진 폴더를 복사해도 됩니다.

원본 저장소·다운로드 서버 소실에도 대비하려면 이 엔진 폴더와 모델·pack·MTP·mmproj, Python/CUDA 사전 준비물, 일반 Python wheels를 개인 SSD/NAS에 함께 보관하세요. Git clone만으로 오프라인 설치 자산까지 생기지는 않습니다.

파일 검증은 다음처럼 단독 실행할 수 있습니다:

```powershell
py -3.11 .\scripts\strata_local.py verify-assets --settings .\settings.local.json
```
