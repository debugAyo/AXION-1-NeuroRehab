import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    urdf_file = os.path.join(pkg_dir, 'urdf', 'axion_arm.urdf')
    rviz_file = os.path.join(pkg_dir, 'rviz', 'axion_view.rviz')
    script_file = os.path.join(pkg_dir, 'scripts', 'axion_ros2_node.py')

    with open(urdf_file, 'r') as f:
        robot_description_content = f.read()

    return LaunchDescription([
        # 1. Robot State Publisher (Publishes 3D Robot TF from URDF)
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description_content}]
        ),

        # 2. AXION-1 Arm Controller Node
        Node(
            package='axion_arm',
            executable=script_file,
            name='axion_arm_controller',
            output='screen'
        ),

        # 3. RViz2 3D Visualizer
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_file] if os.path.exists(rviz_file) else []
        )
    ])
