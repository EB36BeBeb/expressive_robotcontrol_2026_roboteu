#!/usr/bin/env python3
"""
05_mujoco_arm_listener.py
=========================
/arm/joint_command 토픽을 구독하고,
MuJoCo 시뮬레이터에서 simple_arm 모델을 실시간으로 구동합니다.

★ 반드시 같은 컨테이너에서 publisher와 listener를 실행하세요!
   터미널 1:  .\start_docker_ros2.bat   →  python3 tutorials/05_mujoco_arm_listener.py
   터미널 2:  .\start_docker_ros2.bat   →  python3 tutorials/04_arm_joint_publisher.py
   (start_docker_ros2.bat 이 동일 컨테이너에 exec 합니다)
"""

import os
import sys
import time
import threading
import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from sensor_msgs.msg import JointState

import mujoco
import mujoco.viewer


# 모델 파일 경로 (컨테이너 내 /workspace 마운트 기준)
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models",
    "simple_arm.xml",
)

JOINT_NAMES = ["shoulder_pan", "shoulder_lift", "elbow"]


class MuJoCoArmListener(Node):
    """
    ROS 2 Subscriber + MuJoCo 시뮬레이터 연동 노드.
    /arm/joint_command 메시지를 받으면 MuJoCo 액추에이터 목표값을 갱신합니다.
    """

    def __init__(self, model: mujoco.MjModel, data: mujoco.MjData):
        super().__init__("mujoco_arm_listener")
        self.model = model
        self.data = data
        self._lock = threading.Lock()
        self._msg_count = 0

        # 액추에이터 인덱스 미리 조회
        self._act_ids = {}
        for name in JOINT_NAMES:
            act_name = f"act_{name}"
            idx = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, act_name)
            self._act_ids[name] = idx
            self.get_logger().info(
                f"  액추에이터 매핑: {name} → act_{name} (idx={idx})"
            )

        self.subscription = self.create_subscription(
            JointState,
            "/arm/joint_command",
            self._joint_command_callback,
            10,
        )

        self.get_logger().info(f"MuJoCoArmListener 시작 – 모델: {MODEL_PATH}")
        self.get_logger().info(f"구독 토픽: /arm/joint_command")
        self.get_logger().info(
            "★ 다른 터미널에서 publisher를 실행하세요: "
            "python3 tutorials/04_arm_joint_publisher.py"
        )

    # ------------------------------------------------------------------
    def _joint_command_callback(self, msg: JointState):
        """수신한 관절 각도를 MuJoCo 액추에이터에 반영."""
        self._msg_count += 1

        with self._lock:
            for i, name in enumerate(msg.name):
                if name in self._act_ids and i < len(msg.position):
                    act_id = self._act_ids[name]
                    if act_id >= 0:
                        self.data.ctrl[act_id] = msg.position[i]

        # 처음 5개 메시지와 이후 100번째마다 로그 출력
        if self._msg_count <= 5 or self._msg_count % 100 == 0:
            positions = {n: f"{p:.3f}" for n, p in zip(msg.name, msg.position)}
            self.get_logger().info(f"[수신 #{self._msg_count}] {positions}")

    # ------------------------------------------------------------------
    def step_simulation(self):
        """MuJoCo 시뮬레이션 한 스텝 진행 (뷰어 루프에서 호출)."""
        with self._lock:
            mujoco.mj_step(self.model, self.data)


# ======================================================================
def ros_spin_thread(node: MuJoCoArmListener):
    """별도 스레드에서 ROS 2 이벤트 루프 실행."""
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except Exception as e:
        print(f"[ROS Spin 오류] {e}")


def main(args=None):
    rclpy.init(args=args)

    # MuJoCo 모델 로드
    print(f"[MuJoCo] 모델 로딩: {MODEL_PATH}")
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] 모델 파일이 없습니다: {MODEL_PATH}")
        print("  → 현재 디렉토리:", os.getcwd())
        print(
            "  → models/ 내 파일:",
            (
                os.listdir(
                    os.path.join(
                        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "models",
                    )
                )
                if os.path.exists(
                    os.path.join(
                        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "models",
                    )
                )
                else "(디렉토리 없음)"
            ),
        )
        rclpy.shutdown()
        return

    try:
        model = mujoco.MjModel.from_xml_path(MODEL_PATH)
    except Exception as e:
        print(f"[ERROR] 모델 로드 실패: {e}")
        rclpy.shutdown()
        return

    data = mujoco.MjData(model)
    print("[MuJoCo] 모델 로드 성공!")
    print(f"  관절 수: {model.njnt}, 액추에이터 수: {model.nu}")

    # ROS 2 노드 생성
    node = MuJoCoArmListener(model, data)

    # ROS 2 스핀을 별도 스레드에서 실행
    spin_thread = threading.Thread(target=ros_spin_thread, args=(node,), daemon=True)
    spin_thread.start()

    # 잠시 대기 후 토픽 수신 상태 확인
    time.sleep(1.0)
    print()
    print("=" * 55)
    print("  MuJoCo 뷰어 + ROS 2 리스너 준비 완료!")
    print("  /arm/joint_command 토픽을 기다리고 있습니다...")
    print()
    print("  ★ 다른 터미널에서 이 명령어를 실행하세요:")
    print("    python3 tutorials/04_arm_joint_publisher.py")
    print("=" * 55)
    print()

    # MuJoCo 뷰어 실행 (메인 스레드)
    print("[MuJoCo] 뷰어를 시작합니다...")
    print(f"  DISPLAY = {os.environ.get('DISPLAY', '(미설정)')}")

    try:
        with mujoco.viewer.launch_passive(model, data) as viewer:
            viewer.cam.distance = 1.0
            viewer.cam.elevation = -20
            viewer.cam.azimuth = 135

            print("[MuJoCo] 뷰어 실행 중... (창을 닫으면 종료)")
            while viewer.is_running():
                node.step_simulation()
                viewer.sync()
    except Exception as e:
        print(f"[ERROR] 뷰어 실행 실패: {e}")
        print("  X server 가 실행 중인지 확인하세요.")

    # 종료 처리
    print("[종료] 클린업 중...")
    node.destroy_node()
    rclpy.shutdown()
    print("[종료] 완료!")


if __name__ == "__main__":
    main()
