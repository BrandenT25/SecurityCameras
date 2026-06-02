import time
import os
from ultralytics import YOLO
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODELS_DIR = os.path.join(BASE_DIR, "models")

def run(frame_queue, alert_queue, stream_queue, face_rec_queue):
    model = YOLO(f"{MODELS_DIR}/yolov8n.pt")
    model.to("cuda")
    ALERT_DELAY = 2
    alert_cooldowns = {}
    ALERT_COOLDOWN = 30
    GRACE_PERIOD = 4.0
    person_timers = {}
    last_seen_timers = {}
    while True:
        frame = frame_queue.get()
        print("yolo got a frame")
        if frame is None:
            break
        start_time = time.time()

        results = model.track(frame, persist=True, conf=0.4, classes=[0], verbose=False)
        annotated = results[0].plot()
        if stream_queue.qsize() > 2:
            try:
                stream_queue.get_nowait()
            except:
                pass
        stream_queue.put(annotated)
        boxes = results[0].boxes
        visible_ids = set()
        if boxes is not None and boxes.id is not None:
            
            track_ids = boxes.id.cpu().numpy().astype(int)
            print(f"tracking {len(track_ids)} people")
            for track_id in track_ids:
                visible_ids.add(track_id)
                if track_id not in person_timers:
                    person_timers[track_id] = start_time
                last_seen_timers[track_id] = start_time

                duration = start_time - person_timers[track_id]
                print(f"track_id: {track_id} | duration: {duration:.2f}s")  # add this
                if duration >= ALERT_DELAY:
                    last_alert = alert_cooldowns.get(track_id, 0)
                    time_since_alert = start_time - last_alert
                    if start_time - last_alert >= ALERT_COOLDOWN:
                    # Alert Logic
                        print("FIRING ALERT")
                        alert_queue.put({
                            "Timestamp" : start_time,
                            "camera" : 0,
                            "confidence": float(boxes.conf[list(track_ids).index(track_id)].item()),
                            "track_id": track_id

                        })
                        face_rec_queue.put(frame)
                        alert_cooldowns[track_id] = start_time
                        del person_timers[track_id]
                        if track_id in last_seen_timers:
                            del last_seen_timers[track_id]
        else:
            print(f"boxes.id is None")
        for track_id in list(person_timers.keys()):
            if track_id not in visible_ids:
                time_since_missing = start_time - last_seen_timers.get(
                    track_id, start_time
                )
                if time_since_missing > GRACE_PERIOD:
                    del person_timers[track_id]
                if track_id in last_seen_timers:
                    del last_seen_timers[track_id]
