# ROS 2 · MuJoCo · Gazebo 개발 환경 가이드

이 저장소는 Docker를 사용하여 **Windows 환경**에서  
**ROS 2 Humble + MuJoCo + Gazebo** 시뮬레이션을 실행하는 환경을 제공합니다.

```
[Publisher] ──/arm/joint_command──► [MuJoCo Viewer]
                                 └──► [Gazebo Bridge] ──► [Gazebo Sim]
```

---

## 📂 프로젝트 구조

**📖 [팀 CI/CD 및 Git 협업 매뉴얼 읽기](TEAM_CICD_MANUAL.md)**

```
Groupwork/
├── Dockerfile                  # ROS2 + Gazebo + MuJoCo 통합 이미지
├── docker-compose.yml          # 컨테이너 설정 (X11 + 공유 메모리)
├── install_vcxsrv.ps1          # Windows X Server 설치 스크립트
├── start_docker_ros2.bat       # Docker 컨테이너 시작 스크립트
├── models/
│   ├── simple_arm.urdf         # 3관절 로봇 팔 (Gazebo용)
│   └── simple_arm.xml          # 3관절 로봇 팔 (MuJoCo용)
├── config/
│   └── arm_controllers.yaml    # Gazebo ros2_control 컨트롤러 설정
├── launch/
│   └── arm_gazebo.launch.py    # Gazebo 전체 런치 파일
└── tutorials/
    ├── 01_publisher.py         # ROS 2 기본 퍼블리셔
    ├── 02_listener.py          # ROS 2 기본 리스너
    ├── 03_mujoco_check.py      # MuJoCo 설치 확인
    ├── 04_arm_joint_publisher.py  # 팔 관절 명령 퍼블리셔 (사인파)
    ├── 05_mujoco_arm_listener.py  # MuJoCo 뷰어 + ROS2 리스너
    ├── 06_gazebo_arm_launch.py    # Gazebo 시뮬레이션 시작 스크립트
    └── 07_full_demo.py            # Gazebo + MuJoCo 동시 연동 데모
```

---

## 🚀 시작하기 전에 (최초 1회)

### 1. VcXsrv (X Server) 설치 및 실행

```powershell
.\install_vcxsrv.ps1
```

**XLaunch 설정:**  
- `Display settings`: Multiple windows, Display number: **-1**  
- `Client startup`: Start no client  
- `Extra settings`: **"Disable access control" 반드시 체크** ✅  

### 2. Windows 방화벽 설정 (관리자 PowerShell)

```powershell
New-NetFirewallRule -DisplayName "VcXsrv (Docker X11)" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 6000
```

### 3. Docker 이미지 빌드

```powershell
docker-compose build
```

> ⚠️ Gazebo 패키지가 추가되어 첫 빌드에 **10~20분** 소요될 수 있습니다.

---

## 🛠️ 컨테이너 실행

```powershell
.\start_docker_ros2.bat
```

새 터미널을 추가로 열려면:

```powershell
docker exec -it groupwork_ros2 /bin/bash
```

---



## 🔍 기본 점검

```bash
# 1. GUI 연결 테스트
xeyes

# 2. MuJoCo 설치 확인
python3 tutorials/03_mujoco_check.py

# 3. MuJoCo 기본 뷰어
python3 -m mujoco.viewer

# 4. Gazebo 버전 확인
gazebo --version
ros2 pkg list | grep gazebo

# 5. 발행 중인 토픽 확인
ros2 topic list
ros2 topic echo /arm/joint_command
```

---

## 🤖 3D Arm 시뮬레이션 (MuJoCo)

```bash
# 터미널 1 - MuJoCo 뷰어 + 리스너 (소프트웨어 렌더링 자동 적용)
python3 tutorials/05_mujoco_arm_listener.py

# 터미널 2 - 관절 명령 퍼블리셔 (사인파 궤적)
python3 tutorials/04_arm_joint_publisher.py --mujoco-only
```

---


## 🏗️ 로봇 팔 구조

```
base_link
  └─[shoulder_pan: Z축 회전 ±180°]─ link1 (0.15m)
      └─[shoulder_lift: Y축 회전 ±90°]─ link2 (0.15m)
          └─[elbow: Y축 회전 ±90°]─ link3 (0.12m)
              └─[fixed]─ end_effector (빨간 구)
```

| 관절 | 축 | 범위 | 설명 |
|------|-----|------|------|
| shoulder_pan  | Z | ±180° | 수평 회전 |
| shoulder_lift | Y | ±90°  | 어깨 들어올리기 |
| elbow         | Y | ±90°  | 팔꿈치 굽힘 |
