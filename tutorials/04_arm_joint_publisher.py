#!/usr/bin/env python3
"""
04_arm_joint_publisher.py
=========================
ROS 2  /arm/joint_command  토픽으로 관절 목표 각도를 발행합니다.
메시지 타입: sensor_msgs/msg/JointState

사용법 (컨테이너 내부):
    python3 tutorials/04_arm_joint_publisher.py

토픽 확인:
    ros2 topic echo /arm/joint_command
"""

import math
import time
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class ArmJointPublisher(Node):
    """3관절 로봇 팔에 사인파 궤적을 발행하는 퍼블리셔."""

    JOINT_NAMES = ["shoulder_pan", "shoulder_lift", "elbow"]

    def __init__(self):
        super().__init__("arm_joint_publisher")

        # /arm/joint_command 에 JointState 메시지 발행
        self.publisher_ = self.create_publisher(JointState, "/arm/joint_command", 10)

        self.timer = self.create_timer(0.05, self.timer_callback)  # 20 Hz
        self.t = 0.0  # 시간 변수

        self.get_logger().info(
            "ArmJointPublisher 시작 – /arm/joint_command 발행 중 (20 Hz)"
        )

    # ------------------------------------------------------------------
    def timer_callback(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.JOINT_NAMES

        # 사인파 궤적: 각 관절이 다른 위상으로 움직입니다
        q0 = math.sin(self.t * 0.5) * math.radians(60)  # shoulder_pan  ±60°
        q1 = math.sin(self.t * 0.4 + 1.0) * math.radians(45)  # shoulder_lift ±45°
        q2 = math.sin(self.t * 0.6 + 2.0) * math.radians(45)  # elbow         ±45°

        msg.position = [q0, q1, q2]
        msg.velocity = []  # 선택 (없어도 됨)
        msg.effort = []

        self.publisher_.publish(msg)
        self.get_logger().info(
            f"[t={self.t:.2f}s]  pan={math.degrees(q0):.1f}° "
            f"lift={math.degrees(q1):.1f}° "
            f"elbow={math.degrees(q2):.1f}°"
        )

        self.t += 0.05


# ======================================================================
def main(args=None):
    rclpy.init(args=args)
    node = ArmJointPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("사용자가 중단했습니다.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
