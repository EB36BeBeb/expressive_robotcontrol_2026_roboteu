#!/usr/bin/env python3
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node


def generate_launch_description():
    # Define paths
    workspace = "/workspace"
    default_urdf_path = os.path.join(workspace, "Dynamixel_5DoF.urdf")

    # Launch arguments
    urdf_model_arg = DeclareLaunchArgument(
        name="model",
        default_value=default_urdf_path,
        description="Absolute path to robot URDF file",
    )

    # We will read the URDF file
    # Note: Since the URDF path can be dynamically passed, we use a custom function or read it at start.
    # To keep it simple and robust, we read the default_urdf_path or the one resolved by LaunchConfiguration.
    # Reading it directly in python before launching:

    # Robot State Publisher Node
    # Since robot_description parameter requires the actual URDF content, we can use a command or read it.
    # In ROS 2, we can pass the output of 'xacro' or read the file.
    # Let's read the default file directly, or use xacro to process it dynamically if xacro is installed.
    # Let's check if we can read the file at startup:
    try:
        with open(default_urdf_path, "r") as f:
            robot_description_content = f.read()
    except Exception as e:
        robot_description_content = ""
        print(f"Warning: Could not read default URDF file at {default_urdf_path}: {e}")

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": robot_description_content}],
    )

    # Joint State Publisher GUI Node (so the user can interactively move the joints)
    joint_state_publisher_gui_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher_gui",
        output="screen",
    )

    # RViz2 Node
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        # Optionally pass a config file if available, otherwise starts clean
        # arguments=["-d", rviz_config_file]
    )

    return LaunchDescription(
        [
            urdf_model_arg,
            robot_state_publisher_node,
            joint_state_publisher_gui_node,
            rviz_node,
        ]
    )
