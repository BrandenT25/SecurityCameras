import face_recognition
import cv2
import numpy as np
import mediapipe as mp 
import time
import os 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FACES_DIR = os.path.join(BASE_DIR, "data", "faces")
def is_sharp(image, threshold=100) -> bool:
    """
    Function to filter if image is image has enough sharpness
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    return variance > threshold


def is_large_enough(crop_w : int, crop_h : int, min_size=40) -> bool:
    """
    Function to filter images too small current 40x40
    """
    return crop_w >= min_size and crop_h >= min_size

def valid_face_angle(face, face_mesh, w : int, h : int, c) -> bool:
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

            model_points = np.array([
                (-225.0, 170.0, -135.0),
                (225.0, 170.0, -135.0),
                (0.0, 0.0, 0.0),
                (-150.0, -150.0, -125.0),
                (150.0, -150.0, -125.0),
                (0.0, -330.0, -65.0),
            ])

            focal_length = w
            cam_matrix = np.array([
                [focal_length, 0, w / 2],
                [0, focal_length, h / 2],
                [0, 0, 1]
            ], dtype=np.float64)

            dist_matrix = np.zeros((4, 1), dtype=np.float64)

            success, rot_vec, trans_vec = cv2.solvePnP(model_points, face_2d, cam_matrix, dist_matrix)
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


def run(face_rec_queue, retrieve_queue) -> None:
    """
    Function That takes in the yolo frame and converts it into an rgb frame then recognized face locations
    and crops the images based on those locations
    """
    try:
        print("running facial recognition")
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        print("face mesh ready")  
        id = 0
        while True:
            print("waiting for frame...")  
            frame = face_rec_queue.get()
            print(f"face rec got a frame: {frame.shape}")
            if frame is None:
                continue
            if frame.size == 0:
                continue
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            face_locations = face_recognition.face_locations(rgb_frame, model="hog")
            for index, (top, right, bottom, left) in enumerate(face_locations):
                h, w, c = frame.shape
                top, bottom = max(0, top), min(h, bottom)
                left, right = max(0, left), min(w, right)
                
                cropped_face = frame[top:bottom, left:right]
                retrieve_queue.put(cropped_face)
                crop_h, crop_w, crop_c = cropped_face.shape
                print(f"crop size: {crop_w}x{crop_h}")
                rgb_crop = cv2.cvtColor(cropped_face, cv2.COLOR_BGR2RGB)
                if valid_face_angle(rgb_crop,face_mesh, crop_w, crop_h, crop_c) and is_large_enough(crop_w, crop_h) and is_sharp(cropped_face):
                    timestamp = int(time.time() * 1000)
                    cv2.imwrite(f"{FACES_DIR}/face_{index + 1}_{timestamp}.jpg", cropped_face) 
                    print("valid face")
                else:   
                    print("not valid face")


                

                id += 1
    except Exception as e:
        print(f'face recerror {e}')
        import traceback
        traceback.print_exc()
