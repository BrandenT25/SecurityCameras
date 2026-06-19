import datetime
import os
import time

import cv2
import face_recognition
import mediapipe as mp
import numpy as np
import redis

CAMERA_NAME = os.environ.get("rtsp_name")
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))


def to_alert_stream():


def equalize(frame):
    grayscale_frame = cvtColor(frame, cv2.COLOR_BGR2GRAY)
    equalized_frame = clahe.apply(grayscale_frame)
    return equalized_frame


def normalize(frame):
    frame_float = frame.astype(np.float32)
    normalized_frame = (frame_float, None, 0.0, 1.0, cv2.NORM_MINMAX)
return normalized_frame


def blur(frame):
    blurred_frame = cv2.GaussianBlur(frame, (3, 3), 0)
def valid_face_angle(face, face_mesh, w, h, c):
    

def run(face_processing_queue):
    try:
        try:
            r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=False)
        except Exception as e:
            print(f"redis connected failed {e}")
            continue

        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )
        while True:
            currentTime = datetime.now().hour
            frame = face_processing_queue.get()
            if frame is None:
                continue
            if frame.size == 0:
                continue
            filtered_frame = equalize(frame)
            filtered_frame = blur(filtered_frame)
            filtered_frame = equalize(filtered_frame)
            rgb_frame = cv2.cvtColor(filtered_frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame, model="hog")
            if not face_locations:
                _, encodded_frame = cv2.imencode(".jpg", filtered_frame)
                frame_bytes = encodded_frame.tobytes()
                r.xadd(
                    "alert_stream",
                    {
                        "camera": CAMERA_NAME,
                        "frame": frame_bytes,
                        "time": currentTime,
                        "type": "unidentified",
                    },
                    maxlen=1000,
                )
            h, w = frame.shape[:2]
            for index, (top, right, bottom, left) in enumerate(face_locations):
                top, bottom = max(0, top), min(h, bottom)
                left, right = max(0, left), min(w, right)

                cropped_face = filtered_frame[top:bottom, left:right]
                _, encodded_frame = cv2.imencode(".jpg", cropped_face)
                frame_bytes = encodded_frame.tobytes()
                r.xadd(
                    "face_processing_stream",
                    {
                        "camera": CAMERA_NAME,
                        "frame": frame_bytes,
                        "time": currentTime,
                    },
                    maxlen=1000,
                )
    except Exception as e:
        print(f"failed to process face because of {e}")
