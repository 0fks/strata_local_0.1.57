# SC117 모델 파일과 저장 구조

모든 모델은 SC117/Qwen3.8-Flash-Next-GSQ-RCO-abliterated-GGUF의 revision eec4e10a2c29b440a2ae85591fa11569ce752963에 고정합니다. Unsloth는 포함하지 않습니다.

```text
strata-assets/
  models/             IQ3_S GGUF 2개
    IQ3_XXS/          IQ3_XXS GGUF 2개
    IQ2_XS/           IQ2_XS GGUF 2개 (선택)
  pack/               IQ3_S 실행용 pack
    IQ3_XXS/          IQ3_XXS pack
    IQ2_XS/           IQ2_XS pack (선택)
  mtp/                공통 MTP 실행 파일 4개
  vision/             공통 이미지 인코더 (선택)
  engine/             공통 Strata 0.1.57 엔진
  prepared.json       준비된 모델 목록
```

IQ3_S의 기존 폴더 구조는 유지합니다. Install.cmd에는 최상위 strata-assets 폴더를 지정하고 모델을 선택하세요. 각 모델 폴더를 따로 지정하지 않습니다.

모델 파일명 형식:
`Qwen3.8-Flash-Next-GSQ-RCO-abliterated-{양자화}-00001-of-00002.gguf`
`Qwen3.8-Flash-Next-GSQ-RCO-abliterated-{양자화}-00002-of-00002.gguf`

| 양자화 | GGUF 합계 |
| --- | ---: |
| IQ3_S | 83.8636GB |
| IQ3_XXS | 76.1423GB |
| IQ2_XS | 68.4652GB |

이미지 인코더: mmproj-Qwen3.8-Flash-Next-BF16.gguf (0.9075GB)

MTP: 같은 저장소 strata/rt의 dense.bin, dense.txt, experts.bin, draft_vocab.bin (총 0.8243GB). 검증된 실행용 파일을 직접 받으므로 원본 safetensors나 ModelScope가 필요하지 않습니다.

엔진: GitHub Niko1221/Strata v0.2.11의 strata-engine-0.1.57-windows-x86_64-cuda-cuda13.tar.gz. 다운로드 약 628MB, 압축 해제 약 970MB.

모든 외부 바이너리는 고정 크기·SHA-256으로 검사합니다. IQ3_S pack의 바이너리는 기존 고정 해시로 검사합니다. 텍스트는 줄바꿈을 정규화하고 JSON은 내용으로 검사합니다. compat-bf16.json의 source는 모델 파일명만 대조하므로 드라이브·폴더 변경을 허용합니다. 추가 모델의 pack은 각 모델의 검증된 GGUF에서 생성하고 원본 모델 정보 및 생성 파일 해시를 pack-manifest.json에 기록합니다. 이후 설치와 경로 변경에서도 검사합니다.

공통 엔진·MTP·이미지는 한 번만 저장합니다. 모델 2번 조각의 내용이 같더라도 각 양자화의 파일명으로 따로 저장합니다. 특정 파일시스템의 링크 기능에 의존하지 않으므로 일반적인 NVMe 폴더 복사로 옮길 수 있습니다. 용량 계산에도 이 중복 저장을 포함합니다.

준비된 이미지 포함 예상 총량: 2종 165.8GB, IQ2_XS 포함 3종 235.8GB. 모델별 pack은 약 1.55GB로 계산한 예상값입니다. 준비용 Python 환경과 임시 공간은 별도입니다.

준비 옵션 4번은 IQ3_XXS만 받으며 이미지 포함 약 80.4GB, 준비 시 여유 공간 95GB 이상을 권장합니다. 기존 1번 폴더 구조와 설치 방식은 동일합니다. 일부 모델만 재준비해도 다른 모델 파일을 삭제하지 않습니다.
