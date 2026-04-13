import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import TimerAction

def generate_launch_description():

    pkg_homebot_nav = get_package_share_directory('homebot_navigation')

    rviz_launch_arg = DeclareLaunchArgument(
        'rviz', default_value='true',
        description='Open RViz'
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='Use simulation time'
    )

    # SLAM Toolbox launch
    slam_toolbox_launch_path = os.path.join(
        get_package_share_directory('slam_toolbox'),
        'launch',
        'online_async_launch.py'
    )

    slam_params_path = os.path.join(
        pkg_homebot_nav, 'config', 'slam_toolbox_mapping.yaml'
    )

    slam_toolbox_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(slam_toolbox_launch_path),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'slam_params_file': slam_params_path,
        }.items()
    )

    # Interactive marker for moving robot without teleop
    interactive_marker_node = Node(
        package='interactive_marker_twist_server',
        executable='marker_server',
        name='twist_server_node',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        remappings=[('cmd_vel', '/diff_drive/cmd_vel')],
        output='screen',
    )

    # RViz
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        condition=IfCondition(LaunchConfiguration('rviz')),
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        output='screen'
    )

    return LaunchDescription([
        rviz_launch_arg,
        use_sim_time_arg,
        rviz_node,
        TimerAction(
        period=10.0,  # wait 5 seconds for Gazebo to fully initialize
        actions=[
            slam_toolbox_launch,
            interactive_marker_node,
        ]
        )
    ])