# OpenCode 연결

Install.cmd에서 **OpenCode 자동 병합 Y**를 선택하면 현재 사용자의 설정을 백업한 뒤 Strata 공급자·기본 모델·compaction만 병합합니다. 다른 공급자와 MCP는 유지합니다. OpenCode 프로그램은 별도 설치해야 합니다.

설치 후 OpenCode를 완전히 종료했다가 다시 열고 **설치한 SC117 양자화** 모델을 고르세요.

생성 파일은 선택한 설치 폴더에 있습니다. 기본 설치 폴더를 사용했다면:

- 이 PC용: `./runtime/clients/Local/opencode.json`
- LAN 접속용: `./runtime/clients/LAN/opencode.json` (LAN 사용을 켠 경우)

LAN PC에서는 LAN용 JSON의 providers.strata·model·compaction을 그 PC의 OpenCode 설정에 병합합니다. REA 같은 MCP는 접속하는 클라이언트에서 따로 구성합니다. 생성된 JSON에는 API 키가 있으므로 공개하지 마세요.

Windows 방화벽 때문에 LAN 접속이 막히면 관리자 PowerShell을 이 저장소 폴더에서 열고 실행하세요:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\Enable-LAN-Firewall.ps1 -Root .\runtime
```

설치 폴더를 바꿨다면 `./runtime`을 그 상대경로로 바꿉니다. 이 규칙은 Private 네트워크 / LocalSubnet에만 해당 포트를 허용합니다.

직접 설정을 편집하려면 Win+R에서 `%USERPROFILE%\.config\opencode`를 열어 opencode.json을 확인하세요. 이미 개인 설정이 있다면 파일 전체를 덮어쓰지 말고 필요한 항목만 병합합니다.
모델별로 설치 폴더와 clients JSON이 다릅니다. 비교할 때 현재 실행한 모델의 JSON을 사용하고, 같은 기본 포트에서는 한 번에 하나만 실행하세요.

## 회사의 기존 config.json에 provider만 추가

기존 설정이 providers가 아닌 provider(단수)를 사용하는 경우에는 V1 형식의 npm/options 항목이 필요합니다. V2의 providers/package/settings를 그대로 이름만 바꾸지 마세요.

새 설치는 clients/Local 및 LAN 폴더에 provider.json과 provider-entry.txt도 생성합니다. 이미 설치했다면 git pull 후 Export-OpenCode-Provider.cmd를 실행하고 설치 폴더를 지정하세요. 모델 다운로드·재설치·서비스 재시작은 필요 없습니다.

provider-entry.txt 전체를 기존 config.json의 provider 객체 안에 추가하세요. 이미 다른 항목이 있다면 사이에 쉼표를 넣습니다. provider.json은 provider 최상위 객체까지 포함한 확인용 JSON입니다. 기존 파일 전체를 덮어쓰지 마세요.

회사에서 쓰는 $schema 주소, 다른 공급자, MCP는 그대로 유지합니다. 파일에는 실제 API 키가 포함되어 있으므로 공개하지 마세요. 추가 후 OpenCode 서버/클라이언트를 재시작하고 모델을 선택합니다. enabled_providers가 있으면 strata도 허용해야 합니다.
