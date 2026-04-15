#!/bin/bash
source ~/ws_homebot/install/setup.bash

nodes=(
  /planner_server
  /controller_server
  /smoother_server
  /velocity_smoother
  /behavior_server
  /bt_navigator
  /waypoint_follower
)

for n in "${nodes[@]}"; do
  echo "Activating $n"
  ros2 lifecycle set "$n" activate
done