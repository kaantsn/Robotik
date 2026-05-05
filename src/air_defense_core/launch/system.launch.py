import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_dir = get_package_share_directory('air_defense_core')
    rviz_config = os.path.join(pkg_dir, 'rviz', 'tactical.rviz')

    return LaunchDescription([
        Node(package='air_defense_core', executable='rviz_military_sim', output='screen'),
        Node(package='rviz2', executable='rviz2', arguments=['-d', rviz_config], output='screen')
    ])
