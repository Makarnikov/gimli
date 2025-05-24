from robot_hat import Pin, Ultrasonic, Grayscale_Module, ADC
from picarx import Picarx
import time
import keyboard

px = Picarx()
grayscale = Grayscale_Module(ADC(0), ADC(1), ADC(2), reference=2000)

# ⚙️ Ayarlar
STEERING_OFFSET = -9
GRAYSCALE_THRESHOLD = 100
ULTRASONIC_THRESHOLD = 10

# 🎥 Kamera pozisyon ve sınırlar
pan_angle = 0
tilt_angle = 30  # başlangıç yukarı 15°
TILT_MIN = 0
TILT_MAX = 60
PAN_MIN = -40
PAN_MAX = 40

# Başlangıçta kamerayı pozisyonla
px.set_cam_tilt_angle(tilt_angle)
px.set_cam_pan_angle(pan_angle)

# Fonksiyonlar
def steer(angle):
    px.set_dir_servo_angle(angle + STEERING_OFFSET)

def engel_var_mi():
    distance = px.ultrasonic.read()
    if distance is None:
        print("⚠️ Ultrasonik ölçüm hatası (None)")
        return False
    elif distance < 0:
        print(f"⚠️ Ultrasonik geçersiz ölçüm: {distance}")
        return False
    elif distance < ULTRASONIC_THRESHOLD:
        print(f"🚧 Gerçek engel algılandı: {distance:.2f} cm")
        return True
    return False

def bosluk_var_mi():
    left = grayscale.read(grayscale.LEFT)
    middle = grayscale.read(grayscale.MIDDLE)
    right = grayscale.read(grayscale.RIGHT)
    print(f"🎛️ Grayscale L:{left:.0f} M:{middle:.0f} R:{right:.0f}")

    if left < GRAYSCALE_THRESHOLD or middle < GRAYSCALE_THRESHOLD or right < GRAYSCALE_THRESHOLD:
        print("🕳️ Boşluk (beyaz yüzey) algılandı!")
        return True
    return False

print("🧠 Sistem başladı: 'w/s/a/d' hareket, 'i/k/j/l' kamera, 'r' sıfırla, 'q' çıkış")

try:
    while True:
        tehlike = engel_var_mi() or bosluk_var_mi()

        # 🚗 Direksiyon kontrol
        if keyboard.is_pressed('a'):
            steer(-30)
        elif keyboard.is_pressed('d'):
            steer(30)
        else:
            steer(0)

        # 🚗 Hareket
        if keyboard.is_pressed('w') and not tehlike:
            px.forward(30)
        elif keyboard.is_pressed('s'):
            px.backward(30)
        else:
            px.stop()

        # 🎥 Kamera kontrol
        if keyboard.is_pressed('i'):
            tilt_angle = min(TILT_MAX, tilt_angle + 5)
        elif keyboard.is_pressed('k'):
            tilt_angle = max(TILT_MIN, tilt_angle - 5)

        if keyboard.is_pressed('j'):
            pan_angle = max(PAN_MIN, pan_angle - 5)
        elif keyboard.is_pressed('l'):
            pan_angle = min(PAN_MAX, pan_angle + 5)

        if keyboard.is_pressed('r'):
            pan_angle = 0
            tilt_angle = 30
            print("♻️ Kamera resetlendi")

        px.set_cam_tilt_angle(tilt_angle)
        px.set_cam_pan_angle(pan_angle)

        # Çıkış
        if keyboard.is_pressed('q'):
            px.stop()
            print("🛑 Çıkış yapıldı.")
            break

        time.sleep(0.05)

except KeyboardInterrupt:
    px.stop()
    print("\n🛑 Manuel durduruldu.")
