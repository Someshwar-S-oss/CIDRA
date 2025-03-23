import cv2
from ultralytics import YOLO
import numpy as np
from collections import defaultdict
import os

def run_vehicle_detection():
    model = YOLO('yolo11l.pt')
    class_list = model.names

    print("Starting vehicle detection...")

    # cap = cv2.VideoCapture('../../Video/4.mp4')
    cap = cv2.VideoCapture('./detect/video.mp4')

    class_counts = defaultdict(int)

    frame_counter = 0
    while cap.isOpened():
        fps = cap.get(cv2.CAP_PROP_FPS)
        ret, frame = cap.read()
        if not ret:
            break

        frame_counter += 1

        results = model.track(frame, persist=True, classes=[1, 2, 3, 5, 6, 7])

        if results[0].boxes.data is not None:
            # Get the detected boxes, their class indices, and track IDs
            boxes = results[0].boxes.xyxy.cpu()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            class_indices = results[0].boxes.cls.int().cpu().tolist()
            confidences = results[0].boxes.conf.cpu()

        for box, track_id, class_idx, conf in zip(boxes, track_ids, class_indices, confidences):
                x1, y1, x2, y2 = map(int, box)
                cx = (x1 + x2) // 2  # Calculate the center point
                cy = (y1 + y2) // 2

                class_name = class_list[class_idx]
        
                cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
                cv2.putText(frame, f"ID: {track_id} {class_name}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                if frame_counter % 8 == 0:
                    time = frame_counter / fps
                    logput = f"{{vehicle type: {class_name} time: {time:.2f}s}},"
                    print(logput)

                frame_counter = frame_counter + 1

        cv2.imshow("Vehicle Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_vehicle_detection()
