from robot_hat import Pin, Ultrasonic, Grayscale_Module, ADC
from picarx import Picarx
import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

# Donanım başlat
px = Picarx()
grayscale = Grayscale_Module(ADC(0), ADC(1), ADC(2), reference=2000)

# Ayarlar
STEERING_OFFSET = -9
GRAYSCALE_THRESHOLD = 100
ULTRASONIC_THRESHOLD = 10
pan_angle = 0
tilt_angle = 30
TILT_MIN = 0
TILT_MAX = 60
PAN_MIN = -40
PAN_MAX = 40

px.set_cam_tilt_angle(tilt_angle)
px.set_cam_pan_angle(pan_angle)

def steer(angle):
    px.set_dir_servo_angle(angle + STEERING_OFFSET)

def engel_var_mi():
    distance = px.ultrasonic.read()
    if distance is None:
        print("\u26a0\ufe0f Ultrasonik ölçüm hatası (None)")
        return False
    elif distance < 0:
        print(f"\u26a0\ufe0f Ultrasonik geçersiz ölçüm: {distance}")
        return False
    elif distance < ULTRASONIC_THRESHOLD:
        print(f"🚧 Gerçek engel algılandı: {distance:.2f} cm")
        return True
    return False

def bosluk_var_mi():
    left = grayscale.read(grayscale.LEFT)
    middle = grayscale.read(grayscale.MIDDLE)
    right = grayscale.read(grayscale.RIGHT)
    print(f"🎮 Grayscale L:{left:.0f} M:{middle:.0f} R:{right:.0f}")

    if left < GRAYSCALE_THRESHOLD or middle < GRAYSCALE_THRESHOLD or right < GRAYSCALE_THRESHOLD:
        print("🕳️ Boşluk (beyaz yüzey) algılandı!")
        return True
    return False

print("🧠 Sistem başladı: 'w/s/a/d' hareket, 'i/k/j/l' kamera, 'r' sıfırla, 'q' çıkış")

class MotorControlNode(Node):
    def __init__(self):
        super().__init__('motor_control_node')
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.control_callback,
            10
        )
        self.get_logger().info("🚀 ROS2 klavye kontrolü aktif.")

    def control_callback(self, msg: Twist):
        tehlike = engel_var_mi() or bosluk_var_mi()

        # 🚗 Direksiyon
        if msg.angular.z > 0.1:
            steer(-30)
        elif msg.angular.z < -0.1:
            steer(30)
        else:
            steer(0)

        # 🚗 Hareket
        if msg.linear.x > 0.05 and not tehlike:
            px.forward(30)
        elif msg.linear.x < -0.05:
            px.backward(30)
        else:
            px.stop()

        px.set_cam_tilt_angle(tilt_angle)
        px.set_cam_pan_angle(pan_angle)

def main(args=None):
    rclpy.init(args=args)
    node = MotorControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        px.stop()
        print("\n🛑 Manuel durduruldu.")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
