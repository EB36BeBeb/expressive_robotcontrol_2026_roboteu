#!/usr/bin/env python3
"""
06_ik_publisher_ikpy.py
=======================
Uses the 'ikpy' library to solve IK for a 6-DOF robot arm by parsing URDF.
This is much more robust than manual trigonometry.
"""

import os
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Point
from ikpy.chain import Chain

# Path to URDF (relative to workspace root)
URDF_PATH = "/workspace/models/simple_arm.urdf"


class IKPyPublisher(Node):
    def __init__(self):
        super().__init__("ikpy_publisher")

        # 1. Load the robot chain from URDF
        if not os.path.exists(URDF_PATH):
            self.get_logger().error(f"URDF not found at {URDF_PATH}!")
            return

        self.chain = Chain.from_urdf_file(URDF_PATH)
        self.get_logger().info(
            f"Loaded chain: {self.chain.name} with {len(self.chain.links)} links"
        )

        # 2. ROS Publishers
        self.joint_pub = self.create_publisher(JointState, "/arm/joint_command", 10)
        self.target_pub = self.create_publisher(Point, "/arm/target_point", 10)

        self.timer = self.create_timer(0.1, self.timer_callback)
        self.t = 0.0

        # Initial joint positions [rail, pan, lift, elbow, pitch, roll, (EE fixed)]
        # ikpy adds a fixed link for base and EE, so we need to match the size
        self.current_q = [0.0] * len(self.chain.links)

        self.get_logger().info("IKPy Publisher started - URDF based IK")

    def timer_callback(self):
        # 1. Generate Target Position
        radius = 0.2
        target_x = radius * math.cos(self.t)
        target_y = radius * math.sin(self.t)
        target_z = 0.3
        target_pos = [target_x, target_y, target_z]

        self.target_pub.publish(
            Point(x=float(target_x), y=float(target_y), z=float(target_z))
        )

        # 2. Solve IK using ikpy
        # inverse_kinematics returns a list of angles for all links in the chain
        ik_res = self.chain.inverse_kinematics(
            target_pos, initial_position=self.current_q
        )
        self.current_q = ik_res

        # 3. Filter and publish joint states
        # ikpy includes fixed links in its results, we only need the active ones
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()

        # Map ikpy results back to our joint names
        for i, link in enumerate(self.chain.links):
            if (
                link.name != "base_link"
                and "fixed" not in link.name
                and link.name != "end_effector"
            ):
                # We need to find the joint name. In ikpy, it's often the link name.
                # Our URDF joint names: base_rail, shoulder_pan, shoulder_lift, elbow, wrist_pitch, wrist_roll
                if link.name in [
                    "slider_link",
                    "link1",
                    "link2",
                    "link3",
                    "link4",
                    "end_effector",
                ]:
                    # Mapping based on URDF structure
                    pass

        # Simplified mapping for this specific robot
        # [fixed_base, rail, pan, lift, elbow, pitch, roll, fixed_ee]
        msg.name = [
            "base_rail",
            "shoulder_pan",
            "shoulder_lift",
            "elbow",
            "wrist_pitch",
            "wrist_roll",
        ]
        msg.position = ik_res[1:7].tolist()

        self.joint_pub.publish(msg)
        self.t += 0.05


def main(args=None):
    rclpy.init(args=args)
    node = IKPyPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
