#!/usr/bin/env python3
"""
arm_gazebo.launch.py
====================
Gazebo에서 simple_arm을 로드하고 ROS 2 컨트롤러를 활성화하는
공식 launch 파일입니다.

실행:
    ros2 launch /workspace/launch/arm_gazebo.launch.py
"""

import os
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    RegisterEventHandler,
    TimerAction,
)
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    workspace = "/workspace"
    urdf_path = os.path.join(workspace, "models", "simple_arm.urdf")
    config_path = os.path.join(workspace, "config", "arm_controllers.yaml")

    # URDF 파일 읽기
    with open(urdf_path, "r") as f:
        robot_description = f.read()

    # ── 1) Gazebo 빈 월드 실행 ──
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("gazebo_ros"),
                "launch", "gazebo.launch.py"
            )
        ),
        launch_arguments={"world": ""}.items(),  # 빈 월드
    )

    # ── 2) Robot State Publisher (TF 트리) ──
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[
            {"robot_description": robot_description},
            {"use_sim_time": True},
        ],
    )

    # ── 3) Gazebo에 로봇 스폰 ──
    spawn_entity = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        name="spawn_entity",
        output="screen",
        arguments=[
            "-topic", "robot_description",
            "-entity", "simple_arm",
            "-x", "0.0",
            "-y", "0.0",
            "-z", "0.0",
        ],
    )

    # ── 4) 컨트롤러 활성화 (스폰 완료 후) ──
    load_joint_state_broadcaster = ExecuteProcess(
        cmd=["ros2", "control", "load_controller",
             "--set-state", "active", "joint_state_broadcaster"],
        output="screen",
    )

    load_arm_controller = ExecuteProcess(
        cmd=["ros2", "control", "load_controller",
             "--set-state", "active", "arm_joint_trajectory_controller"],
        output="screen",
    )

    # 스폰 완료 후 컨트롤러 순차 활성화
    activate_after_spawn = RegisterEventHandler(
        OnProcessExit(
            target_action=spawn_entity,
            on_exit=[load_joint_state_broadcaster],
        )
    )
    activate_arm_ctrl_after_jss = RegisterEventHandler(
        OnProcessExit(
            target_action=load_joint_state_broadcaster,
            on_exit=[load_arm_controller],
        )
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
        activate_after_spawn,
        activate_arm_ctrl_after_jss,
    ])
