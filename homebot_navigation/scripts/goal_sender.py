#!/usr/bin/env python3

import math
import time
from typing import List, Tuple
from datetime import datetime
from pathlib import Path
import rclpy
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

LOG_PATH = Path.home() / "ws_homebot" / "goal_results.log"


def log_line(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line, flush=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")


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


def publish_initial_pose(
    navigator: BasicNavigator, x: float, y: float, yaw: float, repeats: int = 3
) -> None:
    pub = navigator.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)
    half_yaw = yaw / 2.0

    for _ in range(repeats):
        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = 'map'
        msg.header.stamp = navigator.get_clock().now().to_msg()
        msg.pose.pose.position.x = x
        msg.pose.pose.position.y = y
        msg.pose.pose.position.z = 0.0
        msg.pose.pose.orientation.z = math.sin(half_yaw)
        msg.pose.pose.orientation.w = math.cos(half_yaw)
        msg.pose.covariance = [
            0.25, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.25, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0685,
        ]
        pub.publish(msg)
        time.sleep(0.3)


def main() -> None:
    rclpy.init()
    navigator = BasicNavigator()

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    log_line("===== NEW RUN STARTED =====")

    # Initial pose
    spawn_x, spawn_y, spawn_yaw = -2.0, -0.6, 0.0
    log_line(f"INITIAL_POSE x={spawn_x:.3f} y={spawn_y:.3f} yaw={spawn_yaw:.3f}")

    initial_pose = make_pose(navigator, spawn_x, spawn_y, spawn_yaw)
    navigator.setInitialPose(initial_pose)
    publish_initial_pose(navigator, spawn_x, spawn_y, spawn_yaw)

    log_line("WAITING_FOR_NAV2")
    navigator.waitUntilNav2Active(localizer='slam_toolbox')
    time.sleep(2.0)
    log_line("NAV2_ACTIVE")

    goals: List[Tuple[float, float, float]] = [
        (0.6,  0.0,  0.0),
        (0.8,  0.0,  0.0),
        (1.0,  0.0,  0.0),
        (1.0,  0.2,  0.0),
        (0.8,  0.2,  0.0),
        (0.6,  0.1,  0.0),
    ]

    for i, (x, y, yaw) in enumerate(goals, start=1):
        goal_pose = make_pose(navigator, x, y, yaw)

        log_line(f"START goal={i} x={x:.3f} y={y:.3f} yaw={yaw:.3f}")
        navigator.goToPose(goal_pose)

        start_time = time.time()

        while not navigator.isTaskComplete():
            time.sleep(0.2)

        elapsed = time.time() - start_time
        result = navigator.getResult()

        if result == TaskResult.SUCCEEDED:
            log_line(f"SUCCESS goal={i} x={x:.3f} y={y:.3f} yaw={yaw:.3f} elapsed={elapsed:.2f}s")
        elif result == TaskResult.CANCELED:
            log_line(f"CANCELED goal={i} elapsed={elapsed:.2f}s")
            break
        elif result == TaskResult.FAILED:
            log_line(f"FAILED goal={i} x={x:.3f} y={y:.3f} yaw={yaw:.3f} elapsed={elapsed:.2f}s")
        else:
            log_line(f"UNKNOWN goal={i} result={result}")

    log_line("===== RUN FINISHED =====")
    rclpy.shutdown()


if __name__ == '__main__':
    main()