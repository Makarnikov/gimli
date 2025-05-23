
from picarx import Picarx
import time

px = Picarx()

# Motorları ileri sür
print("▶️ İleri gidiyor...")
px.forward(30)
time.sleep(2)

# Dur
px.stop()
time.sleep(1)

# Geri git
print("◀️ Geri gidiyor...")
px.backward(30)
time.sleep(2)

# Dur
px.stop()
print("🛑 Test bitti.")
