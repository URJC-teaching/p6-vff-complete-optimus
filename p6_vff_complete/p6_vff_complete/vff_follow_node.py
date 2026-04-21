import math

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from enum import IntEnum

from geometry_msgs.msg import Twist, Vector3


class State(IntEnum):
    SEARCHING = 0
    FOLLOWING = 1


class VffFollowNode(Node):

    def __init__(self):
        super().__init__('vff_follow_node')

        self.declare_parameter('max_linear_speed', 0.3)
        self.declare_parameter('max_angular_speed', 1.0)
        self.declare_parameter('search_angular_speed', 0.3)
        self.declare_parameter('person_lost_timeout', 1.0)
        self.declare_parameter('repulsive_gain_factor', 1.0)
        self.declare_parameter('repulsive_influence_distance', 0.5)
        self.declare_parameter('stay_distance', 1.0)

        self.max_linear_speed = self.get_parameter('max_linear_speed').value
        self.max_angular_speed = self.get_parameter('max_angular_speed').value
        self.search_angular_speed = self.get_parameter('search_angular_speed').value
        self.person_lost_timeout = self.get_parameter('person_lost_timeout').value
        self.repulsive_gain_factor = self.get_parameter('repulsive_gain_factor').value
        self.repulsive_influence_distance = self.get_parameter(
            'repulsive_influence_distance').value
        self.stay_distance = self.get_parameter('stay_distance').value

        self.state = State.SEARCHING
        self.last_person_time = self.get_clock().now()

        self.attractive_vec = None
        self.repulsive_vec = Vector3()

        self.attractive_sub = self.create_subscription(
            Vector3, 'attractive_vector',
            self.attractive_callback, 10)

        self.repulsive_sub = self.create_subscription(
            Vector3, 'repulsive_vector',
            self.repulsive_callback, 10)

        self.vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)

        self.timer = self.create_timer(0.05, self.control_cycle)

        self.get_logger().info(
            f'VffFollowNode started | '
            f'max_v={self.max_linear_speed}m/s '
            f'max_w={self.max_angular_speed}rad/s '
            f'search_w={self.search_angular_speed}rad/s | '
            f'stay={self.stay_distance}m '
            f'timeout={self.person_lost_timeout}s '
            f'rep_gain={self.repulsive_gain_factor} '
            f'rep_dist={self.repulsive_influence_distance}m'
        )


    def attractive_callback(self, msg):
        self.attractive_vec = msg
        self.last_person_time = self.get_clock().now()
        dist = math.hypot(msg.x, msg.y)
        angle = math.degrees(math.atan2(msg.y, msg.x))
        self.get_logger().info(
            f'ATTRACTIVE: dist={dist:.2f}m angle={angle:.1f}deg',
            throttle_duration_sec=0.5)
        if self.state == State.SEARCHING:
            self.go_state(State.FOLLOWING)

    def repulsive_callback(self, msg):
        self.repulsive_vec = msg
        dist = math.hypot(msg.x, msg.y)
        self.get_logger().info(
            f'REPULSIVE: dist={dist:.2f}m',
            throttle_duration_sec=1.0)


    def compute_vff(self):
        cmd = Twist()
        if self.attractive_vec is None:
            return cmd

        target_dist = math.hypot(self.attractive_vec.x, self.attractive_vec.y)
        if self.stay_distance > 0 and target_dist < self.stay_distance:
            angle = math.atan2(self.attractive_vec.y, self.attractive_vec.x)
            rotation_dir = 1.0 if angle >= 0.0 else -1.0
            cmd.angular.z = rotation_dir * min(self.max_angular_speed, abs(angle))
            self.get_logger().info(
                f'STAY: dentro de stay_distance ({target_dist:.2f}m < {self.stay_distance}m)',
                throttle_duration_sec=1.0)
            return cmd

        obstacle_dist = math.hypot(self.repulsive_vec.x, self.repulsive_vec.y)
        rep_force_x = 0.0
        rep_force_y = 0.0

        rho_0 = self.repulsive_influence_distance
        if 0.0 < obstacle_dist <= rho_0:
            force_mag = 1.0 / obstacle_dist ** 2
            unit_x = self.repulsive_vec.x / obstacle_dist
            unit_y = self.repulsive_vec.y / obstacle_dist
            rep_force_x = self.repulsive_gain_factor * force_mag * unit_x
            rep_force_y = self.repulsive_gain_factor * force_mag * unit_y

        vff_x = self.attractive_vec.x - rep_force_x
        vff_y = self.attractive_vec.y - rep_force_y

        angle = math.atan2(vff_y, vff_x)
        cmd.linear.x = min(self.max_linear_speed, math.hypot(vff_x, vff_y))
        rotation_dir = 1.0 if angle >= 0.0 else -1.0
        cmd.angular.z = rotation_dir * min(self.max_angular_speed, abs(angle))

        self.get_logger().info(
            f'VFF ({vff_x:.2f}, {vff_y:.2f}) -> '
            f'v={cmd.linear.x:.2f} w={cmd.angular.z:.2f}',
            throttle_duration_sec=0.5)
        return cmd


    def control_cycle(self):
        cmd = Twist()

        if self.state == State.SEARCHING:
            cmd.angular.z = self.search_angular_speed
            self.get_logger().info(
                'SEARCHING — rotating...', throttle_duration_sec=3.0)

        elif self.state == State.FOLLOWING:
            elapsed = (self.get_clock().now() - self.last_person_time)
            if elapsed > Duration(seconds=self.person_lost_timeout):
                # Persona perdida -> volver a buscar
                self.go_state(State.SEARCHING)
                self.attractive_vec = None
                cmd.angular.z = self.search_angular_speed
            else:
                cmd = self.compute_vff()

        self.vel_pub.publish(cmd)
        self.repulsive_vec = Vector3() 


    def go_state(self, new_state):
        self.state = new_state
        self.get_logger().info(f'State -> {new_state.name}')


def main(args=None):
    rclpy.init(args=args)
    node = VffFollowNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.try_shutdown()


if __name__ == '__main__':
    main()