#!/usr/bin/env python3
"""
arm_gazebo.launch.py
====================
The official launch file that loads simple_arm in Gazebo
and activates ROS 2 controllers.

Execution:
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

    # Read URDF file
    with open(urdf_path, "r") as f:
        robot_description = f.read()

    # ── 1) Launch Gazebo empty world ──
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("gazebo_ros"),
                "launch", "gazebo.launch.py"
            )
        ),
        launch_arguments={"world": ""}.items(),  # Empty world
    )

    # ── 2) Robot State Publisher (TF Tree) ──
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

    # ── 3) Spawn robot in Gazebo ──
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

    # ── 4) Activate controllers (After spawn is complete) ──
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

    # Sequentially activate controllers after spawning
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
