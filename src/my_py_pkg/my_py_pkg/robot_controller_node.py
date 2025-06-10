import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
from time import time

class WaypointFollower(Node):
    def __init__(self):
        super().__init__('waypoint_follower')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.timer = self.create_timer(0.1, self.navigate)

        # Corrija se o odom inicia em 0,0 no Stage
        self.odom_offset = (-7.0, -7.0)
        self.position = (-7.0, -7.0)
        self.yaw = 0.0
        self.linear_velocity = 0.0

        self.waypoints = [
            (-2.0, -7.0),
            (-2.0,  4.0),
            ( 7.5,  4.5),
            ( 7.8,  7.8),
            ( 2.0,  7.0),
            ( 2.0,  3.0),
            (-2.0,  3.0),
            (-2.0, -3.0),
            ( 8.0, -3.0)
        ]
        self.current_goal_index = 0
        self.state = 'orienting'
        self.wait_start_time = 0.0

    def odom_callback(self, msg):
        # Verifique se odometria está correta
        x = msg.pose.pose.position.x + self.odom_offset[0]
        y = msg.pose.pose.position.y + self.odom_offset[1]
        self.position = (x, y)
        self.linear_velocity = msg.twist.twist.linear.x

        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.yaw = math.atan2(siny_cosp, cosy_cosp)

    def navigate(self):
        if self.current_goal_index >= len(self.waypoints):
            self.get_logger().info("Todos os objetivos foram alcançados!")
            self.publisher.publish(Twist())
            return

        gx, gy = self.waypoints[self.current_goal_index]
        x, y = self.position
        distance = math.hypot(gx - x, gy - y)
        angle_to_goal = math.atan2(gy - y, gx - x)
        angle_diff = self.normalize_angle(angle_to_goal - self.yaw)

        self.get_logger().info(
            f"[{self.state}] Indo para ponto {self.current_goal_index+1}: "
            f"({gx}, {gy}) | Atual: ({x:.2f}, {y:.2f}) | dist: {distance:.2f}, yaw: {math.degrees(self.yaw):.1f}"
        )

        twist = Twist()

        if self.state == 'orienting':
            if abs(angle_diff) > 0.2:
                twist.angular.z = max(min(2.0 * angle_diff, 1.5), -1.5)
                twist.linear.x = 0.0
            else:
                self.state = 'moving'

        elif self.state == 'moving':
            if distance > 0.2:
                twist.linear.x = 0.5
                twist.angular.z = max(min(2.0 * angle_diff, 1.0), -1.0)
            else:
                twist.linear.x = 0.0
                twist.angular.z = 0.0
                self.publisher.publish(twist)
                self.get_logger().info(f"Objetivo {self.current_goal_index+1} alcançado.")
                self.current_goal_index += 1
                self.state = 'orienting'
                return

        elif self.state == 'waiting':
            # Opcional se quiser adicionar uma pausa
            if time() - self.wait_start_time > 1.0:
                self.current_goal_index += 1
                self.state = 'orienting'
            else:
                twist.linear.x = 0.0
                twist.angular.z = 0.0

        self.publisher.publish(twist)

    @staticmethod
    def normalize_angle(angle):
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle

def main(args=None):
    rclpy.init(args=args)
    node = WaypointFollower()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()

