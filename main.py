from multiprocessing import Process, Queue

import alert
import stream

import camera
import ffmpegProducer
import server
import yolo

if __name__ == "__main__":
    frame_queue = Queue()
    stream_queue = Queue()
    alert_queue = Queue()
    ffmpeg_queue = Queue()

    p1 = Process(target=camera.run, args=(frame_queue))
    p2 = Process(target=yolo.run, args=(frame_queue, alert_queue, stream_queue))
    p3 = Process(target=stream.run, args=(stream_queue))
    p4 = Process(target=alert.run, args=(alert_queue))
    p5 = Process(target=ffmpegProducer.run, arg=(ffmpeg_queue))

    p1.join()
    p2.join()
    p3.join()
    p4.join()
    p5.join

