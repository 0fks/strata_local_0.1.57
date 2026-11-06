# SC117 다운로드 파일

Prepare-Models.cmd가 아래 파일을 받고 pack·MTP를 생성합니다. 기본 다운로드 폴더는 clone 폴더 밖의 ../strata-assets이며 다른 드라이브의 폴더도 지정할 수 있습니다.

```text
strata-assets/
  models/   SC117 IQ3_S GGUF 2개 (83.86GB)
  pack/     검증된 GGUF에서 자동 생성 (약 1.55GB)
  mtp/      필요한 원본 텐서를 받아 자동 생성 (약 0.82GB)
  vision/   이미지 인코더 (이미지 사용 시 약 0.91GB)
  engine/   Strata 0.1.57 실행 프로그램 (약 0.97GB)
```

모델 저장소: SC117/Qwen3.8-Flash-Next-GSQ-RCO-abliterated-GGUF

필요한 모델 파일:
- Qwen3.8-Flash-Next-GSQ-RCO-abliterated-IQ3_S-00001-of-00002.gguf
- Qwen3.8-Flash-Next-GSQ-RCO-abliterated-IQ3_S-00002-of-00002.gguf

이미지 파일: mmproj-Qwen3.8-Flash-Next-BF16.gguf

GGUF·이미지 인코더는 Hugging Face에서 받습니다. revision eec4e10a2c29b440a2ae85591fa11569ce752963에 고정하며 크기·SHA-256을 검사합니다.

MTP는 ModelScope의 Qwen/Qwen3.8-Flash-Next에서 필요한 텐서만 받아 검증·변환합니다. 전체 safetensors를 다운로드하지 않습니다.

엔진 파일: strata-engine-0.1.57-windows-x86_64-cuda-cuda13.tar.gz
GitHub Niko1221/Strata의 v0.2.11 릴리스에서 받고 고정 해시를 검사합니다.

외부 PC의 NVMe에 준비할 때에는 Files ready가 나올 때까지 기다린 뒤 NVMe를 옮기세요. 대상 PC의 Install.cmd에서 실제 assets 경로를 지정하면 됩니다. 드라이브 문자가 달라져도 됩니다.

Unsloth의 GGUF나 pack은 이 SC117 프로필과 호환되지 않습니다. 기존 파일을 자동 삭제하지 않으므로 다른 모델을 받던 폴더와 구분해 준비하세요.
