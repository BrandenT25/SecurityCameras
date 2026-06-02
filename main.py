from multiprocessing import Process, Queue
from pipelines import alert
from pipelines import server
from pipelines import camera
from pipelines import ffmpegProducer
from pipelines import yolo
from pipelines import recorder
from pipelines import faceRecognition
from pipelines import enroll

if __name__ == "__main__":
    frame_queue = Queue()
    stream_queue = Queue()
    alert_queue = Queue()
    ffmpeg_queue = Queue()
    recording_queue = Queue()
    face_rec_queue = Queue()

    p1 = Process(target=camera.run, args=(frame_queue, recording_queue))
    p2 = Process(target=yolo.run, args=(frame_queue, alert_queue, stream_queue, face_rec_queue))
    p3 = Process(target=faceRecognition.run, args=(face_rec_queue,))
    p4 = Process(target=ffmpegProducer.run, args=(stream_queue, ffmpeg_queue))
    p5 = Process(target=recorder.run, args=(recording_queue,))
    p6 = Process(target=alert.run, args=(alert_queue,))
    p7 = Process(target=server.run, args=(ffmpeg_queue,))
    p8 = Process(target=enroll.run, args = ())
    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p5.start()
    p6.start()
    p7.start()
    p8.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()
    p5.join()
    p6.join()
    p7.join()
    p8.join()