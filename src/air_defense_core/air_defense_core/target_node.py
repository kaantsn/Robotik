import rclpy, time
from rclpy.node import Node
from geometry_msgs.msg import PoseArray, Pose, Twist

class TargetSimulator(Node):
    def __init__(self):
        super().__init__('target_node')
        self.pub = self.create_publisher(PoseArray, 'target_positions', 10)
        self.cmd_pub = self.create_publisher(Twist, '/model/enemy_missile/cmd_vel', 10)
        self.timer = self.create_timer(0.05, self.update)
        self.start_time = time.time()
        self.alive = True

    def update(self):
        if not self.alive: return
        dt = time.time() - self.start_time
        # Düşman 50 metreden başlar, saniyede 4 metre hızla dümdüz tarete gelir
        current_x = 50.0 - (4.0 * dt)
        
        if current_x < 5.0: self.alive = False # Çarpışma anında durur

        tw = Twist(); tw.linear.x = -4.0 if self.alive else 0.0
        self.cmd_pub.publish(tw)

        msg = PoseArray(); msg.header.frame_id = "base_link"
        p = Pose(); p.position.x, p.position.y, p.position.z = current_x, 0.0, 10.0
        msg.poses.append(p)
        self.pub.publish(msg)

def main(args=None): rclpy.init(args=args); node = TargetSimulator(); rclpy.spin(node); node.destroy_node(); rclpy.shutdown()
if __name__ == '__main__': main()
