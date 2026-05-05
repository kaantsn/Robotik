import rclpy, math, time, random
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point

class Enemy:
    def __init__(self, e_id):
        self.id = e_id
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(1500.0, 2800.0) 
        self.x = radius * math.cos(angle)
        self.y = radius * math.sin(angle)
        self.z = random.uniform(100.0, 400.0)
        self.speed = random.uniform(130.0, 200.0)
        self.trail = []
        self.active = True

class Interceptor:
    def __init__(self, m_id, target, turret_x, turret_y):
        self.id = m_id
        self.target = target
        self.x, self.y, self.z = turret_x, turret_y, 16.0
        self.vx, self.vy, self.vz = 0.0, 0.0, 0.0
        self.speed = 0.0
        self.max_speed = 850.0
        self.trail = []
        self.active = True

class Explosion:
    def __init__(self, exp_id, x, y, z):
        self.id = exp_id; self.x = x; self.y = y; self.z = z
        self.radius = 5.0; self.alpha = 1.0; self.active = True

class RvizMilitarySim(Node):
    def __init__(self):
        super().__init__('rviz_military_sim')
        self.pub = self.create_publisher(MarkerArray, 'tactical_display', 10)
        self.timer = self.create_timer(0.033, self.update_sim) 
        self.last_time = time.time()
        
        # ORİJİNAL KUSURSUZ YILDIZ FORMASYONU
        self.turrets = []
        turret_id = 0
        R_outer = 250.0 
        R_inner = 100.0 
        
        for i in range(10):
            angle = math.radians(-90 + i * 36)
            r = R_outer if i % 2 == 0 else R_inner
            tx = r * math.cos(angle)
            ty = r * math.sin(angle)
            self.turrets.append({'id': turret_id, 'x': tx, 'y': ty, 'yaw': 0.0, 'pitch': 0.0, 'fired': 0})
            turret_id += 1

        self.spawn_wave()

    def spawn_wave(self):
        # 10 Taret x 10 Füze = 100 HEDEF
        self.enemies = [Enemy(i) for i in range(100)]
        self.interceptors = []
        self.explosions = []
        self.wave_cleared_time = 0.0
        for t in self.turrets:
            t['fired'] = 0

    def get_marker(self, m_id, m_type, r, g, b, a, scale_x, scale_y, scale_z, x, y, z, yaw=0.0, pitch=0.0):
        m = Marker()
        m.header.frame_id = "map"
        m.header.stamp = self.get_clock().now().to_msg()
        m.ns = "tactical"
        m.id = m_id; m.type = m_type; m.action = Marker.ADD
        m.pose.position.x, m.pose.position.y, m.pose.position.z = float(x), float(y), float(z)
        cy, sy = math.cos(yaw * 0.5), math.sin(yaw * 0.5)
        cp, sp = math.cos(pitch * 0.5), math.sin(pitch * 0.5)
        m.pose.orientation.w = cy * cp; m.pose.orientation.x = sy * sp
        m.pose.orientation.y = cy * sp; m.pose.orientation.z = sy * cp
        m.scale.x, m.scale.y, m.scale.z = float(scale_x), float(scale_y), float(scale_z)
        m.color.r, m.color.g, m.color.b, m.color.a = float(r), float(g), float(b), float(a)
        return m

    def update_sim(self):
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time
        ma = MarkerArray()

        active_enemies = [e for e in self.enemies if e.active]
        
        for t in self.turrets:
            if active_enemies:
                closest = min(active_enemies, key=lambda e: (e.x - t['x'])**2 + (e.y - t['y'])**2)
                dx, dy = closest.x - t['x'], closest.y - t['y']
                dist_2d = math.sqrt(dx**2 + dy**2)
                t['yaw'] = math.atan2(dy, dx)
                t['pitch'] = math.atan2(closest.z, dist_2d)

        for e in self.enemies:
            if e.active:
                dist = math.sqrt(e.x**2 + e.y**2)
                e.x -= (e.x / dist) * e.speed * dt
                e.y -= (e.y / dist) * e.speed * dt
                e.trail.append(Point(x=e.x, y=e.y, z=e.z))
                
                # ORİJİNAL OTONOM MANTIK (Her taret tam 10 tane vuracak)
                if dist < 1200.0 and not any(m.target.id == e.id for m in self.interceptors):
                    available_turrets = [t for t in self.turrets if t['fired'] < 10]
                    if available_turrets:
                        closest_turret = min(available_turrets, key=lambda t: (t['x']-e.x)**2 + (t['y']-e.y)**2)
                        closest_turret['fired'] += 1
                        self.interceptors.append(Interceptor(len(self.interceptors), e, closest_turret['x'], closest_turret['y']))

        for m in self.interceptors:
            if m.active:
                if m.speed < m.max_speed: m.speed += 700.0 * dt 
                dx, dy, dz = m.target.x - m.x, m.target.y - m.y, m.target.z - m.z
                dist_m_e = math.sqrt(dx**2 + dy**2 + dz**2)

                if dist_m_e < 35.0 and m.target.active:
                    m.active = m.target.active = False
                    self.explosions.append(Explosion(len(self.explosions), m.target.x, m.target.y, m.target.z))
                elif m.target.active:
                    m.vx += (dx/dist_m_e * m.speed - m.vx) * 12.0 * dt
                    m.vy += (dy/dist_m_e * m.speed - m.vy) * 12.0 * dt
                    m.vz += (dz/dist_m_e * m.speed - m.vz) * 12.0 * dt
                    m.x += m.vx * dt; m.y += m.vy * dt; m.z += m.vz * dt
                    m.trail.append(Point(x=m.x, y=m.y, z=m.z))
                else: m.active = False

        for exp in self.explosions:
            if exp.active:
                exp.radius += 200.0 * dt; exp.alpha -= 2.0 * dt 
                if exp.alpha <= 0: exp.active = False

        if not active_enemies and not any(exp.active for exp in self.explosions):
            if self.wave_cleared_time == 0.0: self.wave_cleared_time = time.time()
            elif time.time() - self.wave_cleared_time > 2.0:
                m_del = Marker(); m_del.action = Marker.DELETEALL; ma.markers.append(m_del)
                self.spawn_wave(); self.pub.publish(ma); return

        # ========================================================
        # GÖRSELLEŞTİRME (MANTIĞA DOKUNULMADI)
        # ========================================================
        
        # Orijinal Zemin
        ma.markers.append(self.get_marker(1, Marker.CYLINDER, 0.0, 0.3, 0.0, 1.0, 700.0, 700.0, 2.0, 0.0, 0.0, -1.0))
        
        # Ekstra Görsel: Merkez Komuta Merkezi (Sistemi Etkilemez)
        ma.markers.append(self.get_marker(2, Marker.CYLINDER, 0.0, 1.0, 1.0, 0.3, 150.0, 150.0, 1.0, 0.0, 0.0, -0.5))
        ma.markers.append(self.get_marker(3, Marker.SPHERE, 0.8, 0.9, 1.0, 0.8, 30.0, 30.0, 15.0, 0.0, 0.0, 5.0))

        # Taretler
        for idx, t in enumerate(self.turrets):
            base_id = 10 + idx*4
            ma.markers.append(self.get_marker(base_id, Marker.CUBE, 0.5, 0.5, 0.55, 1.0, 18.0, 18.0, 12.0, t['x'], t['y'], 6.0, t['yaw'])) 
            ma.markers.append(self.get_marker(base_id+1, Marker.SPHERE, 0.9, 0.9, 0.9, 1.0, 18.0, 18.0, 18.0, t['x'], t['y'], 14.0)) 
            barrel_x = t['x'] + 12.0 * math.cos(t['yaw']) * math.cos(t['pitch'])
            barrel_y = t['y'] + 12.0 * math.sin(t['yaw']) * math.cos(t['pitch'])
            barrel_z = 14.0 + 12.0 * math.sin(t['pitch'])
            ma.markers.append(self.get_marker(base_id+2, Marker.CYLINDER, 0.2, 0.2, 0.2, 1.0, 3.5, 3.5, 25.0, barrel_x, barrel_y, barrel_z, t['yaw'], 1.57 - t['pitch']))

        for e in self.enemies:
            if e.active:
                yaw = math.atan2(-e.y, -e.x)
                ma.markers.append(self.get_marker(100+e.id, Marker.ARROW, 0.9, 0.1, 0.1, 1.0, 50.0, 8.0, 8.0, e.x, e.y, e.z, yaw, 0.0))
                if len(e.trail) > 2:
                    tr = self.get_marker(200+e.id, Marker.LINE_STRIP, 1.0, 0.3, 0.0, 0.9, 5.0, 0.0, 0.0, 0.0, 0.0, 0.0)
                    tr.points = e.trail[-8:]; ma.markers.append(tr) 
            else:
                m1 = self.get_marker(100+e.id, Marker.ARROW, 0.0,0.0,0.0,0.0, 1.0,1.0,1.0, 0.0,0.0,0.0)
                m1.action = Marker.DELETE; ma.markers.append(m1)
                m2 = self.get_marker(200+e.id, Marker.LINE_STRIP, 0.0,0.0,0.0,0.0, 1.0,1.0,1.0, 0.0,0.0,0.0)
                m2.action = Marker.DELETE; ma.markers.append(m2)

        for m in self.interceptors:
            if m.active:
                yaw = math.atan2(m.vy, m.vx)
                pitch = math.atan2(-m.vz, math.sqrt(m.vx**2 + m.vy**2))
                ma.markers.append(self.get_marker(300+m.id, Marker.ARROW, 0.0, 1.0, 1.0, 1.0, 45.0, 6.0, 7.0, m.x, m.y, m.z, yaw, pitch))
                if len(m.trail) > 2:
                    tr = self.get_marker(400+m.id, Marker.LINE_STRIP, 0.0, 1.0, 1.0, 1.0, 5.0, 0.0, 0.0, 0.0, 0.0, 0.0)
                    tr.points = m.trail[-6:]; ma.markers.append(tr) 
            else:
                m1 = self.get_marker(300+m.id, Marker.ARROW, 0.0,0.0,0.0,0.0, 1.0,1.0,1.0, 0.0,0.0,0.0)
                m1.action = Marker.DELETE; ma.markers.append(m1)
                m2 = self.get_marker(400+m.id, Marker.LINE_STRIP, 0.0,0.0,0.0,0.0, 1.0,1.0,1.0, 0.0,0.0,0.0)
                m2.action = Marker.DELETE; ma.markers.append(m2)

        for exp in self.explosions:
            if exp.active:
                # ORİJİNAL PATLAMA ID'LERİ (Tkinter'ın bozulmaması için)
                ma.markers.append(self.get_marker(500+exp.id*3, Marker.SPHERE, 1.0, 1.0, 0.8, max(0.0, exp.alpha), exp.radius*0.4, exp.radius*0.4, exp.radius*0.4, exp.x, exp.y, exp.z))
                ma.markers.append(self.get_marker(500+exp.id*3+1, Marker.SPHERE, 1.0, 0.4, 0.0, max(0.0, exp.alpha*0.8), exp.radius, exp.radius, exp.radius, exp.x, exp.y, exp.z))
                ma.markers.append(self.get_marker(500+exp.id*3+2, Marker.SPHERE, 0.4, 0.0, 0.0, max(0.0, exp.alpha*0.5), exp.radius*1.3, exp.radius*1.3, exp.radius*1.3, exp.x, exp.y, exp.z))
                
                # SADECE GÖRSEL EKLENTİ (800 ID Serisi, mantığa etki etmez)
                shock_radius = exp.radius * 2.5
                ma.markers.append(self.get_marker(800+exp.id, Marker.CYLINDER, 0.0, 1.0, 1.0, max(0.0, exp.alpha*0.6), shock_radius, shock_radius, 2.0, exp.x, exp.y, exp.z))
            else:
                for i in range(3):
                    m1 = self.get_marker(500+exp.id*3+i, Marker.SPHERE, 0.0,0.0,0.0,0.0, 1.0,1.0,1.0, 0.0,0.0,0.0)
                    m1.action = Marker.DELETE; ma.markers.append(m1)
                
                m_shock = self.get_marker(800+exp.id, Marker.CYLINDER, 0.0,0.0,0.0,0.0, 1.0,1.0,1.0, 0.0,0.0,0.0)
                m_shock.action = Marker.DELETE; ma.markers.append(m_shock)

        self.pub.publish(ma)

def main(args=None): rclpy.init(args=args); node = RvizMilitarySim(); rclpy.spin(node); node.destroy_node(); rclpy.shutdown()
if __name__ == '__main__': main()
