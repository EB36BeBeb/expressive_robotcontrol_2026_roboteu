# ROS 2 · MuJoCo · Gazebo Development Environment Guide

This repository provides a Docker-based environment for running **ROS 2 Humble + MuJoCo + Gazebo** simulations on Windows.

```
[Publisher] ──/arm/joint_command──► [MuJoCo Viewer]
                                 └──► [Gazebo Bridge] ──► [Gazebo Sim]
```

---

## 📂 Project Structure

**📖 [Read the Team CI/CD & Git Collaboration Manual](TEAM_CICD_MANUAL.md)**

```
Groupwork/
├── Dockerfile                  # ROS2 + Gazebo + MuJoCo integrated image
├── docker-compose.yml          # Container settings (X11 + Shared memory)
├── install_vcxsrv.ps1          # Windows X Server installation script
├── start_docker_ros2.bat       # Docker container start script
├── models/
│   ├── simple_arm.urdf         # 3-DOF robot arm (for Gazebo)
│   └── simple_arm.xml          # 3-DOF robot arm (for MuJoCo)
├── config/
│   └── arm_controllers.yaml    # Gazebo ros2_control controller settings
├── launch/
│   └── arm_gazebo.launch.py    # Gazebo main launch file
└── tutorials/
    ├── 01_publisher.py         # ROS 2 basic publisher
    ├── 02_listener.py          # ROS 2 basic listener
    ├── 03_mujoco_check.py      # MuJoCo installation check
    ├── 04_arm_joint_publisher.py  # Arm joint command publisher (sine wave)
    ├── 05_mujoco_arm_listener.py  # MuJoCo viewer + ROS2 listener
    ├── 06_gazebo_arm_launch.py    # Gazebo simulation start script
    └── 07_full_demo.py            # Gazebo + MuJoCo full integration demo
```

---

## 🚀 Before Getting Started (First time only)

### 1. Install and run VcXsrv (X Server)

```powershell
.\install_vcxsrv.ps1
```

**XLaunch configuration:**  
- `Display settings`: Multiple windows, Display number: **-1**  
- `Client startup`: Start no client  
- `Extra settings`: **MUST check "Disable access control"** ✅  

### 2. Windows Firewall Configuration (Administrator PowerShell)

```powershell
New-NetFirewallRule -DisplayName "VcXsrv (Docker X11)" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 6000
```

### 3. Build Docker Image

```powershell
docker-compose build
```

> ⚠️ As Gazebo packages are included, the first build may take **10~20 minutes**.

---

## 🛠️ Run Container

```powershell
.\start_docker_ros2.bat
```

To open a new terminal side-by-side:

```powershell
docker exec -it groupwork_ros2 /bin/bash
```

---

## 🔍 Basic Checks

```bash
# 1. Test GUI connectivity
xeyes

# 2. Check MuJoCo installation
python3 tutorials/03_mujoco_check.py

# 3. MuJoCo basic viewer
python3 -m mujoco.viewer

# 4. Check Gazebo version
gazebo --version
ros2 pkg list | grep gazebo

# 5. Check publishing topics
ros2 topic list
ros2 topic echo /arm/joint_command
```

---

## 🤖 3D Arm Simulation (MuJoCo)

```bash
# Terminal 1 - MuJoCo viewer + listener (software rendering applied automatically)
python3 tutorials/05_mujoco_arm_listener.py

# Terminal 2 - Joint command publisher (sine wave trajectory)
python3 tutorials/04_arm_joint_publisher.py --mujoco-only
```

---

## 🏗️ Robot Arm Structure

```
base_link
  └─[shoulder_pan: Z axis rot ±180°]─ link1 (0.15m)
      └─[shoulder_lift: Y axis rot ±90°]─ link2 (0.15m)
          └─[elbow: Y axis rot ±90°]─ link3 (0.12m)
              └─[fixed]─ end_effector (Red sphere)
```

| Joint | Axis | Range | Description |
|------|-----|------|------|
| shoulder_pan  | Z | ±180° | Horizontal pan |
| shoulder_lift | Y | ±90°  | Shoulder lift |
| elbow         | Y | ±90°  | Elbow bend |
