"""
Single-command SLAM mapping + scripted Nav2 goals (no RViz goal clicks).

Prerequisite: workspace sourced. After the run, save the map:
  ros2 run nav2_map_server map_saver_cli -f ~/maps/home --ros-args -p use_sim_time:=true
"""
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_nav = get_package_share_directory('homebot_navigation')
    pkg_bringup = get_package_share_directory('ros_gz_example_bringup')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    use_sim_time = LaunchConfiguration('use_sim_time')
    open_rviz = LaunchConfiguration('open_rviz')
    nav2_params = os.path.join(pkg_nav, 'config', 'nav2_params.yaml')
    rviz_config = os.path.join(pkg_nav, 'config', 'mapping.rviz')

    diff_drive_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_bringup, 'launch', 'diff_drive.launch.py')
        ),
        launch_arguments={'rviz': 'false'}.items(),
    )

    nav2_slam_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'slam': 'True',
            'map': '',
            'use_sim_time': use_sim_time,
            'params_file': nav2_params,
            'autostart': 'True',
            'use_composition': 'True',
            'use_respawn': 'False',
        }.items(),
    )

    # Nav2 publishes /cmd_vel; Gazebo bridge expects /diff_drive/cmd_vel
   
    cmd_vel_relay = ExecuteProcess(
    cmd=['ros2', 'run', 'topic_tools', 'relay', '/cmd_vel_smoothed', '/diff_drive/cmd_vel'],
    output='screen',
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        condition=IfCondition(open_rviz),
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen',
    )

    goal_sender = ExecuteProcess(
        cmd=['ros2', 'run', 'homebot_navigation', 'goal_sender.py'],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument('open_rviz', default_value='true'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        diff_drive_launch,
        nav2_slam_bringup,
        cmd_vel_relay,
        rviz_node,
        TimerAction(period=25.0, actions=[goal_sender]),
    ])