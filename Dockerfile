FROM osrf/ros:humble-desktop

# Find and comment out the problematic dpkg hook wherever it exists
RUN find /etc/dpkg -type f -exec sed -i 's/.*pkg-config-dpkghook.*/# \0/g' {} + && \
    rm -f /usr/share/pkg-config-dpkghook

# 1. Update and install essential tools to stabilize dpkg
RUN rm -f /etc/apt/apt.conf.d/docker-clean && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    apt-utils

# 2. Install the rest of the utility tools and ROS packages
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    python3-pip \
    python3-tk \
    git \
    iputils-ping \
    x11-apps \
    wget \
    curl \
    # Basic ROS 2 packages (Reverted from MoveIt)
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-ros2-control \
    ros-humble-ros2-control \
    ros-humble-ros2-controllers \
    ros-humble-joint-state-publisher \
    ros-humble-robot-state-publisher \
    ros-humble-xacro \
    ros-humble-rviz2 \
    # Build tools
    ros-humble-ament-cmake \
    python3-colcon-common-extensions \
    python3-rosdep \
    # Other utilities
    tmux \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Install Python libraries
RUN python3 -m pip install --no-cache-dir --upgrade pip --progress-bar off && \
    python3 -m pip install --no-cache-dir --progress-bar off \
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
