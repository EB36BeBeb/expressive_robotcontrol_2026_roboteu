# Mesh Files Directory

Please place the following STL files in this directory:
- `ARM_BODY.stl`
- `ARM_HAND_A.stl`
- `ARM_HAND_B.stl`
- `ARM_JOINT1.stl`
- `ARM_JOINT2.stl`
- `ARM_JOINT3.stl`
- `ARM_JOINT4.stl`
- `ARM_JOINT5.stl`

This package structure is required so that ROS 2 and RViz2 can resolve references like `package://my_robot_description/meshes/stl/...` specified in the URDF.
