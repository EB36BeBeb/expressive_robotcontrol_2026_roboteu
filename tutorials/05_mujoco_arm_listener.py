#!/usr/bin/env python3
r"""
05_mujoco_arm_listener.py
=========================
Subscribes to the /arm/joint_command topic and operates the simple_arm model
in the MuJoCo simulator in real-time.

★ Make sure to run the publisher and listener within the same container!
   Terminal 1:  .\start_docker_ros2.bat   ->  python3 tutorials/05_mujoco_arm_listener.py
   Terminal 2:  .\start_docker_ros2.bat   ->  python3 tutorials/04_arm_joint_publisher.py
   (start_docker_ros2.bat executes into the same existing container)
"""

import os
import time
import threading

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from sensor_msgs.msg import JointState

import mujoco
import mujoco.viewer


# Model file path (relative to /workspace mount inside container)
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models",
    "simple_arm.xml",
)

JOINT_NAMES = ["shoulder_pan", "shoulder_lift", "elbow"]


class MuJoCoArmListener(Node):
    """
    ROS 2 Subscriber + MuJoCo Simulator Integration Node.
    Updates MuJoCo actuator targets upon receiving /arm/joint_command messages.
    """

    def __init__(self, model: mujoco.MjModel, data: mujoco.MjData):
        super().__init__("mujoco_arm_listener")
        self.model = model
        self.data = data
        self._lock = threading.Lock()
        self._msg_count = 0

        # Retrieve actuator indices in advance
        self._act_ids = {}
        for name in JOINT_NAMES:
            act_name = f"act_{name}"
            idx = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, act_name)
            self._act_ids[name] = idx
            self.get_logger().info(
                f"  Actuator Mapping: {name} -> act_{name} (idx={idx})"
            )

        self.subscription = self.create_subscription(
            JointState,
            "/arm/joint_command",
            self._joint_command_callback,
            10,
        )

        self.get_logger().info(f"MuJoCoArmListener started - Model: {MODEL_PATH}")
        self.get_logger().info("Subscribed topic: /arm/joint_command")
        self.get_logger().info(
            "★ Run the publisher in another terminal: "
            "python3 tutorials/04_arm_joint_publisher.py"
        )

    # ------------------------------------------------------------------
    def _joint_command_callback(self, msg: JointState):
        """Applies received joint angles to MuJoCo actuators."""
        self._msg_count += 1

        with self._lock:
            for i, name in enumerate(msg.name):
                if name in self._act_ids and i < len(msg.position):
                    act_id = self._act_ids[name]
                    if act_id >= 0:
                        self.data.ctrl[act_id] = msg.position[i]

        # Log output for the first 5 messages and every 100th message thereafter
        if self._msg_count <= 5 or self._msg_count % 100 == 0:
            positions = {n: f"{p:.3f}" for n, p in zip(msg.name, msg.position)}
            self.get_logger().info(f"[Received #{self._msg_count}] {positions}")

    # ------------------------------------------------------------------
    def step_simulation(self):
        """Advances the MuJoCo simulation by one step (called from the viewer loop)."""
        with self._lock:
            mujoco.mj_step(self.model, self.data)


# ======================================================================
def ros_spin_thread(node: MuJoCoArmListener):
    """Executes the ROS 2 event loop in a separate thread."""
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except Exception as e:
        print(f"[ROS Spin Error] {e}")


def main(args=None):
    rclpy.init(args=args)

    # Load MuJoCo Model
    print(f"[MuJoCo] Loading Model: {MODEL_PATH}")
    if not os.path.exists(MODEL_PATH):
        print(f"[ERROR] Model file not found: {MODEL_PATH}")
        print("  -> Current Directory:", os.getcwd())
        print(
            "  -> Files in models/:",
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
                else "(Directory not found)"
            ),
        )
        rclpy.shutdown()
        return

    try:
        model = mujoco.MjModel.from_xml_path(MODEL_PATH)
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        rclpy.shutdown()
        return

    data = mujoco.MjData(model)
    print("[MuJoCo] Model successfully loaded!")
    print(f"  Number of joints: {model.njnt}, Number of actuators: {model.nu}")

    # Create ROS 2 node
    node = MuJoCoArmListener(model, data)

    # Run ROS 2 spin in a separate thread
    spin_thread = threading.Thread(target=ros_spin_thread, args=(node,), daemon=True)
    spin_thread.start()

    # Briefly wait and check topic reception status
    time.sleep(1.0)
    print()
    print("=" * 55)
    print("  MuJoCo Viewer + ROS 2 Listener are ready!")
    print("  Waiting for the /arm/joint_command topic...")
    print()
    print("  ★ Run this command in another terminal:")
    print("    python3 tutorials/04_arm_joint_publisher.py")
    print("=" * 55)
    print()

    # Run MuJoCo viewer (main thread)
    print("[MuJoCo] Starting viewer...")
    print(f"  DISPLAY = {os.environ.get('DISPLAY', '(Not set)')}")

    try:
        with mujoco.viewer.launch_passive(model, data) as viewer:
            viewer.cam.distance = 1.0
            viewer.cam.elevation = -20
            viewer.cam.azimuth = 135

            print("[MuJoCo] Viewer running... (Close window to exit)")
            while viewer.is_running():
                node.step_simulation()
                viewer.sync()
    except Exception as e:
        print(f"[ERROR] Failed to start viewer: {e}")
        print("  Make sure the X server is running.")

    # Cleanup sequence
    print("[Exit] Cleaning up...")
    node.destroy_node()
    rclpy.shutdown()
    print("[Exit] Completed!")


if __name__ == "__main__":
    main()
