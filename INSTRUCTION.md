# Dynamixel 5DoF URDF 시각화 및 애니메이션 가이드

본 가이드는 `Dynamixel_5DoF` 로봇 모델을 사용하여 ROS 2 환경에서 시각화를 구동하고, 원하는 관절 각도를 수동으로 탐색한 뒤, 이를 바탕으로 소금 뿌리기 등의 애니메이션을 만들고 확인하는 방법을 설명합니다.

---

## 1. 초기 개발 환경 및 GUI 설정 (Windows Host)

Docker 컨테이너 내부에서 구동되는 GUI(RViz2, Joint Slider)를 Windows 호스트 화면에 띄우기 위해 X Server를 시작해야 합니다.

1. **VcXsrv 실행**: 
   PowerShell 터미널에서 아래 스크립트를 실행합니다.
   ```powershell
   .\install_vcxsrv.ps1
   ```
   *   **설정 주의**: 실행 마법사가 나타나면 `Extra settings` 단계에서 **"Disable access control"** 항목을 반드시 체크해야 Docker 컨테이너의 GUI 접속이 허용됩니다.

2. **Docker 컨테이너 시작**:
   Windows 터미널에서 다음 배치 파일을 실행해 컨테이너를 구동하고 접속합니다.
   ```powershell
   .\start_docker_ros2.bat
   ```

---

## 2. 시각화 프로그램 실행 모드 (Docker Container)

새로운 통합 런치 파일인 `display.launch.py`는 두 가지 실행 모드를 지원합니다. 아래 모드 중 원하는 모드를 선택하여 실행할 수 있습니다.

> [!NOTE]
> 패키지 파일을 수정한 후에는 항상 컨테이너 내에서 **패키지를 빌드하고 환경 파일을 소싱**해야 변경사항이 반영됩니다.
> ```bash
> colcon build --packages-select my_robot_description
> source install/setup.bash
> ```

### [모드 1] 수동 관절 조작 모드 (GUI Sliders)
각 관절을 마우스 슬라이더로 직접 조작하거나 **Random**(무작위 관절 생성), **Center**(관절 원점 초기화) 기능으로 테스트해 볼 수 있는 모드입니다. 
이 모드를 사용해 로봇이 요리(접시) 위에서 소금통을 들고 흔들기에 최적화된 관절 위치(라디안 값)를 탐색할 수 있습니다.

*   **실행 명령어**:
    ```bash
    ros2 launch my_robot_description display.launch.py mode:=gui
    ```
    *(또는 `mode` 파라미터를 생략하면 기본값인 `gui` 모드로 동작합니다.)*

### [모드 2] 소금 뿌리기 자동 애니메이션 모드
수정한 궤적 스크립트([06_animate_salt_shaker.py](file:///c:/Users/minsk/ExpressiveRotics/Groupwork/tutorials/06_animate_salt_shaker.py))를 실행하여, 로봇 팔이 자동으로 접시 위로 움직여 소금을 터는 모션을 10초 주기로 무한 반복해 보여주는 모드입니다.

*   **실행 명령어**:
    ```bash
    ros2 launch my_robot_description display.launch.py mode:=animate
    ```

---

## 3. 맞춤형 애니메이션 제작 및 확인 절차

로봇의 동작 각도가 어색할 때, 아래의 절차를 통해 나만의 각도를 찾고 스크립트에 적용해 검증할 수 있습니다.

### Step 1: GUI 모드에서 최적의 각도(라디안) 탐색
1. **수동 조작 모드**(`mode:=gui`)로 시각화 프로그램을 실행합니다.
2. `joint_state_publisher_gui` 창에서 슬라이더를 마우스로 조작하며 아래 위치를 만족하는 각도를 찾습니다:
   *   **대기 위치**: 시작할 때의 안전한 팔 각도
   *   **뿌리기 위치**: 소금통 뚜껑 부분이 접시(빨간 원기둥) 바로 위를 향하도록 손목을 아래로 꺾은 상태의 각도
3. 원하는 각도를 만들었으면, 슬라이더 오른쪽에 표시된 **라디안(Radian) 수치**를 메모해 둡니다. (예: `joint_4: 1.8`, `joint_3: 0.8` 등)

### Step 2: 애니메이션 스크립트 수정
1. 호스트 또는 컨테이너에서 [06_animate_salt_shaker.py](file:///c:/Users/minsk/ExpressiveRotics/Groupwork/tutorials/06_animate_salt_shaker.py) 파일을 엽니다.
2. `timer_callback` 내부에 정의된 목표 관절 리스트(`target_pos`) 변수를 수정합니다:
   ```python
   target_pos = [
       0.0,    # joint_1 (기본 회전)
       -0.4,   # joint_2 (어깨 굽힘)
       0.8,    # joint_3 (팔꿈치)
       1.8,    # joint_4 (손목 틸트) -> 여기서 각도 꺾임 조절
       0.0,    # joint_5 (손목 롤)
       -0.1,   # joint_a (집게 A)
       0.1     # joint_b (집게 B)
   ]
   ```
3. **흔들기 강도와 결 조절**:
   `Phase 2` 영역에서 어떤 관절들을 어떤 주기와 진폭으로 흔들지 수식을 튜닝합니다:
   ```python
   # 35.0은 흔드는 속도(주파수), 0.45는 흔드는 범위(라디안 진폭)를 나타냅니다.
   shake_joint_3 = target_pos[2] + 0.15 * math.sin(35.0 * shake_time)
   shake_joint_4 = target_pos[3] + 0.45 * math.sin(35.0 * shake_time)
   ```

### Step 3: 애니메이션 모드로 즉시 확인
1. 수정한 파이썬 스크립트를 저장합니다.
2. 기존 RViz 터미널에서 `Ctrl + C`를 누르고, 애니메이션 모드로 다시 구동합니다.
   ```bash
   ros2 launch my_robot_description display.launch.py mode:=animate
   ```
3. 바뀐 관절 타겟값과 흔들기 패턴이 의도대로 동작하는지 확인하고, 만족할 때까지 피드백 루프를 반복합니다.
