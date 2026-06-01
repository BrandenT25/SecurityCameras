import time

from ultralytics import YOLO


def run(frame_queue, alert_queue, stream_queue):
    model = YOLO("yolo8m.pt")
    person_detected_since = None
    ALERT_DELAY = 2
    GRACE_PERIOD = 0.2
    person_timers = {}
    last_seen_timers = {}
    while True:
        frame = frame_queue.get()
        if frame is None:
            break
        start_time = time.time()

        results = model.track(frame, persist=True, conf=0.6, classes=[0], verbose=False)

        stream_queue.put(results)
        boxes = results[0].boxes
        visible_ids = set()
        if boxes is not None and boxes.id is not None:
            track_ids = boxes.id.cpu().numpy().astype(int)
            for track_id in track_ids:
                visible_ids.add(track_id)
                if track_id not in person_timers:
                    person_timers[track_id] = start_time
                last_seen_timers[track_id] = start_time

                duration = start_time - person_timers[track_id]

                if duration >= ALERT_DELAY:
                    # Alert Logic
                    alert_queue.put(results)
                    del person_timers[track_id]
                    if track_id in last_seen_timers:
                        del last_seen_timers[track_id]
        for track_id in list(person_timers.keys()):
            if track_id not in visible_ids:
                time_since_missing = start_time - last_seen_timers.get(
                    track_id, start_time
                )
                if time_since_missing > GRACE_PERIOD:
                    del person_timers[track_id]
                if track_id in last_seen_timers:
                    del last_seen_timers[track_id]
