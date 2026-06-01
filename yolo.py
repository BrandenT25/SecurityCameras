from ultralytics import YOLO
import time

def run(queue):
    model = YOLO('yolo8m.pt')
    person_detected_since = None
    ALERT_DELAY = 2
    while True:
        frame = frame_queue.get()
        results = model(frame)