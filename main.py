from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture("/dev/video8")

if not cap.isOpened():
    print("Kamera açılamadı.")
    exit()

cv2.namedWindow("YOLOv8 Kamera", cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Kare alınamadı.")
        break

    resized = cv2.resize(frame, (320, 240))
    results = model.predict(source=resized, stream=True, conf=0.3)

    for r in results:
        annotated = r.plot()
        if annotated is not None:
            cv2.imshow("YOLOv8 Kamera", annotated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
