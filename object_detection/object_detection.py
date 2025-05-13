from ultralytics import YOLO
import cv2
from object_detection.danger_scores import get_danger_score
from mapping.weighted_grid_map import WeightedGridMap

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture("/dev/video8")

grid = WeightedGridMap(width=100, height=100)


def image_to_grid(x_pixel, y_pixel, img_width=320, img_height=240, grid_width=100, grid_height=100):
    gx = int((x_pixel / img_width) * grid_width)
    gy = int((y_pixel / img_height) * grid_height)
    return gx, gy


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
        boxes = r.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            score = get_danger_score(label)

            x1, y1, x2, y2 = box.xyxy[0]  # bbox koordinatları
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            gx, gy = image_to_grid(center_x, center_y)
            grid.update_danger_zone(gx, gy, label)

        annotated = r.plot()
        if annotated is not None:
            cv2.imshow("YOLOv8 Kamera", annotated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Programdan çıkınca grid'i yazdır:
grid.print_grid()
