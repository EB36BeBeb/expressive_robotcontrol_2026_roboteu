FROM osrf/ros:humble-desktop

# 기본 패키지 업데이트 및 도구 설치
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-tk \
    git \
    iputils-ping \
    x11-apps \
    wget \
    curl \
    # Gazebo (Ignition Fortress - ROS 2 Humble 기본)
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
    # 빌드 도구
    ros-humble-ament-cmake \
    python3-colcon-common-extensions \
    python3-rosdep \
    # 기타 유틸리티
    tmux \
    nano \
    && rm -rf /var/lib/apt/lists/*

# 파이썬 라이브러리 설치
RUN pip3 install --no-cache-dir \
    mujoco \
    numpy \
    matplotlib \
    scipy \
    transforms3d

# ROS 2 환경 설정 (bashrc에 자동 source)
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
RUN echo "export GAZEBO_MODEL_PATH=/workspace/models:\$GAZEBO_MODEL_PATH" >> ~/.bashrc
RUN echo "export LIBGL_ALWAYS_INDIRECT=0" >> ~/.bashrc

WORKDIR /workspace
CMD ["/bin/bash"]
