# 📘 튜토리얼 상세 가이드

---

## 01 · 기본 Publisher / Subscriber

ROS 2의 핵심 통신 패턴인 **토픽 Pub/Sub**을 배웁니다.

```bash
# 터미널 1
python3 tutorials/01_publisher.py

# 터미널 2
python3 tutorials/02_listener.py
```

**개념**: `MinimalPublisher`가 1초마다 "Hello World: N"을 발행하고,
`MinimalSubscriber`가 수신하여 로그에 출력합니다.

---

## 02 · MuJoCo 설치 확인

```bash
python3 tutorials/03_mujoco_check.py
```

MuJoCo 버전과 간단한 시뮬레이션 스텝 실행을 확인합니다.

---

## 03 · 3D Arm – MuJoCo 시뮬레이션

### 로봇 모델 (`models/simple_arm.xml`)

- **3관절**: shoulder_pan (Z), shoulder_lift (Y), elbow (Y)
- **액추에이터**: Position Servo (kp=50, 목표 위치 제어)
- **센서**: 각 관절 위치 / 속도 측정

### 퍼블리셔 실행

```bash
python3 tutorials/04_arm_joint_publisher.py
```

`/arm/joint_command` 토픽에 `sensor_msgs/JointState` 형태로  
**20Hz** 사인파 궤적을 발행합니다.

| 관절 | 진폭 | 주파수 |
|------|------|--------|
| shoulder_pan  | ±60° | 0.5 rad/s |
| shoulder_lift | ±45° | 0.4 rad/s |
| elbow         | ±45° | 0.6 rad/s |

### MuJoCo 리스너 실행

```bash
python3 tutorials/05_mujoco_arm_listener.py
```

- 토픽을 구독하여 MuJoCo 액추에이터 목표값을 실시간 갱신
- `mujoco.viewer.launch_passive()`로 3D 뷰어 창 표시
- 멀티스레딩: ROS 2 spin ↔ MuJoCo 뷰어 루프 분리

---

## 🛠️ 유용한 ROS 2 명령어

```bash
# 토픽 목록
ros2 topic list

# 토픽 내용 실시간 확인
ros2 topic echo /arm/joint_command

# 퍼블리시 주파수 확인
ros2 topic hz /arm/joint_command

# 컨트롤러 상태
ros2 control list_controllers

# 수동 관절 명령 (Gazebo)
ros2 topic pub /arm_joint_trajectory_controller/joint_trajectory \
  trajectory_msgs/msg/JointTrajectory \
  "{joint_names: ['shoulder_pan','shoulder_lift','elbow'], \
    points: [{positions: [0.5, 0.3, -0.3], \
    time_from_start: {sec: 2, nanosec: 0}}]}"

# RViz2 실행 (관절 시각화)
rviz2
```

---

## ❓ 자주 발생하는 문제

| 증상 | 원인 | 해결 |
|------|------|------|
| MuJoCo 뷰어가 안 뜸 | DISPLAY 미설정 | XLaunch 실행 + `echo $DISPLAY` 확인 |
| `cannot connect to X server` | 방화벽 차단 | 방화벽에 포트 6000 허용 |
| Gazebo slow / crash | 메모리 부족 | `shm_size` 늘리거나 GPU 드라이버 확인 |
| 컨트롤러 활성화 실패 | 스폰 전 실행 | launch 파일 사용 (순서 보장됨) |
| `No such container` | Docker 미실행 | Docker Desktop 시작 후 `.\start_docker_ros2.bat` |
