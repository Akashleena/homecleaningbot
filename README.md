<img width="1453" height="451" alt="image" src="https://github.com/user-attachments/assets/ecf68889-ba4b-4b44-9707-3ee01d358fe3" />
<img width="2048" height="1120" alt="image" src="https://github.com/user-attachments/assets/9f71c1d2-96d1-45a6-b445-78475837b925" />

<img width="1466" height="898" alt="image" src="https://github.com/user-attachments/assets/695ba70e-3529-4d2e-8eee-7bb5ec238894" />

ros2 launch homebot_navigation auto_mapping.launch.py use_composition:=False

Then:

ros2 lifecycle get /behavior_server
ros2 lifecycle get /bt_navigator
If both active, you’re done. If not, run only:

ros2 lifecycle set /behavior_server cleanup
ros2 lifecycle set /behavior_server configure
ros2 lifecycle set /behavior_server activate
ros2 lifecycle set /bt_navigator activate
ros2 lifecycle set /waypoint_follower activate
