# 다운로드 연결 오류

GGUF·이미지 인코더·MTP는 **ModelScope**, 엔진은 **GitHub**에서 직접 받습니다. hf-mirror를 사용하지 않습니다.

1. `git pull`로 갱신합니다.
2. Prepare-Models.cmd를 실행하고 같은 다운로드 폴더를 입력합니다.
3. 중단된 파일은 서버가 지원하면 이어받고 완료 후 SHA-256을 검사합니다.
4. 계속 실패하면 File / Source / Redirect / Network failure 줄을 확인하세요.

작은 응답으로 연결만 먼저 확인하려면:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Prepare-Models.ps1 -Probe
```

이 검사는 대용량 모델을 받지 않고 GGUF 4개·이미지 인코더의 실제 데이터 일부, MTP Range 응답, 엔진 주소를 확인합니다. 사용자 PC의 연결은 그 PC에서 검사해야 합니다.

HTTP 프록시를 이미 사용한다면 마법사에 해당 주소를 입력하세요. 사용하지 않으면 Enter를 누릅니다. 브라우저 전용 프록시는 Python에 적용되지 않을 수 있습니다.
