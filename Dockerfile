FROM osrf/ros:humble-desktop

# Update base packages and install utility tools
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-tk \
    git \
    iputils-ping \
    x11-apps \
    wget \
    curl \
    # Gazebo (Ignition Fortress - Default for ROS 2 Humble)
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-ros2-control \
    ros-humble-ros2-control \
    ros-humble-ros2-controllers \
    ros-humble-joint-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-robot-state-publisher \
    ros-humble-xacro \
    ros-humble-rviz2 \
    ros-humble-controller-manager \
    ros-humble-joint-trajectory-controller \
    ros-humble-forward-command-controller \
    # Build tools
    ros-humble-ament-cmake \
    python3-colcon-common-extensions \
    python3-rosdep \
    # Other utilities
    tmux \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Install Python libraries
RUN pip3 install --no-cache-dir \
    mujoco \
    numpy \
    matplotlib \
    scipy \
    transforms3d

# ROS 2 Environment Configuration (auto-source in bashrc)
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
RUN echo "export GAZEBO_MODEL_PATH=/workspace/models:\$GAZEBO_MODEL_PATH" >> ~/.bashrc
RUN echo "export LIBGL_ALWAYS_INDIRECT=0" >> ~/.bashrc

WORKDIR /workspace
CMD ["/bin/bash"]
