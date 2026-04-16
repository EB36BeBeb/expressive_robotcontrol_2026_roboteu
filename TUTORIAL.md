# 📘 Detailed Tutorial Guide

---

## 01 · Basic Publisher / Subscriber

Learn **Topic Pub/Sub**, the core communication pattern of ROS 2.

```bash
# Terminal 1
python3 tutorials/01_publisher.py

# Terminal 2
python3 tutorials/02_listener.py
```

**Concept**: `MinimalPublisher` publishes "Hello World: N" every 1 second, and `MinimalSubscriber` receives it to log.

---

## 02 · Check MuJoCo Installation

```bash
python3 tutorials/03_mujoco_check.py
```

Checks the MuJoCo version and confirms a simple simulation step runs correctly.

---

## 03 · 3D Arm – MuJoCo Simulation

### Robot Model (`models/simple_arm.xml`)

- **3 Joints**: shoulder_pan (Z), shoulder_lift (Y), elbow (Y)
- **Actuators**: Position Servo (kp=50, target position control)
- **Sensors**: Joint position / velocity measurements

### Run Publisher

```bash
python3 tutorials/04_arm_joint_publisher.py
```

Publishes a **20Hz** sine wave trajectory to the `/arm/joint_command` topic in `sensor_msgs/JointState` format.

| Joint | Amplitude | Frequency |
|------|------|--------|
| shoulder_pan  | ±60° | 0.5 rad/s |
| shoulder_lift | ±45° | 0.4 rad/s |
| elbow         | ±45° | 0.6 rad/s |

### Run MuJoCo Listener

```bash
python3 tutorials/05_mujoco_arm_listener.py
```

- Subscribes to the topic and updates the target values of MuJoCo actuators in real-time.
- Shows the 3D viewer window using `mujoco.viewer.launch_passive()`.
- Multithreading: ROS 2 spin ↔ MuJoCo viewer loop are running in separate threads.

---

## 🛠️ Useful ROS 2 Commands

```bash
# Topic list
ros2 topic list

# Real-time topic content monitoring
ros2 topic echo /arm/joint_command

# Check publish frequency
ros2 topic hz /arm/joint_command

# Controller states
ros2 control list_controllers

# Manual joint command (Gazebo)
ros2 topic pub /arm_joint_trajectory_controller/joint_trajectory \
  trajectory_msgs/msg/JointTrajectory \
  "{joint_names: ['shoulder_pan','shoulder_lift','elbow'], \
    points: [{positions: [0.5, 0.3, -0.3], \
    time_from_start: {sec: 2, nanosec: 0}}]}"

# Run RViz2 (Joint visualization)
rviz2
```

---

## ❓ Frequently Asked Questions

| Symptom | Cause | Solution |
|------|------|------|
| MuJoCo viewer doesn't open | DISPLAY not set | Run XLaunch + check `echo $DISPLAY` |
| `cannot connect to X server` | Firewall blocking | Allow port 6000 in your firewall |
| Gazebo slow / crash | Insufficient memory | Increase `shm_size` or check GPU drivers |
| Controller activation failed | Executed before spawn | Use launch files (guarantees order) |
| `No such container` | Docker not running | Start Docker Desktop, then `.\start_docker_ros2.bat` |
