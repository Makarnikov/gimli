from robot_hat import Pin, Ultrasonic, Grayscale_Module, ADC
from picarx import Picarx
import time
import threading
from inputs import get_key

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Quaternion, TransformStamped
from tf2_ros import TransformBroadcaster
from transforms3d.euler import euler2quat

px = Picarx()
grayscale = Grayscale_Module(ADC(0), ADC(1), ADC(2), reference=2000)

# params

STEERING_OFFSET = -9
GRAYSCALE_THRESHOLD = 100
ULTRASONIC_THRESHOLD = 15
pan_angle = 0
tilt_angle = 30
TILT_MIN = 0
TILT_MAX = 60
PAN_MIN = -40
PAN_MAX = 40

tuslar = set()

x, y, theta = 0.0, 0.0, 0.0
last_time = time.time()


def steer(angle):
    px.set_dir_servo_angle(angle + STEERING_OFFSET)  # centers the wheels


def engel_var_mi():
    distance = px.ultrasonic.read()  # measures the ultrasonic value
    if distance is None:
        print("[!] Ultrasonik ölçüm hatası (None)")
        return False
    elif distance < 0:
        print(f"[!] Ultrasonik geçersiz ölçüm: {distance}")
        return False
    elif distance < ULTRASONIC_THRESHOLD:
        print(f"[!] Gerçek engel algılandı: {distance:.2f} cm")
        return True
    return False


def bosluk_var_mi():
    left = grayscale.read(grayscale.LEFT)
    middle = grayscale.read(grayscale.MIDDLE)
    right = grayscale.read(grayscale.RIGHT)
    print(f"[GRAYSCALE] L:{left:.0f} M:{middle:.0f} R:{right:.0f}")

    if left < GRAYSCALE_THRESHOLD or middle < GRAYSCALE_THRESHOLD or right < GRAYSCALE_THRESHOLD:
        print("[!] Boşluk (beyaz yüzey) algılandı!")
        return True
    return False


def klavye_dinle():
    while True:
        events = get_key()
        for e in events:
            if e.ev_type == 'Key':
                if e.state == 1:
                    tuslar.add(e.code)
                elif e.state == 0:
                    tuslar.discard(e.code)


# Bu thread klavye olaylarını dinler
threading.Thread(target=klavye_dinle, daemon=True).start()


def main():
    global x, y, theta, last_time  # odometry and time variables
    print("[SİSTEM] Başladı: 'w/s/a/d' hareket, 'i/k/j/l' kamera, 'r' sıfırla, 'q' çıkış")

    rclpy.init()    # Initialize ROS 2
    node = Node("odometry_node")    # Create a ROS 2 node
    # Create a publisher for Odometry messages
    odom_pub = node.create_publisher(Odometry, "/odom", 10)
    # Create a TransformBroadcaster for TF2 transforms#
    tf_broadcaster = TransformBroadcaster(node)

    try:
        while rclpy.ok():  # ROS2 main loop
            now = time.time()
            dt = now - last_time
            last_time = now

            vx = 0.0    # Linear velocity(x axis)
            vth = 0.0   # Angular velocity
            tehlike = engel_var_mi() or bosluk_var_mi()

            # UGV CONTROL

            if 'KEY_W' in tuslar and not tehlike:
                px.forward(30)
                vx = 0.1
            elif 'KEY_S' in tuslar:
                px.backward(30)
                vx = -0.1
            else:
                px.stop()

            if vx != 0.0:  # Araç hareket ediyorsa direksiyon etkili
                if 'KEY_A' in tuslar:
                    steer(-30)
                    vth = 1.0
                elif 'KEY_D' in tuslar:
                    steer(30)
                    vth = -1.0
                else:
                    steer(0)
            else:
                steer(0)  # Sabitse teker düz olsun

            # ODOMETRY CALCULATION

            theta += vth * dt  # angular position update
            x += vx * dt * cos(theta)  # linear position update (x axis)
            y += vx * dt * sin(theta)  # linear position update (y axis)

            odom = Odometry()           # Create Odometry message
            odom.header.stamp = node.get_clock().now().to_msg()  # Add time stamp to message
            odom.header.frame_id = "odom"       # Frame ID for the odometry message
            odom.child_frame_id = "base_link"   # Child frame ID for the base link
            odom.pose.pose.position.x = x
            odom.pose.pose.position.y = y
            # Convert Euler angles to quaternion
            q = euler2quat(0, 0, theta)
            odom.pose.pose.orientation = Quaternion(    # Set orientation using quaternion
                x=q[1], y=q[2], z=q[3], w=q[0])
            odom.twist.twist.linear.x = vx
            odom.twist.twist.angular.z = vth
            odom_pub.publish(odom)

            # TF2 TRANSFORM BROADCASTING

            t = TransformStamped()
            t.header.stamp = node.get_clock().now().to_msg()
            t.header.frame_id = "odom"
            t.child_frame_id = "base_link"
            t.transform.translation.x = x
            t.transform.translation.y = y
            t.transform.translation.z = 0.0
            t.transform.rotation = Quaternion(x=q[1], y=q[2], z=q[3], w=q[0])
            tf_broadcaster.sendTransform(t)

            # CAMERA CONTROL

            global tilt_angle, pan_angle
            if 'KEY_I' in tuslar:
                tilt_angle = min(TILT_MAX, tilt_angle + 5)
            elif 'KEY_K' in tuslar:
                tilt_angle = max(TILT_MIN, tilt_angle - 5)

            if 'KEY_J' in tuslar:
                pan_angle = max(PAN_MIN, pan_angle - 5)
            elif 'KEY_L' in tuslar:
                pan_angle = min(PAN_MAX, pan_angle + 5)

            if 'KEY_R' in tuslar:
                pan_angle = 0
                tilt_angle = 30
                print("[!] Kamera resetlendi")

            px.set_cam_tilt_angle(tilt_angle)
            px.set_cam_pan_angle(pan_angle)

            # EXIT

            if 'KEY_Q' in tuslar:
                px.stop()
                print("[SİSTEM] Çıkış yapıldı.")
                break

            time.sleep(0.05)

    except KeyboardInterrupt:
        px.stop()
        print("[SİSTEM] Manuel durduruldu.")
    finally:
        rclpy.shutdown()
        node.destroy_node()


if __name__ == '__main__':
    from math import sin, cos
    main()
