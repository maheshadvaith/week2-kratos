import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
from action_msgs.msg import GoalStatus

class MissionClient(Node):

    def __init__(self):
        super().__init__("mission_client")
        # Read waypoints
        self.declare_parameter("waypoint_file", "waypoints.txt")
        file = self.get_parameter("waypoint_file").value


        #Loading waypoints
        self.points = []
        with open(file) as f:
            for line in f:
                if line.startswith("#") or line.strip() == "":
                    continue
                self.points.append(tuple(map(float, line.split())))

        self.i = 0
        self.success = 0

        self.get_logger().info(f"Loaded {len(self.points)} waypoints")

        #COnnecting tot he action server 
        self.client = ActionClient(self, NavigateToPose, "/navigate_to_pose")

        self.get_logger().info("Waiting for Nav2 action server...")
        self.client.wait_for_server()

        self.send_goal()

    def send_goal(self):
        #stopping if all waypoints are done
        if self.i == len(self.points):
            self.get_logger().info(
                f"Mission complete: {self.success}/{len(self.points)} waypoints reached"
            )
            rclpy.shutdown()
            return

        x, y = self.points[self.i]

        self.get_logger().info(
            f"Dispatching waypoint {self.i+1}/{len(self.points)}: x={x:.2f}, y={y:.2f}"
        )
    # creating a navigation goal 
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = "map"
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation.w = 1.0

        future = self.client.send_goal_async(
            goal,
            feedback_callback=self.feedback
        )

        future.add_done_callback(self.goal_response)

    def goal_response(self, future):

        goal_handle = future.result()
# If rejected, move to the next waypoint
        if not goal_handle.accepted:
            self.get_logger().warning("Goal rejected")
            self.i += 1
            self.send_goal()
            return
        #waiting for navigation result
        goal_handle.get_result_async().add_done_callback(self.result)
    #live feedback
    def feedback(self, msg):
        self.get_logger().info(
            f"Feedback: distance remaining = {msg.feedback.distance_remaining:.2f} m"
        )

    def result(self, future):

        if future.result().status == GoalStatus.STATUS_SUCCEEDED:
            self.success += 1
            self.get_logger().info(f"Waypoint {self.i+1} SUCCEEDED")
        else:
            self.get_logger().warning(f"Waypoint {self.i+1} FAILED")

        self.i += 1
        self.send_goal()


def main(args=None):
    rclpy.init(args=args)
    node = MissionClient()
    rclpy.spin(node)


if __name__ == "__main__":
    main()



