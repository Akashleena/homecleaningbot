#!/usr/bin/env python3

import math
import time
from typing import List, Tuple

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from lifecycle_msgs.msg import State
from lifecycle_msgs.srv import GetState

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

def wait_for_lifecycle_active(node, lifecycle_node_name: str, timeout_sec: float = 120.0) -> None:
    """
    Block until a lifecycle node reaches ACTIVE state.
    """
    service_name = f"{lifecycle_node_name}/get_state"
    client = node.create_client(GetState, service_name)
    if not client.wait_for_service(timeout_sec=10.0):
        raise RuntimeError(f"Service not available: {service_name}")
    start = node.get_clock().now()
    timeout_ns = int(timeout_sec * 1e9)
    while rclpy.ok():
        req = GetState.Request()
        future = client.call_async(req)
        rclpy.spin_until_future_complete(node, future, timeout_sec=2.0)
        if future.result() is not None:
            current_id = future.result().current_state.id
            current_label = future.result().current_state.label
            if current_id == State.PRIMARY_STATE_ACTIVE:
                print(f"{lifecycle_node_name} is ACTIVE")
                return
            else:
                print(f"Waiting for {lifecycle_node_name}: {current_label}")
        else:
            print(f"Waiting for response from {service_name}...")
        elapsed_ns = (node.get_clock().now() - start).nanoseconds
        if elapsed_ns > timeout_ns:
            raise TimeoutError(f"Timed out waiting for {lifecycle_node_name} to become ACTIVE")
        time.sleep(1.0)
    raise RuntimeError("ROS shutdown while waiting for lifecycle node")

def main() -> None:
    rclpy.init()
    navigator = BasicNavigator()

    # Spawn pose from your diff_drive.launch.py
    # Initial pose should match your spawn pose
    initial_pose = make_pose(navigator, -2.0, -0.6, 0.0)
    navigator.setInitialPose(initial_pose)

    
    # In SLAM mapping mode, wait for slam_toolbox instead of AMCL
    navigator.waitUntilNav2Active(localizer='slam_toolbox')
    
    wait_for_lifecycle_active(navigator, '/planner_server')
    wait_for_lifecycle_active(navigator, '/controller_server')
    wait_for_lifecycle_active(navigator, '/bt_navigator')
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