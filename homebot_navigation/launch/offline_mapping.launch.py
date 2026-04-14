import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_nav = get_package_share_directory('homebot_navigation')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    open_rviz = LaunchConfiguration('open_rviz')
    use_sim_time = LaunchConfiguration('use_sim_time')

    nav2_params = os.path.join(pkg_nav, 'config', 'nav2_params.yaml')
    rviz_config = os.path.join(pkg_nav, 'config', 'mapping.rviz')

    base_mapping_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav, 'launch', 'mapping.launch.py')
        ),
        launch_arguments={
            'open_rviz': 'false',
            'use_sim_time': use_sim_time,
        }.items()
    )

    nav2_slam_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'slam': 'True',
            'use_localization': 'False',
            'map': '',
            'use_sim_time': use_sim_time,
            'params_file': nav2_params,
            'autostart': 'True',
        }.items()
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('open_rviz', default_value='true'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        base_mapping_launch,
        nav2_slam_bringup,
        rviz_node,
    ])