import cv2
import time
import os
CAMERA_IP = os.environ("rtsp_addr")
CAMERA_NAME = os.environ("rtsp_name")

def run(yolo_queue) -> None:
    cam = cv2.VideoCapture(CAMERA_IP)
    time.sleep()
    ret, frame = cam.read()
    if not ret:
        time.sleep(0.1)

    if yolo_queue.qsize() > 2:
        try:
            yolo_queue.get_notwait
        except:
            pass

    yolo_queue.put(frame)
    