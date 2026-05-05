import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseArray, Point
from std_msgs.msg import Int32
from visualization_msgs.msg import Marker, MarkerArray

class VisualizerNode(Node):
    def __init__(self):
        super().__init__('visualizer_node')
        self.target_sub = self.create_subscription(PoseArray, 'true_target_positions', self.target_cb, 10)
        self.missile_sub = self.create_subscription(Point, 'missile_position', self.missile_cb, 10)
        self.kill_sub = self.create_subscription(Int32, 'target_destroyed', self.kill_cb, 10)
        self.marker_pub = self.create_publisher(MarkerArray, 'visualization_marker_array', 10)
        
        self.targets = []
        self.missile_pos = None
        self.explosions = [] 
        self.timer = self.create_timer(0.1, self.publish_markers)

    def target_cb(self, msg): self.targets = msg.poses
    def missile_cb(self, msg): self.missile_pos = msg
    
    def kill_cb(self, msg):
        killed_id = msg.data
        for t in self.targets:
            if int(t.orientation.w) == killed_id:
                self.explosions.append({'id': killed_id, 'pos': t.position, 'timer': 10})
                break
        self.missile_pos = None

    def publish_markers(self):
        arr = MarkerArray()
        
        # HEDEFLERİ ÇİZ
        for t in self.targets:
            t_id = int(t.orientation.w)
            if any([ex['id'] == t_id for ex in self.explosions]): continue # Patlıyorsa çizme
            
            tm = Marker()
            tm.header.frame_id, tm.id, tm.type, tm.action = "base_link", t_id, Marker.SPHERE, Marker.ADD
            tm.pose.position = t.position
            tm.scale.x, tm.scale.y, tm.scale.z = 10.0, 10.0, 10.0
            tm.color.r, tm.color.g, tm.color.b, tm.color.a = 1.0, 0.0, 0.0, 1.0
            arr.markers.append(tm)
            
        # PATLAMALARI ÇİZ
        for ex in self.explosions[:]:
            em = Marker()
            em.header.frame_id, em.id, em.type, em.action = "base_link", ex['id'] + 10, Marker.SPHERE, Marker.ADD
            em.pose.position = ex['pos']
            em.scale.x, em.scale.y, em.scale.z = 60.0, 60.0, 60.0
            em.color.r, em.color.g, em.color.b, em.color.a = 1.0, 0.5, 0.0, 0.8
            arr.markers.append(em)
            ex['timer'] -= 1
            if ex['timer'] <= 0:
                dm = Marker()
                dm.header.frame_id, dm.id, dm.action = "base_link", ex['id'] + 10, Marker.DELETE
                arr.markers.append(dm)
                self.explosions.remove(ex)

        # FÜZEYİ ÇİZ
        if self.missile_pos and self.missile_pos.z > 0:
            mm = Marker()
            mm.header.frame_id, mm.id, mm.type, mm.action = "base_link", 100, Marker.SPHERE, Marker.ADD
            mm.pose.position = self.missile_pos
            mm.scale.x, mm.scale.y, mm.scale.z = 3.0, 3.0, 3.0
            mm.color.r, mm.color.g, mm.color.b, mm.color.a = 1.0, 1.0, 0.0, 1.0
            arr.markers.append(mm)
            
        self.marker_pub.publish(arr)

def main(args=None):
    rclpy.init(args=args)
    node = VisualizerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
