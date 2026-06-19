from datetime import datetime
import os

import cv2
import face_recognition
import mediapipe as mp
import numpy as np
import redis

CAMERA_NAME = os.environ.get("rtsp_name")
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    min_detection_confidence=0.5, min_tracking_confidence=0.5
)
r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=False)


def equalize(frame):
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l_equalized = clahe.apply(l)
    lab_equalized = cv2.merge([l_equalized, a, b])
    equalized_frame = cv2.cvtColor(lab_equalized, cv2.COLOR_LAB2BGR)
    return equalized_frame


def normalize(frame):
    frame_float = frame.astype(np.float32)
    normalized_frame = cv2.normalize(frame_float, None, 0.0, 1.0, cv2.NORM_MINMAX)
    return normalized_frame


def blur(frame):
    blurred_frame = cv2.GaussianBlur(frame, (3, 3), 0)
    return blurred_frame


def valid_face_angle(face, face_mesh, w, h, c):
    """
    function to use mediapipes face landmarks which takes
    left eye, right eye, nose tip, left mouth corner, right mouth corner, and chin
    to determine the face angle and filter out if yaw, pitch, or roll are too much
    """
    results = face_mesh.process(face)
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            landmark_ids = [33, 263, 1, 61, 291, 199]
            points_2d = {}
            points_3d = {}

            for idx, lm in enumerate(face_landmarks.landmark):
                if idx in landmark_ids:
                    x, y = int(lm.x * w), int(lm.y * h)
                    points_2d[idx] = [x, y]
                    points_3d[idx] = [x, y, 0]

            face_2d = np.array([points_2d[i] for i in landmark_ids], dtype=np.float64)
            face_3d = np.array([points_3d[i] for i in landmark_ids], dtype=np.float64)

            model_points = np.array(
                [
                    (-225.0, 170.0, -135.0),
                    (225.0, 170.0, -135.0),
                    (0.0, 0.0, 0.0),
                    (-150.0, -150.0, -125.0),
                    (150.0, -150.0, -125.0),
                    (0.0, -330.0, -65.0),
                ]
            )

            focal_length = w
            cam_matrix = np.array(
                [[focal_length, 0, w / 2], [0, focal_length, h / 2], [0, 0, 1]],
                dtype=np.float64,
            )

            dist_matrix = np.zeros((4, 1), dtype=np.float64)

            success, rot_vec, trans_vec = cv2.solvePnP(
                model_points, face_2d, cam_matrix, dist_matrix
            )
            rmat, _ = cv2.Rodrigues(rot_vec)
            angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

            yaw = angles[1]
            pitch = angles[0]
            roll = angles[2]
            if pitch > 90:
                pitch = 180 - pitch
            elif pitch < -90:
                pitch = -180 - pitch

            if roll > 90:
                roll = 180 - roll
            elif roll < -90:
                roll = -180 - roll
            print(f"yaw: {yaw:.1f} | pitch: {pitch:.1f} | roll: {roll:.1f}")

            if abs(pitch) <= 60 and abs(yaw) <= 60 and abs(roll) <= 60:
                return True
            else:
                return False
    return False


def run(face_processing_queue):
    try:
        while True:
            currentTime = datetime.now().hour
            frame = face_processing_queue.get()
            if frame is None:
                continue
            if frame.size == 0:
                continue
            filtered_frame = equalize(frame)
            filtered_frame = blur(filtered_frame)
            rgb_frame = cv2.cvtColor(filtered_frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame, model="hog")
            h, w, c = frame.shape
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
                continue
            for index, (top, right, bottom, left) in enumerate(face_locations):
                top, bottom = max(0, top), min(h, bottom)
                left, right = max(0, left), min(w, right)

                cropped_face = filtered_frame[top:bottom, left:right]
                rgb_cropped_face = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)
                cropped_h, cropped_w, cropped_c = cropped_face.shape
                _, encodded_frame = cv2.imencode(".jpg", cropped_face)
                frame_bytes = encodded_frame.tobytes()
                if not valid_face_angle(
                    rgb_cropped_face, face_mesh, cropped_w, cropped_h, cropped_c
                ):
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
                    continue

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
