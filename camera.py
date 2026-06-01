import cv2


def run(frame_queue):
    
    cam = cv2.VideoCapture(0)
    while True:
        ret, frame = cam.read()
        if not ret:
            break
        frame_queue.put(frame)
        




\