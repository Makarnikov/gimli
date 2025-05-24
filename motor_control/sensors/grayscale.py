from robot_hat import Grayscale_Module, ADC
from picarx import Picarx
import time

# Sensör ve araç başlat
gs = Grayscale_Module(ADC(0), ADC(1), ADC(2), reference=2000)
px = Picarx()

# Eşik değeri (bu değerin altı = açık renk / çizgi)
THRESHOLD = 200

print("🚗 Araç çalışıyor. Açık zemin algılanırsa duracak.")

try:
    while True:
        left = gs.read(gs.LEFT)
        middle = gs.read(gs.MIDDLE)
        right = gs.read(gs.RIGHT)
        print(f"Sol: {left}, Orta: {middle}, Sağ: {right}")

        # Eğer herhangi biri eşik altındaysa dur
        if left < THRESHOLD or middle < THRESHOLD or right < THRESHOLD:
            px.stop()
            print("🛑 Açık zemin (çizgi veya boşluk) algılandı. Araç durdu.")
        else:
            px.set_dir_servo_angle(0)
            px.forward(30)

        time.sleep(0.02)

except KeyboardInterrupt:
    px.stop()
    print("\n🛑 Manuel durduruldu.")
