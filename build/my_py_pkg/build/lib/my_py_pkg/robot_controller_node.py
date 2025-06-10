import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math
import time

class RobotController(Node):
    def __init__(self):
        super().__init__('robot_controller')

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        # Inicialização com offset do .world
        self.odom_offset = (-7.0, -7.0)
        self.position = [-7.0, -7.0]
        self.yaw = math.radians(45)

        # Parâmetros
        self.linear_speed = 0.6  
        self.angular_speed = 0.3 
        self.dt = 0.1

        # Waypoints
        self.waypoints = [
            (-2.0, -7.0),
            (-2.0,  4.0),
            (7.5,  4.5),
            (7.0, 7.5),
            (2.0, 7.0),
            (2.0, 3.0),
            (-2.0, 3.0),
            (-2.0, -3.0),
            (7.5, -2.0)
        ]
        self.current_waypoint = 0

        # Estados
        self.phase = 'rotate'
        self.target_angle = None
        self.start_time = time.time()

        self.timer = self.create_timer(self.dt, self.update)

    def update(self):
        msg = Twist()

        if self.current_waypoint >= len(self.waypoints):
            self.get_logger().info("Todos os waypoints foram alcançados.")
            self.publisher.publish(Twist())
            self.destroy_timer(self.timer)
            return

        target = self.waypoints[self.current_waypoint]
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        distance = math.hypot(dx, dy)
        angle_to_target = math.atan2(dy, dx)
        angle_diff = self.normalize_angle(angle_to_target - self.yaw)

        self.get_logger().info(f"Indo para {target} | Atual: {self.position} | Distância: {distance:.2f} | Yaw: {math.degrees(self.yaw):.2f} | Dif. ang.: {math.degrees(angle_diff):.2f}")

        if self.phase == 'rotate':
            if abs(angle_diff) > 0.05:
                msg.angular.z = max(min(self.angular_speed, abs(angle_diff) / self.dt), 0.2) * (1 if angle_diff > 0 else -1)
            else:
                msg.angular.z = 0.0
                self.phase = 'move'
        elif self.phase == 'move':
            if distance > 0.5:
                # Se for o último waypoint, força avanço ignorando obstáculos visuais
                if self.current_waypoint == len(self.waypoints) - 1:
                    msg.linear.x = self.linear_speed
                else:
                    msg.linear.x = self.linear_speed
            else:
                msg.linear.x = 0.0
                self.get_logger().info(f"Alcançou waypoint {self.current_waypoint + 1}: {target}")
                self.current_waypoint += 1
                self.phase = 'rotate'

        # Atualiza simulação interna de posição e orientação
        self.yaw += msg.angular.z * self.dt
        self.position[0] += msg.linear.x * math.cos(self.yaw) * self.dt
        self.position[1] += msg.linear.x * math.sin(self.yaw) * self.dt

        self.publisher.publish(msg)

    def normalize_angle(self, angle):
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

def main(args=None):
    rclpy.init(args=args)
    node = RobotController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

