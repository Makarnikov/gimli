from picarx import Picarx
import time

px = Picarx()

try:
    while True:
        distance = px.ultrasonic.read()  # sensörü direkt buradan oku
        print(f"📏 Mesafe: {distance:.2f} cm")

        if distance > 10:
            px.set_dir_servo_angle(0)
            px.forward(30)
        else:
            px.stop()
            print("🛑 Engel algılandı.")

        time.sleep(0.1)

except KeyboardInterrupt:
    px.stop()
    print("\n🛑 Durduruldu.")
