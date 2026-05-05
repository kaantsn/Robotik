import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Vector3
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64

class TurretController(Node):
    def __init__(self):
        super().__init__('turret_node')
        self.sub = self.create_subscription(Vector3, 'turret_commands', self.cmd_cb, 10)
        self.rviz_pub = self.create_publisher(JointState, 'joint_states', 10)
        self.gz_yaw_pub = self.create_publisher(Float64, '/cmd_yaw', 10)
        self.gz_pitch_pub = self.create_publisher(Float64, '/cmd_pitch', 10)
        self.current_yaw, self.current_pitch = 0.0, 0.0
        self.timer = self.create_timer(0.05, self.publish_joints)

    def cmd_cb(self, msg):
        self.current_yaw, self.current_pitch = msg.x, msg.y

    def publish_joints(self):
        js = JointState(); js.header.stamp = self.get_clock().now().to_msg()
        js.name = ['base_to_yaw', 'yaw_to_pitch']
        js.position = [float(self.current_yaw), float(self.current_pitch)]
        self.rviz_pub.publish(js)
        
        y_msg, p_msg = Float64(), Float64()
        y_msg.data, p_msg.data = float(self.current_yaw), float(self.current_pitch)
        self.gz_yaw_pub.publish(y_msg); self.gz_pitch_pub.publish(p_msg)

def main(args=None):
    rclpy.init(args=args); node = TurretController(); rclpy.spin(node); node.destroy_node(); rclpy.shutdown()
if __name__ == '__main__': main()
