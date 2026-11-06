# 다운로드 파일과 위치

Prepare-Models.cmd를 실행하면 필요한 파일을 받고 pack과 MTP를 자동 생성합니다.

기본 위치는 clone 폴더 밖의 `../strata-assets`입니다. `D:\strata-assets`처럼 다른 드라이브 경로도 입력할 수 있습니다. 설치할 때 같은 폴더를 지정하세요.

```text
../strata-assets/
  models/   Unsloth UD-IQ3_XXS v3.1 GGUF 4개 (약 83.6GB)
  pack/     GGUF에서 자동 생성 + pack-manifest.json
  mtp/      ModelScope에서 필요한 텐서만 받아 자동 생성
  vision/   mmproj-BF16.gguf (이미지 사용 시, 약 0.9GB)
  engine/   Strata 0.1.57 실행 프로그램
```

## 모델 다운로드

[ModelScope Unsloth Qwen3.8-Flash-Next-GGUF](https://www.modelscope.cn/models/unsloth/Qwen3.8-Flash-Next-GGUF)의 UD-IQ3_XXS 폴더를 사용합니다. 파일명에 **of-00004**가 있는 4개 파일이어야 합니다. 이전 3분할 파일은 사용하지 않습니다.

- [GGUF 1/4](https://www.modelscope.cn/models/unsloth/Qwen3.8-Flash-Next-GGUF/resolve/master/UD-IQ3_XXS/Qwen3.8-Flash-Next-UD-IQ3_XXS-00001-of-00004.gguf)
- [GGUF 2/4](https://www.modelscope.cn/models/unsloth/Qwen3.8-Flash-Next-GGUF/resolve/master/UD-IQ3_XXS/Qwen3.8-Flash-Next-UD-IQ3_XXS-00002-of-00004.gguf)
- [GGUF 3/4](https://www.modelscope.cn/models/unsloth/Qwen3.8-Flash-Next-GGUF/resolve/master/UD-IQ3_XXS/Qwen3.8-Flash-Next-UD-IQ3_XXS-00003-of-00004.gguf)
- [GGUF 4/4](https://www.modelscope.cn/models/unsloth/Qwen3.8-Flash-Next-GGUF/resolve/master/UD-IQ3_XXS/Qwen3.8-Flash-Next-UD-IQ3_XXS-00004-of-00004.gguf)

- [이미지 인코더](https://www.modelscope.cn/models/unsloth/Qwen3.8-Flash-Next-GGUF/resolve/master/mmproj-BF16.gguf)

크기·SHA-256은 원본 Strata의 Unsloth v3.1 revision `d96201194f103c906994f283f504209dc8d2a10c`와 대조합니다. ModelScope 주소는 master이므로 파일이 교체되면 검증에 실패하고 중단합니다. pack은 해당 GGUF에서 생성한 파일의 크기·해시와 원본 모델 정보를 별도로 기록합니다.

수동 다운로드 시 GGUF 4개를 models, 이미지 인코더를 vision에 원래 이름으로 넣고 Prepare-Models.cmd를 실행하세요. 정확한 파일은 다시 받지 않습니다. SC117용 pack은 새 모델과 호환되지 않아 새로 생성됩니다. 이전 모델 파일을 자동으로 삭제하지 않습니다.

## MTP와 엔진

MTP는 [ModelScope Qwen](https://www.modelscope.cn/models/Qwen/Qwen3.8-Flash-Next)에서 필요한 텐서만 받아 고정 해시로 검사합니다. 전체 safetensors를 받지 않습니다.

엔진은 [GitHub Strata 릴리스](https://github.com/Niko1221/Strata/releases/tag/v0.2.11)의 0.1.57 CUDA13 패키지이며 아카이브와 실행 파일의 고정 해시를 검사합니다.

## 폴더 변경

Strata Local Stop → 다운로드 폴더 전체 이동 → Change-Assets.cmd에서 새 경로 입력 → Strata Local Start 순서입니다. 파일 이동은 사용자가 합니다.

[연결 오류 안내](NETWORK.ko.md)
