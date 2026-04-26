#!/usr/bin/env python3
"""
07_ik_listener.py
=================
Subscribes to joint commands and target points, visualizing them in MuJoCo.
- Moves the 5-DOF arm based on /arm/joint_command.
- Moves a red sphere marker based on /arm/target_point.
"""

import os
import threading
import numpy as np

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
    "shoulder_pan",
    "shoulder_lift",
    "elbow",
    "wrist_pitch",
    "wrist_roll",
]


class MuJoCoIKListener(Node):
    def __init__(self, model: mujoco.MjModel, data: mujoco.MjData):
        super().__init__("mujoco_ik_listener")
        self.model = model
        self.data = data
        self._lock = threading.Lock()

        # Actuator mapping
        self._act_ids = {}
        for name in JOINT_NAMES:
            act_name = f"act_{name}"
            idx = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, act_name)
            self._act_ids[name] = idx

        # Subscriptions
        self.joint_sub = self.create_subscription(
            JointState, "/arm/joint_command", self._joint_callback, 10
        )
        self.target_sub = self.create_subscription(
            Point, "/arm/target_point", self._target_callback, 10
        )

        # Target body index
        self.target_body_id = mujoco.mj_name2id(
            model, mujoco.mjtObj.mjOBJ_BODY, "target"
        )
        self.mocap_id = model.body_mocapid[self.target_body_id]

        self.get_logger().info("MuJoCoIKListener started")

    def _joint_callback(self, msg: JointState):
        with self._lock:
            for i, name in enumerate(msg.name):
                if name in self._act_ids and i < len(msg.position):
                    act_id = self._act_ids[name]
                    if act_id >= 0:
                        self.data.ctrl[act_id] = msg.position[i]

    def _target_callback(self, msg: Point):
        with self._lock:
            if self.mocap_id >= 0:
                self.data.mocap_pos[self.mocap_id] = [msg.x, msg.y, msg.z]

    def step_simulation(self):
        with self._lock:
            mujoco.mj_step(self.model, self.data)

            # Compute distance between EE and target for visual feedback
            ee_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_SITE, "ee_site")
            ee_pos = self.data.site_xpos[ee_id]
            target_pos = self.data.mocap_pos[self.mocap_id]
            dist = np.linalg.norm(ee_pos - target_pos)

            if (
                self.get_clock().now().nanoseconds % 10**9 < 10**8
            ):  # Log roughly once per sec
                self.get_logger().info(f"Distance to target: {dist:.4f}m", once=False)


def ros_spin_thread(node):
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()


def main(args=None):
    rclpy.init(args=args)

    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model file not found at {MODEL_PATH}")
        return

    model = mujoco.MjModel.from_xml_path(MODEL_PATH)
    data = mujoco.MjData(model)
    node = MuJoCoIKListener(model, data)

    spin_thread = threading.Thread(target=ros_spin_thread, args=(node,), daemon=True)
    spin_thread.start()

    try:
        with mujoco.viewer.launch_passive(model, data) as viewer:
            viewer.cam.distance = 1.2
            viewer.cam.elevation = -30
            while viewer.is_running():
                node.step_simulation()
                viewer.sync()
    except Exception as e:
        print(f"Viewer Error: {e}")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
