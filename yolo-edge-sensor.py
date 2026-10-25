import cv2
import requests
from ultralytics import YOLO

# Automatically downloads lightweight YOLOv8n weights on first run
model = YOLO("yolov8n.pt")

# COCO class IDs for vehicles: 2=car, 3=motorcycle, 5=bus, 7=truck
VEHICLE_CLASSES = [2, 3, 5, 7]

# Change this to your Render URL once deployed, e.g. "https://smart-green-corridor.onrender.com"
API_ENDPOINT = "http://127.0.0.1:8000/api/v1/junctions/J1/density"

# Use 0 for laptop webcam, or path to a sample traffic video file
cap = cv2.VideoCapture(0)

print("🎥 YOLOv8 Edge Traffic Density Sensor started for Junction J1...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, verbose=False)[0]
    vehicle_count = 0

    for box in results.boxes:
        cls_id = int(box.cls[0])
        if cls_id in VEHICLE_CLASSES:
            vehicle_count += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 120), 2)

    # Display live count overlay on video feed
    cv2.putText(
        frame,
        f"J1 Live Queue Count: {vehicle_count} vehicles",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )
    cv2.imshow("YOLOv8 Edge Traffic Sensor - Junction J1", frame)

    # Push live vehicle count to backend webhook every frame
    try:
        requests.post(
            API_ENDPOINT,
            json={
                "vehicle_count": vehicle_count,
                "source": "YOLOv8_LAPTOP_WEBCAM"
            },
            timeout=0.1
        )
    except Exception:
        pass

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()