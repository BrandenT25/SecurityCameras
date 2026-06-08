from multiprocessing import Process, Queue
import camera
import time

def main() -> None:
    yolo_queue = Queue()

    p1 = Process(target=(camera.run), args=(yolo_queue,))

    p1.start
    p1.join