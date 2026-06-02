from datetime import date, datetime, timedelta
import cv2
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORDINGS_DIR = os.path.join(BASE_DIR, "recordings")
def run(recorder_queue):
    start_date = date.today()
    start_hour = datetime.now().hour
    current_minute = datetime.now().minute
    frame, fps = recorder_queue.get()
    height, width, channels = frame.shape
    frame_size = (width, height)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    os.makedirs(f'{RECORDINGS_DIR}/video-{start_date}', exist_ok=True)
    writer = cv2.VideoWriter(f"{RECORDINGS_DIR}/video-{start_date}/video_{start_hour}_{current_minute}.mp4", fourcc, 30, frame_size )
    writer.write(frame)
    while True:
        frame, fps = recorder_queue.get()
        current_hour = datetime.now().hour
        current_date = date.today()
        if current_date != start_date:
            print("making new date folder")
            if writer:
                writer.release()
            os.makedirs(f'{RECORDINGS_DIR}/video-{current_date}', exist_ok=True)
            writer = cv2.VideoWriter(f"{RECORDINGS_DIR}/video-{start_date}/video_{start_hour}_{current_minute}.mp4", fourcc, 30, frame_size )
            start_date = current_date
            start_hour = current_hour
        elif current_hour != start_hour:
            print("making new video file")
            if writer:
                writer.release()
            writer = cv2.VideoWriter(f"{RECORDINGS_DIR}/video-{start_date}/video_{start_hour}_{current_minute}.mp4", fourcc, 30, frame_size )
            start_hour = current_hour
        print("writing video")
        writer.write(frame)


    