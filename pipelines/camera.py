import cv2
import time

def run(frame_queue, recorder_queue):
    
    cam = cv2.VideoCapture(0)
    time.sleep(2)
    while True:
        ret, frame = cam.read()
        if not ret:
            time.sleep(0.1)
            continue

        if frame_queue.qsize() > 2:
            try:
                frame_queue.get_nowait()
            except:
                pass
        fps = cam.get(cv2.CAP_PROP_FPS)
        frame_queue.put(frame)
        recorder_queue.put((frame, fps))
        print("frame put in frame_queue") 
        




