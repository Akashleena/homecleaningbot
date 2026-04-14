#!/usr/bin/env python3

import math
import time
from typing import List, Tuple

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult


def make_pose(navigator: BasicNavigator, x: float, y: float, yaw: float) -> PoseStamped:
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = x
    pose.pose.position.y = y
    pose.pose.position.z = 0.0

    half_yaw = yaw / 2.0
    pose.pose.orientation.z = math.sin(half_yaw)
    pose.pose.orientation.w = math.cos(half_yaw)
    return pose


def main() -> None:
    rclpy.init()
    navigator = BasicNavigator()

    # Spawn pose from your diff_drive.launch.py
    # Initial pose should match your spawn pose
    initial_pose = make_pose(navigator, -2.0, -0.6, 0.0)
    navigator.setInitialPose(initial_pose)

    # In SLAM mapping mode, wait for slam_toolbox instead of AMCL
    navigator.waitUntilNav2Active(localizer='slam_toolbox')
    # First-pass route through both rooms and doorway
    goals: List[Tuple[float, float, float]] = [
        (-2.2, -1.8, 0.0),
        (-2.2,  1.6, 1.57),
        (-0.8,  0.0, 0.0),
        ( 0.8, -0.2, 0.0),
        ( 1.6, -0.7, 0.0),
        ( 2.8, -1.2, 0.0),
        ( 3.0,  1.4, 1.57),
        ( 1.8,  1.2, 3.14),
    ]

    for i, (x, y, yaw) in enumerate(goals, start=1):
        goal_pose = make_pose(navigator, x, y, yaw)
        navigator.goToPose(goal_pose)

        while not navigator.isTaskComplete():
            time.sleep(0.2)

        result = navigator.getResult()

        if result == TaskResult.SUCCEEDED:
            print(f'Goal {i} succeeded: x={x}, y={y}, yaw={yaw}')
        elif result == TaskResult.CANCELED:
            print(f'Goal {i} canceled')
            break
        elif result == TaskResult.FAILED:
            print(f'Goal {i} failed: x={x}, y={y}, yaw={yaw}')
        else:
            print(f'Goal {i} returned unknown result')

    print('All goals processed.')
    rclpy.shutdown()


if __name__ == '__main__':
    main()