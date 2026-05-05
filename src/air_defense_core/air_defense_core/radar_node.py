import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseArray, Pose
import random

class RadarNode(Node):
    def __init__(self):
        super().__init__('radar_node')
        self.sub = self.create_subscription(PoseArray, 'true_target_positions', self.truth_cb, 10)
        self.pub = self.create_publisher(PoseArray, 'target_positions', 10)

    def truth_cb(self, msg):
        noisy_msg = PoseArray()
        noisy_msg.header = msg.header
        noise_level = 20.0
        
        for p in msg.poses:
            np = Pose()
            np.position.x = p.position.x + random.uniform(-noise_level, noise_level)
            np.position.y = p.position.y + random.uniform(-noise_level, noise_level)
            np.position.z = p.position.z + random.uniform(-noise_level, noise_level)
            np.orientation = p.orientation # ID'yi koru
            noisy_msg.poses.append(np)
            
        self.pub.publish(noisy_msg)

def main(args=None):
    rclpy.init(args=args)
    node = RadarNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
