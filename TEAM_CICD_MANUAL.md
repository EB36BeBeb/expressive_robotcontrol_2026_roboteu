# 🤖 ExpressiveRotics 팀 프로젝트 CI/CD 및 Git 협업 매뉴얼

본 매뉴얼은 로봇 개발 팀 프로젝트를 위한 GitHub 설정, 브랜치 보호 규칙, CI/CD 구축 파이프라인 및 워크플로우에 대한 가이드라인을 제공합니다.

---

## 1. 📂 Git 브랜치 전략 (Git Flow)

로봇 분야의 특성상 시뮬레이션 환경 구축과 파이썬/ROS 스크립트 작성에 대한 버전 관리가 중요합니다. 다음과 같은 형태로 브랜치를 운영합니다.

- **`main` (or `master`)**: 항상 실행 가능하고 안정적인 최신 프로젝트 상태를 유지하는 브랜치. 이 브랜치로의 직접 푸시(Push)는 엄격히 금지됩니다.
- **`dev` (Development)**: 기능 개발이 병합(Merge)되는 메인 개발 브랜치. 
- **`feature/<기능명>`**: 터토리얼 개발, 로봇 제어 기능 추가 등을 작업하는 브랜치 (예: `feature/mujoco-ik`, `feature/ros2-publisher`).

### 💡 작업 순서
1. `dev` 브랜치에서 최신 코드를 다운로드 (`git pull origin dev`)
2. 새로운 기능 브랜치 생성 (`git checkout -b feature/새로봇기능`)
3. 작업 완료 후 커밋 및 원격 저장소에 푸시 (`git push origin feature/새로봇기능`)
4. GitHub에서 `dev` 브랜치를 향해 **Pull Request(PR)** 생성
5. 코드 리뷰 및 CI 테스트 통과 확인 후 Merge

---

## 2. 🛡 GitHub 브랜치 보호 설정 (Branch Protection Rules)

`main` 및 `dev` 브랜치의 안정성을 보장하기 위해 GitHub Repository 설정에서 다음 규칙을 활성화해야 합니다.

1. **Settings > Branches > Add branch protection rule** 로 이동
2. **Branch name pattern**에 `main` (그리고 `dev` 도 추가 권장) 입력
3. 다음과 같은 보호 옵션을 체크합니다:
   - ✅ **Require a pull request before merging**: 모든 변경사항은 PR을 통해서만 병합되어야 합니다.
   - ✅ **Require approvals (최소 1명 이상)**: 팀원 중 최소 1명 이상의 승인(Approve)을 받아야 합니다.
   - ✅ **Require status checks to pass before merging**: 빌드(Docker 빌드)와 테스트(Pytest)가 성공적으로 완료되어야 Merge 버튼이 활성화되도록 설정합니다. (**Search** 창에 `build-and-test` 로 Status check 이름을 검색해 추가하세요.)
   - ✅ **Do not allow bypassing the above settings**: 관리자라고 하더라도 강제로 규칙을 무시할 수 없도록 차단합니다.

---

## 3. ⚙️ CI/CD 워크플로우 파이프라인 개요

현재 이 프로젝트에는 `.github/workflows/ci.yml` 파일이 세팅되어 있어 프로젝트가 GitHub에 푸시될 때마다 다음 작업이 자동 실행됩니다.

1. **Docker 컨테이너 빌드 테스트**: 제공된 `Dockerfile`과 `docker-compose.yml`을 이용하여 ROS 2 환경의 도커 이미지가 정상적으로 빌드되는지 검증합니다. 잘못된 종속성으로 인해 도커 이미지가 깨지는 것을 방지합니다.
2. **파이썬 문법 검사 (Linting)**: `flake8`을 사용하여 Python 코드에 심각한 오류(존재하지 않는 변수 사용 등)가 없는지 문법 체크를 진행합니다.
3. **단위 테스트 (PyTest)**: `tests/` 폴더 내부에 정의된 테스트 스크립트들을 자동으로 실행합니다. (현재 `test_ci.py` 가 추가되어 환경을 점검합니다.) 테스트를 통과해야 코드 리뷰어들이 안심하고 코드를 검토할 수 있습니다.

---

## 4. ✅ 팀원들이 지켜야할 추가 사항

1. **테스트 스크립트 작성**: 새로운 파이썬 코드를 추가하면, 해당 코드의 함수가 정상 작동하는지를 검사하는 단위 테스트 코드를 `tests/` 폴더 안쪽에 함께 작성해주세요 (예: `test_kinematics.py`).
2. **이슈(Issue) 관리**: 팀원과 작업을 분담할 때 GitHub Issue를 생성하여 버그 기록, 작업 할당, 진행 상황 체크용으로 활용하세요.
3. **커밋 메시지 규칙 준수**: 다음과 같은 접두사(Prefix) 형태를 맞춰서 남겨주세요.
   - `feat:` (새로운 기능 추가)
   - `fix:` (버그 수정)
   - `docs:` (문서 수정)
   - `test:` (테스트 코드 수정)
   - `refactor:` (코드 리팩토링)
