import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseArray, Vector3
from std_msgs.msg import Int32
import math
import time

class CommandControlNode(Node):
    def __init__(self):
        super().__init__('c2_node')
        self.sub = self.create_subscription(PoseArray, 'target_positions', self.target_cb, 10)
        self.pub = self.create_publisher(Vector3, 'turret_commands', 10)
        self.target_pub = self.create_publisher(Int32, 'designated_target_id', 10)
        
        self.est_x, self.est_y, self.est_z, self.vel_x, self.vel_y, self.vel_z = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        self.last_time = 0.0
        self.alpha, self.beta = 0.2, 0.05
        self.projectile_speed = 1000.0
        self.locked_target_id = -1

    def target_cb(self, msg):
        if not msg.poses: return
        current_time = time.time()
        
        closest_target, min_dist = None, 999999.0
        for p in msg.poses:
            dist = math.sqrt(p.position.x**2 + p.position.y**2 + p.position.z**2)
            if dist < min_dist: min_dist, closest_target = dist, p
                
        if not closest_target: return
        target_id = int(closest_target.orientation.w)
        
        id_msg = Int32(); id_msg.data = target_id
        self.target_pub.publish(id_msg)
        
        if self.locked_target_id != target_id:
            self.locked_target_id = target_id
            self.est_x, self.est_y, self.est_z = closest_target.position.x, closest_target.position.y, closest_target.position.z
            self.vel_x, self.vel_y, self.vel_z = 0.0, 0.0, 0.0
            self.last_time = current_time
            return
            
        dt = current_time - self.last_time
        if dt <= 0: return
        self.last_time = current_time

        px, py, pz = self.est_x + self.vel_x * dt, self.est_y + self.vel_y * dt, self.est_z + self.vel_z * dt
        rx, ry, rz = closest_target.position.x - px, closest_target.position.y - py, closest_target.position.z - pz
        self.est_x, self.est_y, self.est_z = px + self.alpha * rx, py + self.alpha * ry, pz + self.alpha * rz
        self.vel_x, self.vel_y, self.vel_z = self.vel_x + (self.beta/dt)*rx, self.vel_y + (self.beta/dt)*ry, self.vel_z + (self.beta/dt)*rz

        tof = math.sqrt(self.est_x**2 + self.est_y**2 + self.est_z**2) / self.projectile_speed
        fx, fy, fz = self.est_x + (self.vel_x * tof), self.est_y + (self.vel_y * tof), self.est_z + (self.vel_z * tof)

        cmd_msg = Vector3()
        cmd_msg.x = math.atan2(fy, fx)
        cmd_msg.y = math.atan2(fz, math.sqrt(fx**2 + fy**2))
        cmd_msg.z = 0.0
        self.pub.publish(cmd_msg) # HATA BURADAYDI, DÜZELTİLDİ!

def main(args=None):
    rclpy.init(args=args); node = CommandControlNode(); rclpy.spin(node); node.destroy_node(); rclpy.shutdown()
if __name__ == '__main__': main()
