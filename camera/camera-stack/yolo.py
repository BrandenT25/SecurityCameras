import time
import os
from ultralytics import YOLO
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent().parent()
CONFIG_FILE = os.path.join(BASE_DIR, "shared", "config","yoloConfig.json" )
with open(CONFIG_FILE, "r") as f:
    config_data = json.load(f)
ALERT_DELAY = config_data["alert_delay"]
ALERT_COOLDOWN = config_data["alert_cooldown"]
GRACE_PERIOD = config_data["grace_period"]
MODEL = config_data["model"] 
person_timers = {}
last_seen_timers = {}
alert_cooldowns = {}
def run(yolo_queue):
    model = YOLO(MODEL)
    while frame is None:
        time.sleep(0.1)
    start_time = time.time()
    results = model.track(frame, persist=True, conf=0.4,classes=[0], verbose=False )
    if yolo_queue.qsize() > 2:
        try



    while True:
        frame = yolo_queue.get()