from robot_hat import Pin, Ultrasonic, Grayscale_Module, ADC
from picarx import Picarx
import time
import threading
from inputs import get_key

px = Picarx()
grayscale = Grayscale_Module(ADC(0), ADC(1), ADC(2), reference=2000)

# Ayarlar
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

# Döngü kontrolü için değişkenler
son_donme_yonu = "sag"
engel_sayaci = 0
engel_sayaci_limit = 3

# Klavye dinleme

def klavye_dinle():
    while True:
        events = get_key()
        for e in events:
            if e.ev_type == 'Key':
                if e.state == 1:
                    tuslar.add(e.code)
                elif e.state == 0:
                    tuslar.discard(e.code)

threading.Thread(target=klavye_dinle, daemon=True).start()


def steer(angle):
    px.set_dir_servo_angle(angle + STEERING_OFFSET)


def engel_var_mi():
    distance = px.ultrasonic.read()
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


def main():
    global son_donme_yonu, engel_sayaci
    print("[SİSTEM] Başladı: 'w/s/a/d' hareket, 'm' mod, 'q' çıkış")

    otonom_mod = True  # Başlangıçta otonom modda

    try:
        while True:
            if 'KEY_Q' in tuslar:
                px.stop()
                break

            if 'KEY_M' in tuslar:
                otonom_mod = not otonom_mod
                mod_str = "Otonom" if otonom_mod else "Manuel"
                print(f"[MOD] {mod_str} moda geçildi.")
                time.sleep(0.5)  # debounce için

            if otonom_mod:
                if engel_var_mi() or bosluk_var_mi():
                    px.stop()
                    time.sleep(0.3)
                    px.backward(30)
                    time.sleep(0.5)
                    px.stop()

                    if son_donme_yonu == "sag":
                        steer(-30)
                        son_donme_yonu = "sol"
                    else:
                        steer(30)
                        son_donme_yonu = "sag"

                    px.forward(30)
                    time.sleep(0.6)
                    px.stop()

                    engel_sayaci += 1
                    if engel_sayaci >= engel_sayaci_limit:
                        steer(0)
                        px.backward(30)
                        time.sleep(1)
                        px.stop()
                        engel_sayaci = 0
                else:
                    steer(0)
                    px.forward(30)
            else:
                # Manuel kontrol
                if 'KEY_W' in tuslar:
                    px.forward(30)
                elif 'KEY_S' in tuslar:
                    px.backward(30)
                else:
                    px.stop()

                if 'KEY_A' in tuslar:
                    steer(-30)
                elif 'KEY_D' in tuslar:
                    steer(30)
                else:
                    steer(0)

            time.sleep(0.05)

    except KeyboardInterrupt:
        px.stop()
        print("[SİSTEM] Manuel durduruldu.")


if __name__ == '__main__':
    main()
