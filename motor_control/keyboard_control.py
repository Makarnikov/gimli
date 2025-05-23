import sys
sys.path.append('/home/gimli/robot-hat')  # bu dizin senin robot_hat dosyanın olduğu yer
import time
import keyboard
from picarx import Picarx

px = Picarx()

pan_angle = 0
tilt_angle = 0

print("🕹️ Basılı tuşla kontrol başlıyor. 'q' = çıkış")

try:
    while True:
        # Yön kontrolü
        if keyboard.is_pressed('a'):
            px.set_dir_servo_angle(-39)
        elif keyboard.is_pressed('d'):
            px.set_dir_servo_angle(21)
        else:
            px.set_dir_servo_angle(-9)

        # Hareket kontrolü
        if keyboard.is_pressed('w'):
            px.forward(80)
        elif keyboard.is_pressed('s'):
            px.backward(80)
        else:
            px.stop()

        # Kamera kontrolü
        if keyboard.is_pressed('i'):
            tilt_angle = min(60, tilt_angle + 5)
            px.set_cam_tilt_angle(tilt_angle)
        elif keyboard.is_pressed('k'):
            tilt_angle = max(-5, tilt_angle - 5)
            px.set_cam_tilt_angle(tilt_angle)
        elif keyboard.is_pressed('j'):
            pan_angle = max(-45, pan_angle - 5)
            px.set_cam_pan_angle(pan_angle)
        elif keyboard.is_pressed('l'):
            pan_angle = min(45, pan_angle + 5)
            px.set_cam_pan_angle(pan_angle)

        if keyboard.is_pressed('q'):
            px.stop()
            print("🛑 Çıkış yapıldı.")
            break

        time.sleep(0.05)

except KeyboardInterrupt:
    px.stop()
    print("\n🛑 Manuel durduruldu.")
