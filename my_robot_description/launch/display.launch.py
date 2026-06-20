#!/usr/bin/env python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import LaunchConfigurationEquals
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_name = "my_robot_description"

    # Locate URDF
    urdf_path = os.path.join(
        get_package_share_directory(package_name), "urdf", "Dynamixel_5DoF.urdf"
    )

    with open(urdf_path, "r") as f:
        robot_description = f.read()

    # Declare launch arguments
    # mode: 'gui' (use manual joint_state_publisher_gui) or 'animate' (run salt shaker animation script)
    mode_arg = DeclareLaunchArgument(
        name="mode",
        default_value="gui",
        choices=["gui", "animate", "handover"],
    )

    # PAD arguments for handover mode (default: baseline [0,0,0])
    pad_p_arg = DeclareLaunchArgument(
        name="P", default_value="0", description="Pleasure (-1~1)"
    )
    pad_a_arg = DeclareLaunchArgument(
        name="A", default_value="0", description="Arousal (-1~1)"
    )
    pad_d_arg = DeclareLaunchArgument(
        name="D", default_value="0", description="Dominance (-1~1)"
    )

    # 1. Robot State Publisher Node (always runs)
    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[{"robot_description": robot_description}],
    )

    # 2. RViz2 Node (always runs with our pre-configured urdf.rviz)
    rviz_config_file = os.path.join(
        get_package_share_directory(package_name), "rviz", "urdf.rviz"
    )
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config_file],
    )

    # 3. GUI Mode: Joint State Publisher GUI Node
    joint_state_publisher_gui_node = Node(
        package="joint_state_publisher_gui",
        executable="joint_state_publisher_gui",
        name="joint_state_publisher_gui",
        output="screen",
        condition=LaunchConfigurationEquals("mode", "gui"),
    )

    # 4. Animate Mode: Runs the custom salt shaker animation script
    animate_script = ExecuteProcess(
        cmd=["python3", "/workspace/tutorials/06_animate_salt_shaker.py"],
        output="screen",
        condition=LaunchConfigurationEquals("mode", "animate"),
    )

    # 5. Handover Mode: Runs the affective handover animation script with PAD args
    handover_script = ExecuteProcess(
        cmd=[
            "python3",
            "/workspace/tutorials/07_affective_handover.py",
            "--pad",
            LaunchConfiguration("P"),
            LaunchConfiguration("A"),
            LaunchConfiguration("D"),
        ],
        output="screen",
        condition=LaunchConfigurationEquals("mode", "handover"),
    )

    return LaunchDescription(
        [
            mode_arg,
            pad_p_arg,
            pad_a_arg,
            pad_d_arg,
            robot_state_publisher_node,
            rviz_node,
            joint_state_publisher_gui_node,
            animate_script,
            handover_script,
        ]
    )
