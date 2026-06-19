import cv2
import time
import os

CAMERA_IP = os.environ.get("rtsp_addr")
CAMERA_NAME = os.environ.get("rtsp_name")


def run(yolo_queue) -> None:
    cam = cv2.VideoCapture(CAMERA_IP)
    while True:
        ret, frame = cam.read()
        if not ret:
            time.sleep(0.1)
            continue
        if yolo_queue.qsize() > 2:
            try:
                yolo_queue.get_nowait()
            except:
                pass

        yolo_queue.put(frame)
