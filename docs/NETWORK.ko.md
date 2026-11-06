# 다운로드 연결 오류

현재 기본 모델은 SC117 IQ3_S입니다. 모델·이미지 인코더는 Hugging Face, MTP는 ModelScope, 엔진은 GitHub에서 받습니다.

Check-Downloads.cmd를 실행하면 Python 패키지 설치 없이 연결을 검사하며 실패한 서버를 FAIL 줄에 표시합니다.

외부 PC에서 NVMe에 준비할 경우 회사 네트워크 설정을 변경할 필요가 없습니다. 인터넷이 되는 PC에서 Prepare-Models.cmd를 완료한 뒤 NVMe를 연결해 Install.cmd에서 실제 경로를 지정하세요.

다운로드가 중단되면 같은 폴더로 다시 실행하세요. 지원되는 경우 이어받고 SHA-256을 검사합니다. 모델 다운로드를 위한 회사망 연결과 Python 패키지 설치에 필요한 연결은 별개입니다.

특정 미러를 사용하려면 Prepare-Models.ps1의 -Mirror 인수에 주소를 지정할 수 있습니다. 미러가 동일한 원본 CDN으로 리디렉션할 수 있어 연결을 보장하지는 않습니다.
