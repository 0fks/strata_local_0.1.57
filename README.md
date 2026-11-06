# strata_local

검증한 Strata를 새 Windows PC에 설치하는 개인용 독립 저장소입니다. 원본 Strata 소스는 `vendor/strata`에 직접 보관합니다. 원본 GitHub가 없어져도 이 저장소와 미리 준비한 설치 자산으로 재설치할 수 있습니다.

현재 기준: 소스 `9f7d977d` / 엔진 **0.1.57 CUDA13** / SC117 IQ3_S / CPU 이미지 / 192K. Ryzen 5700X·96GB RAM·RTX 5070 Ti에서 검증한 프로필입니다. 다른 하드웨어에 자동으로 최적화되는 범용 설치기는 아닙니다.

## 새 PC에서

1. **Python·CUDA·NVIDIA 드라이버는 직접 설치**합니다. [준비 방법](docs/PREREQUISITES.ko.md).
2. 외장 SSD/NAS 등에서 대용량 파일을 준비합니다. [필수 파일·폴더와 출처](docs/ASSETS.ko.md).
3. 이 저장소를 clone하고 **Install.cmd를 더블클릭**합니다.
4. 질문에 따라 경로, 컨텍스트, 이미지와 LAN 사용 여부를 선택합니다.
5. 설치가 끝나면 생성된 OpenCode JSON을 적용합니다. [OpenCode 연결](docs/OPENCODE.ko.md).

설치 마법사에서 선택하는 항목:

| 항목 | 선택 |
| --- | --- |
| Python / CUDA | 직접 설치한 실행 파일·DLL 폴더 |
| 대용량 파일 | 모델·pack·MTP·엔진·이미지 인코더 폴더 각각 지정 |
| 컨텍스트 | 64K / 128K / **192K 검증값** / 256K |
| 이미지 | CPU 8스레드 사용 또는 끄기 |
| LAN | 끄기(기본) / 켜기 + 실제 IP·포트 |
| 파일 배치 | 설치 폴더로 복사 / 지정한 경로에서 그대로 사용 |
| OpenCode | JSON만 생성 / 기존 설정에 백업 후 병합 |
| 실행 편의 | 별도 이름의 바탕화면 아이콘 / 로그인 자동 시작 |
| Python 패키지 | 로컬 wheels / PyPI 다운로드 |

설정은 Git에서 제외되는 `settings.local.json`에 저장됩니다. 경로만 바꾸고 다시 실행할 수 있습니다.

```powershell
# 설정 파일로 설치 전 검사만
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install.ps1 -UseSettings -PlanOnly

# 설정 파일로 설치
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install.ps1 -UseSettings
```

Plan은 파일 존재·크기·엔진 manifest를 확인합니다. 전체 모델 해시는 실제 설치 때 검사하므로 80GB 이상을 읽는 시간이 필요합니다. 서버는 설치 후 사용자가 시작을 선택하기 전까지 실행하지 않습니다. 다른 모델 서버를 이미 사용하는 PC에서는 새 서버를 동시에 시작하지 마세요.

## 저장소와 설치 결과

```text
vendor/strata/             원본에 등록된 소스 스냅샷, 원본 LICENSE 포함
scripts/strata_local.py    검증·설치·설정 생성·안전한 시작/종료
manifests/                고정 버전·파일명·크기·SHA-256
settings.example.json     비밀값 없는 경로/선택 예시
tests/                    배포 도구 검사
docs/                     준비·OpenCode·업데이트 안내
```

기본 설치 위치는 `%LOCALAPPDATA%\StrataLocal`입니다. 소스·가상환경·서버 설정·로그·OpenCode JSON이 그 안에 생성됩니다. 복사를 선택하면 모델도 이 위치로 복사됩니다. 모델 폴더를 그대로 사용하는 경우 그 원본 위치를 계속 연결해 두어야 합니다. 설치 후 원본 경로가 사라지면 모델을 시작할 수 없습니다.

기존 설치 폴더를 덮어쓰는 업데이트는 거부합니다. 새 설치 폴더에서 검증 후 전환하세요. 이 프로젝트는 현재 운영 중인 별도 `D:\Git\Strata` 설치를 자동 변경하지 않습니다.

## 개인정보·라이선스

실제 API 키·사용자 설정·세션·로그·대용량 모델·Python·CUDA·엔진은 Git에 넣지 않습니다. 설치할 때 새 API 키 5개를 생성하고 설치 폴더에 접근 제한을 적용합니다. OpenCode JSON에도 키가 들어가므로 개인적으로 보관하세요.

원본 MIT 고지와 라이선스는 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 및 [LICENSE](LICENSE)에 보존했습니다. 원본 프로젝트의 공개 테스트·벤치마크 자료는 소스 스냅샷 일부이며 이 PC에서 만든 개인 실험 결과가 아닙니다. 모델·CUDA 등의 별도 라이선스는 각 배포물의 고지를 확인해야 합니다.

## 검증과 업데이트

```powershell
py -3.11 -m unittest discover -s tests -v
```

설치 시험 및 공개 전 검사는 [검증 기록](docs/VALIDATION.ko.md), 향후 원본 변경 반영은 [업데이트 절차](docs/UPDATING.ko.md)를 참고하세요. 소스 버전을 자동으로 latest에 맞추지 않습니다.
