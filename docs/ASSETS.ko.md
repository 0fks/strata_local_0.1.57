# 다운로드 위치와 파일 목록

**Prepare-Models.cmd가 다운로드와 준비를 처리합니다.** 다른 PC에서 파일을 가져올 필요가 없습니다.

기본 위치는 다음과 같습니다. 다른 폴더를 선택하면 폴더 이름만 달라집니다.

```text
../strata-assets/
  models/   SC117 IQ3_S GGUF 2개
  pack/     GGUF에서 자동 생성
  mtp/      ModelScope에서 필요한 텐서를 받아 자동 생성
  vision/   이미지 인코더 — 이미지 사용 시
  engine/   Strata 0.1.57 실행 프로그램
```

## Hugging Face 대신 사용하는 경로

### SC117 IQ3_S — hf-mirror

아래 파일의 정상 응답과 파일 크기를 2026-11-06에 확인했습니다. 다운로드 도구는 완료 후 고정 SHA-256도 검사합니다.

- [GGUF 1/2 — 약 55.1GB](https://hf-mirror.com/SC117/Qwen3.8-Flash-Next-GSQ-RCO-abliterated-GGUF/resolve/eec4e10a2c29b440a2ae85591fa11569ce752963/IQ3_S/Qwen3.8-Flash-Next-GSQ-RCO-abliterated-IQ3_S-00001-of-00002.gguf)
- [GGUF 2/2 — 약 28.8GB](https://hf-mirror.com/SC117/Qwen3.8-Flash-Next-GSQ-RCO-abliterated-GGUF/resolve/eec4e10a2c29b440a2ae85591fa11569ce752963/IQ3_S/Qwen3.8-Flash-Next-GSQ-RCO-abliterated-IQ3_S-00002-of-00002.gguf)
- [이미지 인코더 — 약 0.9GB](https://hf-mirror.com/SC117/Qwen3.8-Flash-Next-GSQ-RCO-abliterated-GGUF/resolve/eec4e10a2c29b440a2ae85591fa11569ce752963/mmproj-Qwen3.8-Flash-Next-BF16.gguf)

수동으로 받았다면 위 두 GGUF를 선택한 `models` 폴더에, 이미지 파일은 `vision` 폴더에 원래 이름대로 넣고 Prepare-Models.cmd를 실행하세요. 이미 정확히 받은 파일은 검사 후 다시 받지 않습니다. pack과 MTP는 도구가 준비하므로 사용자가 따로 구할 필요가 없습니다.

hf-mirror는 제3자 대체 서버이며 실제 전송이 huggingface.co와 us.aws.cdn.hf.co로 리디렉션되는 것을 확인했습니다. 따라서 Hugging Face 네트워크 접속 없이 다운로드된다고 보장할 수 없습니다. 항상 접속된다고 보장할 수 없으며, 파일이 고정 해시와 다르면 준비를 중단합니다. 단순히 파일 이름만 보고 다른 가중치를 사용하지 않습니다.

### MTP — ModelScope

[Qwen/Qwen3.8-Flash-Next](https://www.modelscope.cn/models/Qwen/Qwen3.8-Flash-Next)에서 필요한 MTP 텐서만 내려받습니다. 인덱스와 HTTP Range 응답을 확인했습니다. 전체 원본 모델을 받는 방식이 아닙니다. Strata의 고정 텐서 해시 검사 후 실행용 MTP를 생성합니다.

### 엔진 — GitHub Releases

[Strata 0.1.57 CUDA13 패키지](https://github.com/Niko1221/Strata/releases/download/v0.2.11/strata-engine-0.1.57-windows-x86_64-cuda-cuda13.tar.gz)를 다운로드해 자동 압축 해제합니다. 고정 아카이브·파일 해시를 검사합니다.

## Unsloth를 찾는 경우

[ModelScope의 Unsloth Qwen3.8-Flash-Next-GGUF](https://www.modelscope.cn/models/unsloth/Qwen3.8-Flash-Next-GGUF)도 파일 목록을 확인했습니다. 다만 이 배포본은 SC117 전용이므로 Unsloth 파일을 대신 넣으면 안 됩니다. 별도 프로필과 pack·설정 검증이 필요합니다. 확인하지 않은 Unsloth 모델을 설치 선택지로 표시하지 않습니다.

SC117의 같은 이름 ModelScope 저장소는 확인 시 404였으므로 SC117용 대체 경로로 안내하지 않습니다.

## 접속이 안 될 때

먼저 Prepare-Models.ps1의 `-Probe`로 작은 응답만 확인할 수 있습니다:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Prepare-Models.ps1 -Probe
```

이 검사는 대용량 가중치를 받지 않습니다. 서버 차단·다운로드 오류가 나면 출력된 URL과 상태를 확인하세요. 모든 대체 서버까지 접속 불가하면 파일을 새로 다운로드할 수 없으므로 네트워크 경로를 해결해야 합니다.
## 폴더 선택 / 변경

다운로드 질문에 `../strata-assets`처럼 clone 폴더 밖의 상대경로 또는 `D:\strata-assets`처럼 다른 드라이브 경로를 입력할 수 있습니다. 설치 화면의 다운로드 폴더에도 같은 값을 입력하세요.

나중에 옮길 때에는 Strata를 중지하고 폴더 전체를 이동한 뒤 `Change-Assets.cmd`로 새 위치를 연결하세요. Python/CUDA가 있는 prereqs 및 설치 폴더 자체를 옮기는 기능은 아닙니다.

연결 시간 초과는 [네트워크 오류 안내](NETWORK.ko.md)를 참고하세요.
