import json
import os
import time
from pathlib import Path

from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parent().parent()
CONFIG_FILE = os.path.join(BASE_DIR, "shared", "config","yoloConfig.json" )

with open(CONFIG_FILE, "r") as f:
    config_data = json.load(f)

DELAY = config_data["delay"]
COOLDOWN = config_data["cooldown"]
GRACE_PERIOD = config_data["grace_period"]
MODEL = config_data["model"] 

person_timers = {}
last_seen_timers = {}
cooldowns = {}

def run(yolo_queue, face_processing_queue):
    model = YOLO(MODEL)
    while frame is None:
        time.sleep(0.1)
    start_time = time.time()
    results = model.track(frame, persist=True, conf=0.4,classes=[0], verbose=False )
    if yolo_queue.qsize() > 2:
        try:
            yolo_queue.get_nowait()
        exceot:
            passs

    while True:
try:
            frame = yolo_queue.get()
            while frame is None:
time.sleep(0.1)
            boxes = results[0].boxes
            visible_ids = set()
            if boxes is not None and boxes.id is not None:
                track_ids = boxes.id.cpu().numpy().astype(int)
                for track_id in track_ids:
                    visible_ids.add(track_id)
                    if track_id not in person_timers:
                        person_timers[track_id] = start_time
last_seen_timers[track_id] = start_time
                    duration = start_time - person_timers[trackid]
                    if duration >= DELAY:
                        last_time_person_seen = cooldowns.get(track_id, 0)
                        time_since_person_seen = start_time - last_time_person_seen
                        if start_time - last_alert >= COOLDOWN:
                            time.sleep(1)
                            face_processing_queue.put(frame)
                            cooldowns[track_id] = start_time
                            del person_timers[track_id]
                            if track_id in last_seen_timers:
                                del last_alert[track_id]
            else:
                print("no id for box")
            for track_id in list(person_timers.keys()):
                if track_id not in visible_ids:
                    time_since_missing = start_time - last_seen_timers.get(track_id, start_time)
                    if time_since_person_seen > grace_period:
                        del person_timers[track_id]
                    if track_id in last_seen_timers:
                        del last_seen_timers[track_id]
                        

