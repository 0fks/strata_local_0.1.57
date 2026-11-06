# 다운로드 연결 오류

GGUF·이미지 인코더·MTP는 **ModelScope**, 엔진은 **GitHub**에서 직접 받습니다. hf-mirror를 사용하지 않습니다.

1. `git pull`로 갱신합니다.
2. Prepare-Models.cmd를 실행하고 같은 다운로드 폴더를 입력합니다.
3. 중단된 파일은 서버가 지원하면 이어받고 완료 후 SHA-256을 검사합니다.
4. 계속 실패하면 File / Source / Redirect / Network failure 줄을 확인하세요.

**Check-Downloads.cmd를 더블클릭**하면 패키지 설치 없이 모든 다운로드 경로를 검사합니다. FAIL 줄에는 실패한 서버와 오류가 표시됩니다.

명령으로 실행하려면:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Prepare-Models.ps1 -Probe
```

이 검사는 대용량 모델을 받지 않고 GGUF 4개·이미지 인코더의 실제 데이터 일부, MTP Range 응답, 엔진 주소를 확인합니다. 사용자 PC의 연결은 그 PC에서 검사해야 합니다.

HTTP 프록시를 이미 사용한다면 마법사에 해당 주소를 입력하세요. 사용하지 않으면 Enter를 누릅니다. 브라우저 전용 프록시는 Python에 적용되지 않을 수 있습니다.

회사 네트워크에서 timeout이 나면 IT 담당자에게 진단의 FAIL 줄과 접속 허용 요청을 전달하세요. 필요한 서버는 www.modelscope.cn, cdn-lfs-cn-1.modelscope.cn, github.com, release-assets.githubusercontent.com 등이며 실제 리디렉션 서버는 출력에서 확인합니다. 브라우저와 Python은 회사 프록시 적용 방식이 다를 수 있습니다. 프록시 주소·인증 방식은 회사에서 제공하는 설정을 사용하세요.
