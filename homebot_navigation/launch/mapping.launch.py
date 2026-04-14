import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_homebot_nav = get_package_share_directory('homebot_navigation')
    pkg_bringup = get_package_share_directory('ros_gz_example_bringup')

    open_rviz_arg = DeclareLaunchArgument(
        'open_rviz',
        default_value='true',
        description='Open RViz'
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )

    # Include robot + sim + bridge + EKF bringup
    diff_drive_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_bringup, 'launch', 'diff_drive.launch.py')
        ),
        launch_arguments={
            'rviz': 'false',
        }.items()
    )

    slam_toolbox_launch_path = os.path.join(
        get_package_share_directory('slam_toolbox'),
        'launch',
        'online_async_launch.py'
    )

    slam_params_path = os.path.join(
        pkg_homebot_nav, 'config', 'slam_toolbox_mapping.yaml'
    )

    rviz_config_path = os.path.join(
        pkg_homebot_nav, 'config', 'mapping.rviz'
    )

    slam_toolbox_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(slam_toolbox_launch_path),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'slam_params_file': slam_params_path,
        }.items()
    )

    interactive_marker_node = Node(
        package='interactive_marker_twist_server',
        executable='marker_server',
        name='twist_server_node',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        remappings=[('cmd_vel', '/diff_drive/cmd_vel')],
        output='screen',
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config_path],
        condition=IfCondition(LaunchConfiguration('open_rviz')),
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output='screen'
    )

    return LaunchDescription([
        open_rviz_arg,
        use_sim_time_arg,
        diff_drive_launch,
        rviz_node,
        TimerAction(
            period=10.0,
            actions=[
                slam_toolbox_launch,
                interactive_marker_node,
            ]
        )
    ])