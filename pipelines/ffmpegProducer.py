import cv2

def run(stream_queue : Queue, ffmpeg_queue : Queue) -> None:
    """
    Function that takes in the yolo frame and encodes it in ffmpeg format and transfers it to the web server
    """
    while True:
        frame = stream_queue.get()
        if frame is None:
            break
        print(f"frame type: {type(frame)}, shape: {frame.shape if hasattr(frame, 'shape') else 'no shape'}")
        ret, buffer = cv2.imencode('.jpg', frame)
        print(f"encode success: {ret}, buffer size: {len(buffer) if ret else 0}")
        if ret:
            if ffmpeg_queue.qsize() > 2:
                try:
                    ffmpeg_queue.get_nowait()
                except:
                    pass
            ffmpeg_queue.put(buffer.tobytes())
            print("frame encoded and sent to ffmpeg_queue")