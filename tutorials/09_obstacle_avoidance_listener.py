#!/usr/bin/env python3
"""
09_obstacle_avoidance_listener.py
=================================
Visualizes the 6-DOF system (Base Rail + 5-DOF Arm).
Subscribes to joint commands, target points, and obstacle points.
"""

import os
import threading

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Point

import mujoco
import mujoco.viewer

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models",
    "simple_arm.xml",
)

JOINT_NAMES = [
    "base_rail",
    "shoulder_pan",
    "shoulder_lift",
    "elbow",
    "wrist_pitch",
    "wrist_roll",
]


class ObstacleAvoidanceListener(Node):
    def __init__(self, model: mujoco.MjModel, data: mujoco.MjData):
        super().__init__("obstacle_avoidance_listener")
        self.model = model
        self.data = data
        self._lock = threading.Lock()

        # Actuator mapping
        self._act_ids = {
            name: mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, f"act_{name}")
            for name in JOINT_NAMES
        }

        # Body mapping for mocap markers
        self.target_mocap_id = model.body_mocapid[
            mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "target")
        ]
        self.obstacle_mocap_id = model.body_mocapid[
            mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "obstacle")
        ]

        # Subscriptions
        self.create_subscription(
            JointState, "/arm/joint_command", self._joint_callback, 10
        )
        self.create_subscription(Point, "/arm/target_point", self._target_callback, 10)
        self.create_subscription(
            Point, "/arm/obstacle_point", self._obstacle_callback, 10
        )

        self.get_logger().info("ObstacleAvoidanceListener (6-DOF) started")

    def _joint_callback(self, msg: JointState):
        with self._lock:
            for i, name in enumerate(msg.name):
                if name in self._act_ids:
                    act_id = self._act_ids[name]
                    if act_id >= 0 and i < len(msg.position):
                        self.data.ctrl[act_id] = msg.position[i]

    def _target_callback(self, msg: Point):
        with self._lock:
            if self.target_mocap_id >= 0:
                self.data.mocap_pos[self.target_mocap_id] = [msg.x, msg.y, msg.z]

    def _obstacle_callback(self, msg: Point):
        with self._lock:
            if self.obstacle_mocap_id >= 0:
                self.data.mocap_pos[self.obstacle_mocap_id] = [msg.x, msg.y, msg.z]

    def step_simulation(self):
        with self._lock:
            mujoco.mj_step(self.model, self.data)


def ros_spin_thread(node):
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()


def main(args=None):
    rclpy.init(args=args)

    if not os.path.exists(MODEL_PATH):
        print(f"Error: {MODEL_PATH} not found")
        return

    model = mujoco.MjModel.from_xml_path(MODEL_PATH)
    data = mujoco.MjData(model)
    node = ObstacleAvoidanceListener(model, data)

    spin_thread = threading.Thread(target=ros_spin_thread, args=(node,), daemon=True)
    spin_thread.start()

    try:
        with mujoco.viewer.launch_passive(model, data) as viewer:
            viewer.cam.distance = 1.5
            viewer.cam.elevation = -20
            while viewer.is_running():
                node.step_simulation()
                viewer.sync()
    except Exception as e:
        print(f"Viewer error: {e}")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
