import rclpy, time, subprocess, os
from rclpy.node import Node
from geometry_msgs.msg import PoseArray, Twist

class MissileNode(Node):
    def __init__(self):
        super().__init__('missile_node')
        self.sub = self.create_subscription(PoseArray, 'target_positions', self.update, 10)
        self.cmd_pub = self.create_publisher(Twist, '/model/defense_missile/cmd_vel', 10)
        self.fired = False
        self.exploded = False
        self.m_x = 0.0

    def update(self, msg):
        if not msg.poses or self.exploded: return
        t_x = msg.poses[0].position.x
        
        # Düşman 30 metreye geldiğinde SAVUNMA FÜZESİ ATEŞLENİR
        if t_x <= 30.0 and not self.fired:
            self.fired = True
            self.m_x = 2.0
            
        if self.fired:
            # Füze saniyede 8 metre hızla ileri uçar
            self.m_x += 8.0 * 0.05 
            tw = Twist(); tw.linear.x = 8.0; tw.linear.z = 2.0 # Hafif yukarı kavis
            
            # ÇARPIŞMA (Hedefle füze havada buluştuğunda)
            if abs(t_x - self.m_x) < 2.5:
                self.exploded = True
                tw = Twist() # İkisini de durdur
                self.cmd_pub.publish(tw)
                
                # SABİT PATLAMA KÜRESİNİ YARAT
                exp_path = os.path.expanduser('~/air_defense_ws/src/air_defense_core/urdf/explosion.sdf')
                subprocess.Popen(['ros2', 'run', 'ros_gz_sim', 'create', '-file', exp_path, '-name', 'boom', '-x', str(t_x), '-z', '10.0'])
                
                # Çarpışan füzeleri görünmez yap (Yeraltına gönder)
                subprocess.Popen(['ros2', 'topic', 'pub', '--once', '/model/enemy_missile/cmd_vel', 'geometry_msgs/msg/Twist', '{linear: {z: -100.0}}'])
                subprocess.Popen(['ros2', 'topic', 'pub', '--once', '/model/defense_missile/cmd_vel', 'geometry_msgs/msg/Twist', '{linear: {z: -100.0}}'])
                return
                
            self.cmd_pub.publish(tw)

def main(args=None): rclpy.init(args=args); node = MissileNode(); rclpy.spin(node); node.destroy_node(); rclpy.shutdown()
if __name__ == '__main__': main()
