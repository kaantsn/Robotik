import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
import math
import random

class WeaponControlNode(Node):
    def __init__(self):
        super().__init__('weapon_node')
        self.subscription = self.create_subscription(Point, 'target_position', self.target_callback, 10)
        self.bullet_speed = 1000.0 # m/s (Örnek: 35mm uçaksavar mermisi hızı)
        self.max_range = 1500.0 # Etkili menzil (metre)
        self.is_firing = False
        self.get_logger().info('Silah Kontrol Sistemi Aktif. Hedefin menzile girmesi bekleniyor...')

    def target_callback(self, msg):
        if self.is_firing:
            return # Halihazırda ateş edildiyse, merminin hedefe varmasını bekle
            
        # 3 Boyutlu Uzayda Mesafe Hesabı
        distance = math.sqrt(msg.x**2 + msg.y**2 + msg.z**2)
        
        # Hedef menzile girdiyse ateşle!
        if distance <= self.max_range:
            self.get_logger().warn(f'DİKKAT! Hedef menzile girdi (Mesafe: {distance:.2f}m). ATEŞ SERBEST!')
            self.fire_weapon(distance)
            
    def fire_weapon(self, distance):
        self.is_firing = True
        tof = distance / self.bullet_speed
        self.get_logger().info(f'>>> NAMLU ATEŞLENDİ! Merminin hedefe varış süresi: {tof:.2f} saniye...')
        
        # Vurma olasılığı (Hedef ne kadar yakınsa vurma ihtimali o kadar yüksek)
        hit_chance = 1.0 - (distance / (self.max_range + 200)) 
        
        # Merminin uçuş süresi kadar bekleyen tek seferlik bir zamanlayıcı oluştur
        self.timer = self.create_timer(tof, lambda: self.hit_check(hit_chance))
        
    def hit_check(self, hit_chance):
        self.timer.cancel() # Zamanlayıcıyı durdur
        roll = random.random() # 0.0 ile 1.0 arası rastgele zar at
        
        if roll < hit_chance:
            self.get_logger().fatal('+++ HEDEF BAŞARIYLA İMHA EDİLDİ! +++')
            # Gerçek bir simülasyonda burada hedefi yok edip yeni hedef çıkarırdık.
            # Şimdilik 2 saniye bekleyip ateş serbest bırakıyoruz.
        else:
            self.get_logger().error('--- ISKALADI! Yeniden angaje olunuyor... ---')
            
        self.is_firing = False

def main(args=None):
    rclpy.init(args=args)
    weapon_node = WeaponControlNode()
    rclpy.spin(weapon_node)
    weapon_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
