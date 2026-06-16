#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
import math
import time


class SaltShakerAnimator(Node):
    def __init__(self):
        super().__init__("salt_shaker_animator")
        self.publisher_ = self.create_publisher(JointState, "joint_states", 10)
        self.timer_period = 0.02  # 50 Hz
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        self.start_time = time.time()

        # Joint names matching Dynamixel_5DoF URDF
        self.joint_names = [
            "joint_1",
            "joint_2",
            "joint_3",
            "joint_4",
            "joint_5",
            "joint_a",
            "joint_b",
        ]
        self.get_logger().info(
            "Salt Shaker Animator Node Started! Animating shaking motion..."
        )

    def timer_callback(self):
        t = time.time() - self.start_time

        # Cycle duration: 10 seconds
        # 0s - 3s: Move to food plate
        # 3s - 7s: Shaking salt
        # 7s - 10s: Move back to home position
        cycle_time = t % 10.0

        # Define target joint positions
        # Home positions: all 0.0
        home_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        # Pre-shaking position (hovering over the plate, salt shaker pointing down)
        # We adjust shoulder/elbow/wrist to reach forward and tilt down
        target_pos = [
            2.835,  # joint_1
            0.288,  # joint_2
            1.239,  # joint_3
            -0.119,  # joint_4
            1.544,  # joint_5
            0.899,  # joint_a
            0.00,  # joint_b
        ]

        current_pos = [0.0] * 7

        if cycle_time < 3.0:
            # Phase 1: Interpolate Home -> Target (hover above plate)
            alpha = cycle_time / 3.0
            # Smooth interpolation using cosine profile
            smooth_alpha = (1.0 - math.cos(alpha * math.pi)) / 2.0
            for i in range(7):
                current_pos[i] = home_pos[i] + smooth_alpha * (
                    target_pos[i] - home_pos[i]
                )

        elif cycle_time < 7.0:
            # Phase 2: Shaking salt!
            # Rapidly oscillate joint_3 (elbow) and joint_4 (wrist tilt) to shake the salt
            shake_time = cycle_time - 3.0

            # Oscillate elbow (joint_3) and wrist tilt (joint_4) to mimic shaking salt out
            shake_joint_3 = target_pos[2] + 0.15 * math.sin(35.0 * shake_time)
            shake_joint_4 = target_pos[3] + 0.45 * math.sin(35.0 * shake_time)

            for i in range(7):
                current_pos[i] = target_pos[i]
            current_pos[2] = shake_joint_3
            current_pos[3] = shake_joint_4

        else:
            # Phase 3: Interpolate Target -> Home
            alpha = (cycle_time - 7.0) / 3.0
            smooth_alpha = (1.0 - math.cos(alpha * math.pi)) / 2.0
            for i in range(7):
                current_pos[i] = target_pos[i] + smooth_alpha * (
                    home_pos[i] - target_pos[i]
                )

        # Create JointState message
        msg = JointState()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = current_pos

        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    animator = SaltShakerAnimator()
    try:
        rclpy.spin(animator)
    except KeyboardInterrupt:
        pass
    finally:
        animator.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
