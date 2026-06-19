from multiprocessing import Process, Queue

import camera
import face_processing
import yolo


def main() -> None:
    yolo_queue = Queue()
    face_processing_queue = Queue()
    p1 = Process(target=(camera.run), args=(yolo_queue, face_processing_queue,))
    p2 = Process(target=(face_processing.run), args=(face_processing_queue,))

    p1.start
    p2.start
    

    p1.join
    p2.join
