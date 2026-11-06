# OpenCode 연결

설치 마법사에서 컨텍스트·이미지·LAN을 선택하면 같은 값을 반영한 OpenCode V2 JSON을 만듭니다.

- 로컬: `<설치폴더>\clients\Local\opencode.json`, `127.0.0.1` 사용.
- LAN 켠 경우: `<설치폴더>\clients\LAN\opencode.json`, 사용자가 입력한 실제 서버 IP 사용.
- LAN을 끄면 외부 PC용 파일은 생성하지 않습니다.
- 이미지 사용 시 input에 text/image, 끄면 text만 표시합니다.
- 서버와 클라이언트 모델 ID·컨텍스트를 함께 맞춥니다. 클라이언트 출력 한도 16384, 자동 compaction buffer 24576 / keep.tokens 8000.

로컬 설정을 자동 병합하도록 선택하면 `%USERPROFILE%\.config\opencode\opencode.json`을 먼저 백업하고 `providers.strata`, 기본 `model`, `compaction`만 변경합니다. 기존 다른 공급자·MCP·권한은 보존합니다. `.jsonc`를 직접 쓰는 환경은 자동 병합 대신 수동 병합하세요. 잘못된 기존 JSON을 만나면 덮어쓰지 않고 실패합니다.

LAN PC에서는 그 PC의 사용자 설정에 LAN용 JSON의 해당 항목을 병합하세요. REA 같은 MCP는 접속하는 클라이언트 PC에서 별도로 구성합니다. 서버 PC의 REA 경로를 원격 PC에 복사하지 않습니다. 설치기는 OpenCode 프로그램 자체를 설치하지 않습니다.

LAN에 TCP 포트를 허용해야 한다면 관리자 PowerShell에서 실행합니다:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Enable-LAN-Firewall.ps1 -Root C:\StrataLocal
```

이 helper는 선택한 포트를 Private 네트워크 / LocalSubnet에만 허용하고 기존 같은 이름 규칙은 덮어쓰지 않습니다. 실제 네트워크 프로필과 서브넷을 확인하세요. Git 저장소의 서버 예시 IP를 그대로 사용하는 방식이 아닙니다.

API 키는 새 설치마다 5개 생성됩니다. 설치 폴더의 `api-keys.private.json`과 생성된 클라이언트 JSON은 비밀 파일입니다. 이 저장소에는 기존 PC의 실제 API 키가 들어 있지 않습니다.
