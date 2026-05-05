import rclpy
from rclpy.node import Node
from visualization_msgs.msg import MarkerArray
import tkinter as tk
from tkinter import ttk
import math
import time
import random

class C2Listener(Node):
    def __init__(self):
        super().__init__('tkinter_c2_listener')
        self.sub = self.create_subscription(MarkerArray, 'tactical_display', self.data_callback, 10)
        self.enemies = {}; self.interceptors = {}; self.explosions = []
        self.event_log = []; self.missiles_fired = 0

    def data_callback(self, msg):
        current_enemies = {}; current_interceptors = {}; exp_list = []
        for m in msg.markers:
            if m.action == 0:
                x, y, z = m.pose.position.x, m.pose.position.y, m.pose.position.z
                dist = math.sqrt(x**2 + y**2)
                azimuth = math.degrees(math.atan2(y, x))
                if azimuth < 0: azimuth += 360
                
                if 100 <= m.id < 200:
                    current_enemies[m.id] = {'x': x, 'y': y, 'z': z, 'dist': dist, 'azm': azimuth}
                    if m.id not in self.enemies:
                        self.event_log.append(f"[{time.strftime('%H:%M:%S')}] RADAR: YENİ İZ [TRK-{m.id}] MENZİL: {dist:.0f}m")
                elif 300 <= m.id < 400:
                    current_interceptors[m.id] = {'x': x, 'y': y, 'z': z}
                    if m.id not in self.interceptors:
                        self.missiles_fired += 1
                        self.event_log.append(f"[{time.strftime('%H:%M:%S')}] WPN: VLS ATEŞLENDİ [INT-{m.id}]")
                # Patlamaları daha stabil algılamak için ID aralığını genişlettik
                elif 500 <= m.id < 800 and m.id % 3 == 0:
                    exp_list.append((x, y, m.scale.x))
            elif m.action == 2:
                if 100 <= m.id < 200 and m.id in self.enemies:
                    self.event_log.append(f"[{time.strftime('%H:%M:%S')}] SYS: HEDEF İMHA EDİLDİ [TRK-{m.id}]")

        self.enemies = current_enemies; self.interceptors = current_interceptors; self.explosions = exp_list

