cmake_minimum_required(VERSION 3.8)
project(homebot_navigation)

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  config
  launch
  maps
  rviz
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/goal_sender.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()