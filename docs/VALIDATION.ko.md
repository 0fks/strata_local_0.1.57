# 검증 범위

배포 대상: Unsloth Qwen3.8-Flash-Next UD-IQ3_XXS v3.1 (4분할), Strata 엔진 0.1.57.

모델 파일의 크기·SHA-256은 보존된 Strata setup.py의 UNSLOTH_V31_SHARDS와 일치합니다. GGUF는 ModelScope에서 직접 받습니다. pack 해시는 실제 변환 후 별도로 기록하며 SC117 해시를 재사용하지 않습니다.

공급자·MCP 병합, 경로 변경, 다운로드 이어받기·해시·압축 경로 검증을 자동 테스트합니다. 기존 실행 중인 Strata는 수정하지 않았습니다. 기본 API 포트는 18765입니다.

대용량 모델 전체 다운로드·Unsloth 변환·추론·속도 비교는 수행하지 않았습니다. 새 PC에서 Prepare-Models.cmd와 Install.cmd를 완료한 후 실행 검증이 필요합니다. vendor 스냅샷과 라이선스를 보존합니다.

2026-11-06 확인: 자동 테스트 22개 통과, PowerShell 구문 검사 통과. 네트워크 Probe는 GGUF 4개 및 이미지 인코더의 실제 GGUF 헤더·고정 크기, GitHub 엔진 주소, ModelScope MTP의 8바이트 Range 응답까지 통과했습니다.
