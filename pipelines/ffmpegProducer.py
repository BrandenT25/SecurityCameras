import cv2

def run(stream_queue, ffmpeg_queue):
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