class C2DashboardApp:
    def __init__(self, root, ros_node):
        self.root = root
        self.ros_node = ros_node
        self.root.title("HAKİM - HAVA SAVUNMA KOMUTA KONTROL MERKEZİ")
        self.root.geometry("1500x850")
        self.root.configure(bg="#02060a")
        
        self.sweep_angle = 0
        self.max_range = 1600.0
        
        self.setup_ui()
        self.update_loop()

    def setup_ui(self):
        hud_frame = tk.Frame(self.root, bg="#05101a", bd=2, relief="ridge")
        hud_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.lbl_clock = tk.Label(hud_frame, text="00:00:00", bg="#05101a", fg="cyan", font=("Consolas", 14, "bold"))
        self.lbl_clock.pack(side=tk.LEFT, padx=15, pady=5)
        
        self.lbl_threat_level = tk.Label(hud_frame, text="DURUM: GÜVENDE", bg="#05101a", fg="#00ff44", font=("Consolas", 14, "bold"))
        self.lbl_threat_level.pack(side=tk.LEFT, padx=20)
        
        self.lbl_active_targets = tk.Label(hud_frame, text="AKTİF İZ: 0", bg="#05101a", fg="white", font=("Consolas", 14, "bold"))
        self.lbl_active_targets.pack(side=tk.RIGHT, padx=15)
        
        self.lbl_ammo = tk.Label(hud_frame, text="MÜHİMMAT: %100", bg="#05101a", fg="#00ff44", font=("Consolas", 14, "bold"))
        self.lbl_ammo.pack(side=tk.RIGHT, padx=20)

        main_frame = tk.Frame(self.root, bg="#02060a")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        left_frame = tk.Frame(main_frame, bg="#02060a", bd=2, relief="sunken")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(left_frame, text="▼ AESA TAKTİK RADAR (LINK-16) ▼", bg="#02060a", fg="#00ff44", font=("Consolas", 12, "bold")).pack(pady=2)
        self.canvas = tk.Canvas(left_frame, bg="#000502", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        right_frame = tk.Frame(main_frame, bg="#02060a")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(right_frame, text="▼ AKTİF TEHDİT KİNEMATİK MATRİSİ ▼", bg="#330000", fg="white", font=("Consolas", 11, "bold")).pack(fill=tk.X)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#05101a", foreground="#00ff44", fieldbackground="#05101a", font=("Consolas", 10), rowheight=25)
        style.configure("Treeview.Heading", background="#002200", foreground="white", font=("Consolas", 10, "bold"))
        
        self.tree = ttk.Treeview(right_frame, columns=("ID", "SINIF", "MESAFE(m)", "AÇI(°)", "ETA(s)", "Pk(%)"), show="headings", height=10)
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=70, anchor=tk.CENTER)
        self.tree.pack(fill=tk.X, pady=5)

        tk.Label(right_frame, text="▼ TAKTİK OLAY GÜNLÜĞÜ ▼", bg="#002200", fg="white", font=("Consolas", 11, "bold")).pack(fill=tk.X, pady=2)
        self.log_text = tk.Text(right_frame, bg="#000000", fg="#00ff44", font=("Consolas", 10), height=14, bd=2, relief="sunken")
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # LOG RENKLENDİRME TAG'LERİ (Orijinal Kod Yapısına Görsel Eklenti)
        self.log_text.tag_config("sys", foreground="#00ff44") 
        self.log_text.tag_config("wpn", foreground="#00ffff") 
        self.log_text.tag_config("hit", foreground="#ffff00") 
        self.log_text.tag_config("new", foreground="#ff3333") 

    def draw_radar(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width(); h = self.canvas.winfo_height()
        if w < 10 or h < 10: return
        cx, cy = w / 2, h / 2
        scale = min(w, h) / (2.0 * self.max_range)

        # Merkez ve Eksenler
        self.canvas.create_line(cx, 0, cx, h, fill="#003300", dash=(2, 4))
        self.canvas.create_line(0, cy, w, cy, fill="#003300", dash=(2, 4))
        self.canvas.create_oval(cx-5, cy-5, cx+5, cy+5, outline="#00ff44")

        # Menzil Halkaları
        for r in [400, 800, 1200, 1600]:
            pr = r * scale
            self.canvas.create_oval(cx - pr, cy - pr, cx + pr, cy + pr, outline="#004400", width=1)
            if r != 1600: self.canvas.create_text(cx + pr + 15, cy + 10, text=f"{r}m", fill="#00aa00", font=("Consolas", 8))

        # YILDIZ TARET FORMASYONUNU 2D RADARA ÇİZME (SADECE ÇİZİMDİR, MANTIĞI ETKİLEMEZ)
        for i in range(10):
            angle = math.radians(-90 + i * 36)
            r_radar = 35.0 if i % 2 == 0 else 15.0 
            tx = cx + r_radar * math.cos(angle)
            ty = cy + r_radar * math.sin(angle)
            self.canvas.create_oval(tx-3, ty-3, tx+3, ty+3, fill="#00ffff", outline="#00ffff")
            self.canvas.create_oval(tx-6, ty-6, tx+6, ty+6, outline="#004444")

        # Radar Taraması (Sweep)
        self.sweep_angle = (self.sweep_angle - 4) % 360
        rad = math.radians(self.sweep_angle)
        ex, ey = cx + (self.max_range * scale) * math.cos(rad), cy - (self.max_range * scale) * math.sin(rad)
        self.canvas.create_line(cx, cy, ex, ey, fill="#00ff44", width=2)

        closest_id = None; min_dist = 9999
        for e_id, data in self.ros_node.enemies.items():
            if data['dist'] < min_dist:
                min_dist = data['dist']; closest_id = e_id

        # Düşman Çizimi
        for e_id, data in self.ros_node.enemies.items():
            px, py = cx + data['x'] * scale, cy - data['y'] * scale
            self.canvas.create_polygon(px, py-6, px-6, py+6, px+6, py+6, fill="#ff0000", outline="#ffaaaa")
            self.canvas.create_text(px+15, py-10, text=f"TRK-{e_id}", fill="#ff5555", font=("Consolas", 8))
            
            # Kilit Kutusu
            if e_id == closest_id and int(time.time() * 5) % 2 == 0:
                self.canvas.create_rectangle(px-12, py-12, px+12, py+12, outline="yellow", width=2.0)
                self.canvas.create_text(px, py+18, text="[ LOCK ]", fill="yellow", font=("Consolas", 8, "bold"))

        # Önleyici Çizimi
        for i_id, data in self.ros_node.interceptors.items():
            px, py = cx + data['x'] * scale, cy - data['y'] * scale
            self.canvas.create_polygon(px, py-5, px-5, py, px, py+5, px+5, py, fill="#00ffff", outline="white")

        # Patlama Çizimi
        for x, y, radius in self.ros_node.explosions:
            px, py = cx + x * scale, cy - y * scale
            pr = radius * scale * 1.5
            self.canvas.create_oval(px-pr, py-pr, px+pr, py+pr, outline="#ff8800", width=2)
            self.canvas.create_oval(px-pr*0.5, py-pr*0.5, px+pr*0.5, py+pr*0.5, fill="#ffaa00")

    def update_loop(self):
        rclpy.spin_once(self.ros_node, timeout_sec=0)
        self.draw_radar()
        
        self.lbl_clock.config(text=time.strftime('SYS TIME: %H:%M:%S'))
        
        for item in self.tree.get_children(): self.tree.delete(item)
            
        active_count = len(self.ros_node.enemies)
        self.lbl_active_targets.config(text=f"AKTİF İZ: {active_count}")
        
        if active_count > 0:
            self.lbl_threat_level.config(text="DURUM: TAARRUZ [KIRMIZI]", fg="#ff3333")
        else:
            self.lbl_threat_level.config(text="DURUM: GÜVENDE [YEŞİL]", fg="#00ff44")

        # ORİJİNAL TABLO MANTIĞI
        for e_id, data in self.ros_node.enemies.items():
            dist = data['dist']
            eta = dist / 280.0
            pk = min(99.9, max(45.0, 100 - (dist / 50.0) + random.uniform(-2, 2)))
            cls = "KRİTİK" if dist < 800 else "YÜKSEK" if dist < 1200 else "TAKİP"
            self.tree.insert("", "end", values=(f"TRK-{e_id}", cls, f"{dist:.0f}", f"{data['azm']:.1f}", f"{eta:.1f}", f"%{pk:.1f}"))

        rem = 100 - self.ros_node.missiles_fired
        self.lbl_ammo.config(text=f"MÜHİMMAT: %{rem}")
        if rem <= 20: self.lbl_ammo.config(fg="red")
        
        # SADECE RENKLİ YAZILDIRMA EKLENTİSİ
        if self.ros_node.event_log:
            self.log_text.config(state=tk.NORMAL)
            for log in self.ros_node.event_log:
                tag = "sys"
                if "WPN" in log: tag = "wpn"
                elif "İMHA" in log: tag = "hit"
                elif "YENİ" in log: tag = "new"
                self.log_text.insert(tk.END, log + "\n", tag)
            self.ros_node.event_log.clear()
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)

        self.root.after(40, self.update_loop)

def main(args=None):
    rclpy.init(args=args); ros_node = C2Listener(); root = tk.Tk()
    app = C2DashboardApp(root, ros_node)
    def on_closing():
        ros_node.destroy_node(); rclpy.shutdown(); root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing); root.mainloop()

if __name__ == '__main__': main()
