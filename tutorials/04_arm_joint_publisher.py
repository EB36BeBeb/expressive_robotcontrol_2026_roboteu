#!/usr/bin/env python3
"""
04_arm_joint_publisher.py
=========================
Publishes target joint angles to the /arm/joint_command topic.
Message type: sensor_msgs/msg/JointState

Usage (Inside the container):
    python3 tutorials/04_arm_joint_publisher.py

To monitor the topic:
    ros2 topic echo /arm/joint_command
"""

import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class ArmJointPublisher(Node):
    """Publisher that generates a sine wave trajectory for a 3-DOF robot arm."""

    JOINT_NAMES = ["shoulder_pan", "shoulder_lift", "elbow"]

    def __init__(self):
        super().__init__("arm_joint_publisher")

        # Publish JointState messages to /arm/joint_command
        self.publisher_ = self.create_publisher(JointState, "/arm/joint_command", 10)

        self.timer = self.create_timer(0.05, self.timer_callback)  # 20 Hz
        self.t = 0.0  # Time variable

        self.get_logger().info(
            "ArmJointPublisher started - Publishing to /arm/joint_command (20 Hz)"
        )

    # ------------------------------------------------------------------
    def timer_callback(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.JOINT_NAMES

        # Sine wave trajectory: each joint moves with a different phase
        q0 = math.sin(self.t * 0.5) * math.radians(60)  # shoulder_pan  ±60°
        q1 = math.sin(self.t * 0.4 + 1.0) * math.radians(45)  # shoulder_lift ±45°
        q2 = math.sin(self.t * 0.6 + 2.0) * math.radians(45)  # elbow         ±45°

        msg.position = [q0, q1, q2]
        msg.velocity = []  # Optional
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
        node.get_logger().info("Interrupted by user.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
