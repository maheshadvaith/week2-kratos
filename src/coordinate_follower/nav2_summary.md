## Navigation workflow

The `mission_client.py` sends a NavigateToPose goal to Nav2 using an action client, which is handled by `send_goal_async(goal)`, you are basically asking the robot to move to x,y.

the goal is sent to the navigator which manages the movement process. It asks the planner server to calculate a path from the robots current position to the goal.

After the path is created, the controller follows it by sending movement commands on `/cmd_vel`. while the robot is moving, feedback is sent to the console such as distance to the goal.

Once the robot reaches the waypoint or the navigation fails, result is sent back to mission client which moves to the next waypoint

Global costmap is used by planner server to find a path across the map. Local costmap is used to avoid nearby obstacles while following that path. local costmap is used by controller server.

Two costmaps are required because planning the overall route and avoiding obstacles are different tasks. GLobal is more long term planning, and local is more short term obstacle avoidance.

