#!/usr/bin/env python3
"""
08_obstacle_avoidance_ikpy.py
=============================
Combines 'ikpy' for Forward Kinematics and 'scipy.optimize' for
custom IK with obstacle avoidance.
"""

import os
import math
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Point
from ikpy.chain import Chain
from scipy.optimize import minimize

URDF_PATH = "/workspace/models/simple_arm.urdf"


class IKPyObstacleAvoidance(Node):
    def __init__(self):
        super().__init__("ikpy_obstacle_avoidance")

        if not os.path.exists(URDF_PATH):
            self.get_logger().error(f"URDF not found at {URDF_PATH}!")
            return

        self.chain = Chain.from_urdf_file(URDF_PATH)

        self.joint_pub = self.create_publisher(JointState, "/arm/joint_command", 10)
        self.target_pub = self.create_publisher(Point, "/arm/target_point", 10)
        self.obstacle_pub = self.create_publisher(Point, "/arm/obstacle_point", 10)

        self.timer = self.create_timer(0.1, self.timer_callback)
        self.t = 0.0
        self.current_q = np.zeros(len(self.chain.links))
        self.obstacle_pos = np.array([0.15, 0.08, 0.25])

        self.get_logger().info("IKPy Obstacle Avoidance started")

    def get_all_link_positions(self, q):
        """Returns the 3D positions of all links using ikpy's FK."""
        transformations = self.chain.forward_kinematics(q, full_kinematics=True)
        # Extract (x, y, z) from each 4x4 transformation matrix
        return [t[:3, 3] for t in transformations]

    def inverse_kinematics_with_avoidance(self, target_pos, obstacle_pos, q_guess):
        def objective(q):
            link_positions = self.get_all_link_positions(q)
            ee_pos = link_positions[-1]

            # 1. Distance to Target
            error_cost = np.linalg.norm(ee_pos - target_pos) ** 2

            # 2. Obstacle Avoidance (Penalty for every link)
            avoid_cost = 0.0
            d_safe = 0.18
            for p in link_positions[1:-1]:  # Skip base and EE fixed links
                dist = np.linalg.norm(p - obstacle_pos)
                if dist < d_safe:
                    avoid_cost += 0.5 * (1.0 / dist - 1.0 / d_safe) ** 2

            # 3. Regularization
            reg_cost = 0.001 * np.linalg.norm(q - q_guess) ** 2

            return error_cost + avoid_cost + reg_cost

        # Bounds from ikpy chain
        bounds = []
        for link in self.chain.links:
            if link.bounds is not None:
                bounds.append(link.bounds)
            else:
                bounds.append((-math.pi, math.pi))

        res = minimize(
            objective,
            q_guess,
            method="L-BFGS-B",
            bounds=bounds,
            options={"ftol": 1e-4, "maxiter": 30},
        )
        return res.x

    def timer_callback(self):
        target_x = 0.2 * math.cos(self.t)
        target_y = 0.2 * math.sin(self.t)
        target_z = 0.3
        target_pos = np.array([target_x, target_y, target_z])

        self.current_q = self.inverse_kinematics_with_avoidance(
            target_pos, self.obstacle_pos, self.current_q
        )

        # Publish
        self.target_pub.publish(
            Point(x=float(target_x), y=float(target_y), z=float(target_z))
        )
        self.obstacle_pub.publish(
            Point(
                x=float(self.obstacle_pos[0]),
                y=float(self.obstacle_pos[1]),
                z=float(self.obstacle_pos[2]),
            )
        )

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = [
            "base_rail",
            "shoulder_pan",
            "shoulder_lift",
            "elbow",
            "wrist_pitch",
            "wrist_roll",
        ]
        msg.position = self.current_q[1:7].tolist()
        self.joint_pub.publish(msg)

        self.t += 0.05


def main(args=None):
    rclpy.init(args=args)
    node = IKPyObstacleAvoidance()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
