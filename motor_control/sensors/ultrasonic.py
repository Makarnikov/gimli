from robot_hat import Ultrasonic, Pin
import time

# Bağlantılara göre doğru BCM pin numaraları
TRIGGER_PIN = 27  # D2
ECHO_PIN = 22     # D3

sensor = Ultrasonic(Pin(TRIGGER_PIN), Pin(ECHO_PIN))

print("📏 Mesafe ölçülüyor... Ctrl+C ile çık")

try:
    while True:
        distance = sensor.read()
        if distance is None or distance == -1:
            print("❌ Ölçüm başarısız")
        else:
            print(f"📏 Mesafe: {distance:.2f} cm")
        time.sleep(0.2)

except KeyboardInterrupt:
    print("\n🛑 Ölçüm durduruldu.")
