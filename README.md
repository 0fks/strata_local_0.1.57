# Strata Local 설치하기

**새 PC에서 모델 파일을 준비하고, `Install.cmd`를 더블클릭하면 됩니다.**

이 설치법은 **Windows · RAM 96GB · NVIDIA 그래픽 메모리 16GB 이상** 기준입니다.

## 1. 모델 파일을 준비하세요

이미 Strata가 잘 돌아가는 PC가 있다면 **그 PC의 파일을 외장 SSD로 복사**하세요. 다시 다운로드할 필요가 없습니다. **Hugging Face에 접속할 수 없어도 됩니다.**

준비할 폴더는 다섯 개입니다.

```text
StrataAssets/
  models/   모델 파일 2개
  pack/     모델 실행에 필요한 준비 파일
  mtp/      응답 생성 보조 파일
  vision/   이미지 인코더 — 이미지를 안 쓰면 생략
  engine/   Strata 실행 프로그램
```

어디에서 무엇을 복사할지는 **[파일 준비 안내](docs/ASSETS.ko.md)**를 보세요. 전체 약 **88GB**입니다. 설치할 드라이브에는 **100GB 이상 여유 공간**을 권장합니다.

## 2. Python과 CUDA를 직접 준비하세요

**[사전 준비 안내](docs/PREREQUISITES.ko.md)** 순서대로 진행하세요.

- Python **3.11 / 64비트**
- NVIDIA 드라이버 **580.65 이상**
- CUDA **13.0** 실행 파일

이미 설치했다면 다시 설치하지 않아도 됩니다.

## 3. Install.cmd를 더블클릭하세요

저장소 폴더 안의 **`Install.cmd`**를 실행합니다. GitHub를 사용한다면 clone한 폴더 또는 **Code → Download ZIP**으로 받은 폴더에서 찾으면 됩니다.

질문이 나오면 아래처럼 선택하세요. **대괄호 안 값이 맞으면 Enter만 누르면 됩니다.**

| 질문 | 처음 설치할 때 |
| --- | --- |
| Python 실행 파일 | 자동으로 찾은 경로가 맞으면 Enter |
| CUDA 폴더 | 사전 준비 안내의 경로 입력 |
| 설치 폴더 | 기본값 유지 |
| 파일 폴더 | 1단계에서 준비한 폴더 지정 |
| 이미지 사용 | 사진을 읽게 하려면 Y |
| 컨텍스트 | **192** 입력 — 한 번에 기억할 수 있는 대화량 |
| LAN 사용 | 이 PC에서만 쓰면 **N**, 다른 PC에서도 접속하면 **Y** |
| 대용량 파일 복사 | **Y** — 복사가 끝나면 외장 SSD를 빼도 됨 |
| 오프라인 wheels | 인터넷이 되면 빈칸으로 Enter |
| OpenCode 자동 병합 | 이 PC의 OpenCode에 연결하려면 **Y** |
| 바탕화면 바로가기 | **Y** |
| 로그인 시 자동 시작 | 원하면 Y |

마지막에 설치 여부를 묻는 질문에 **Y**를 입력하세요. 큰 파일을 복사하고 확인하므로 시간이 걸립니다.

## 4. 시작하고 OpenCode를 여세요

설치가 끝나면 바탕화면의 **Strata Local Start**로 켜고, **Strata Local Stop**으로 끕니다.

OpenCode 자동 병합을 선택했다면 OpenCode를 완전히 종료했다가 다시 열고 **SC117 IQ3_S** 모델을 선택하세요. 다른 PC에서 연결하는 방법은 **[OpenCode 연결 안내](docs/OPENCODE.ko.md)**를 참고하세요.

---

**알아두세요:** Python·CUDA·OpenCode 프로그램은 이 설치기가 대신 설치하지 않습니다. 모델을 새로 받는 기능도 없으며 준비한 파일을 사용합니다. 원본 소스와 라이선스는 저장소에 보존되어 있습니다.

[필수 파일](docs/ASSETS.ko.md) · [사전 준비](docs/PREREQUISITES.ko.md) · [업데이트 방법](docs/UPDATING.ko.md) · [검증 기록](docs/VALIDATION.ko.md) · [라이선스](THIRD_PARTY_NOTICES.md)