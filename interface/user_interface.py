import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2


class RobotUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Robot Kontrol Paneli")
        self.master.geometry("500x600")

        self.label = tk.Label(
            master, text="Robot Kamerası", font=("Arial", 14))
        self.label.pack(pady=5)

        # Kamera görüntüsü alanı
        self.video_label = tk.Label(master)
        self.video_label.pack()

        # Yönlendirme düğmeleri
        btn_frame = tk.Frame(master)
        btn_frame.pack(pady=10)

        self.forward = tk.Button(
            btn_frame, text="↑", width=5, command=self.move_forward)
        self.left = tk.Button(btn_frame, text="←",
                              width=5, command=self.move_left)
        self.right = tk.Button(btn_frame, text="→",
                               width=5, command=self.move_right)
        self.backward = tk.Button(
            btn_frame, text="↓", width=5, command=self.move_backward)

        self.forward.grid(row=0, column=1)
        self.left.grid(row=1, column=0)
        self.right.grid(row=1, column=2)
        self.backward.grid(row=2, column=1)

        # Başla butonu
        self.start_btn = tk.Button(
            master, text="🟢 Başla", bg="green", fg="white", command=self.set_start)
        self.start_btn.pack(pady=10)

        # Durum etiketi
        self.status = tk.Label(master, text="Durum: Bekleniyor", fg="blue")
        self.status.pack(pady=5)

        # Kamera başlat
        self.cap = cv2.VideoCapture(0)
        self.update_frame()

    # --- Kamera görüntüsünü yenile ---
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (400, 300))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        self.master.after(30, self.update_frame)  # 30ms sonra tekrar çağır

    # --- Tuş fonksiyonları ---
    def move_forward(self):
        print("İleri git komutu gönderildi")
        self.status.config(text="İleri")

    def move_backward(self):
        print("Geri git komutu gönderildi")
        self.status.config(text="Geri")

    def move_left(self):
        print("Sola dön komutu gönderildi")
        self.status.config(text="Sol")

    def move_right(self):
        print("Sağa dön komutu gönderildi")
        self.status.config(text="Sağ")

    def set_start(self):
        print("Başlangıç konumu ayarlandı")
        self.status.config(text="Başlangıç noktası belirlendi!")
        messagebox.showinfo(
            "Başlatıldı", "Robotun başlangıç noktası ayarlandı.")

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()


# --- Arayüzü çalıştır ---
if __name__ == "__main__":
    root = tk.Tk()
    app = RobotUI(root)
    root.mainloop()
