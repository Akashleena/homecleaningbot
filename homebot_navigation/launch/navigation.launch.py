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
    pkg_bringup = get_package_share_directory('ros_gz_example_bringup')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    open_rviz = LaunchConfiguration('open_rviz')
    use_sim_time = LaunchConfiguration('use_sim_time')
    map_file = LaunchConfiguration('map')

    nav2_params = os.path.join(pkg_nav, 'config', 'nav2_params.yaml')
    rviz_config = os.path.join(pkg_nav, 'config', 'mapping.rviz')

    diff_drive_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_bringup, 'launch', 'diff_drive.launch.py')
        ),
        launch_arguments={
            'rviz': 'false',
        }.items()
    )

    nav2_localization_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'slam': 'False',
            'use_localization': 'True',
            'map': map_file,
            'use_sim_time': use_sim_time,
            'params_file': nav2_params,
            'autostart': 'True',
        }.items()
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        condition=IfCondition(open_rviz),
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument('open_rviz', default_value='true'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument(
            'map',
            default_value='/home/aleenatron/ws_homebot/maps/test_map.yaml'
        ),
        diff_drive_launch,
        nav2_localization_bringup,
        rviz_node,
    ])