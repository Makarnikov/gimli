import sys
import time
import keyboard

# robot_hat modülünü elle ekle (kurulum pip'te görünmediyse)
sys.path.append('/home/gimli/robot-hat')

from picarx import Picarx

px = Picarx()

def ileri():
    px.forward(30)
    print("▶️ İleri")

def geri():
    px.backward(30)
    print("◀️ Geri")

def dur():
    px.stop()

print("🕹️ Basılı tuşla kontrol başlıyor. 'q' = çıkış")

try:
    while True:
        if keyboard.is_pressed('up'):
            ileri()
        elif keyboard.is_pressed('down'):
            geri()
        else:
            dur()

        if keyboard.is_pressed('q'):
            dur()
            print("🛑 Çıkış yapıldı.")
            break

        time.sleep(0.05)

except KeyboardInterrupt:
    dur()
    print("\n🛑 Manuel durduruldu.")
