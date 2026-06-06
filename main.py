from multiprocessing import Process, Queue
from pipelines import alert, server, camera, ffmpegProducer, yolo, recorder, faceRecognition, enroll, retrievePerson
import logging
import time
"""
def setup_logging(level = logging.DEBUG) -> None:
    root = logging.getLogger("pipeline")
    root.setLevel(level)

    fmt = logging.formater(
        "%(asctime)s | %(levelname)-8s | %(name)-20s | %(threadname)-15s | %(message)s"
        datefmt = "%H:%M:%S" 
    )
    console = logging.streamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)

    file = logging.fileHandler("pipeline.log")
    file.setLevel(logging.DEBUG)
    file.setFormatter(fmt)
    root.addHandler(console)
    root.addHandler(file)
"""
if __name__ == "__main__":
    # Setup pipelines for each process as Queue objects
    frame_queue = Queue()
    stream_queue = Queue()
    retrieve_queue = Queue()
    alert_queue = Queue()
    ffmpeg_queue = Queue()
    recording_queue = Queue()
    face_rec_queue = Queue()
    """
    direct functions through these pipelines and define 
    which functions receive and pass through which pipelines
    """
    p1 = Process(target=camera.run, args=(frame_queue, recording_queue))
    p2 = Process(target=yolo.run, args=(frame_queue, stream_queue, face_rec_queue))
    p3 = Process(target=faceRecognition.run, args=(face_rec_queue, retrieve_queue,))
    time.sleep(30)
    p4 = Process(target=retrievePerson.run, args=(retrieve_queue,))
    p5 = Process(target=ffmpegProducer.run, args=(stream_queue, ffmpeg_queue))
    p6 = Process(target=recorder.run, args=(recording_queue,))
    p7 = Process(target=alert.run, args=(alert_queue,))
    p8 = Process(target=server.run, args=(ffmpeg_queue,))
    p9 = Process(target=enroll.run, args = ())
    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p5.start()
    p6.start()
    p7.start()
    p8.start()
    p9.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()
    p5.join()
    p6.join()
    p7.join()
    p8.join()
    p9.join()