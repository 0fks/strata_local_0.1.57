# 다운로드 연결 오류

SC117 모델·이미지·MTP는 Hugging Face에서, 엔진은 GitHub에서 받습니다. ModelScope를 사용하지 않습니다.

Check-Downloads.cmd는 Python 패키지를 설치하지 않고 기본 두 모델과 공통 파일의 실제 일부 데이터를 검사합니다. 실패한 서버는 FAIL 줄에 표시됩니다. 세 모델을 모두 검사하려면 Prepare-Models.ps1 -Probe에서 2를 선택하세요.

다운로드가 중단되면 같은 폴더·선택으로 다시 실행합니다. 가능한 경우 이어받고 SHA-256을 검사합니다. 이미 검증된 공통 파일은 다시 받지 않습니다.

회사망 변경 없이 인터넷 되는 PC에서 NVMe에 준비할 수 있습니다. Files ready가 나오면 사용할 PC로 옮겨 Install.cmd에서 실제 경로와 모델을 선택하세요. Python·CUDA·패키지 준비는 별도입니다.
