import insightface
from insightface.app import FaceAnalysis
import cv2
import os
import numpy as np
import time
import json
from data.people.people_db import is_person_known, save_person
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FACES_DIR = os.path.join(BASE_DIR, "data", "faces")
CLUSTERS_DIR = os.path.join(BASE_DIR, "data", "clusters")
INSIGHTFACE_ROOT = os.path.join(BASE_DIR, "models", "insightface")
def cosine_similarity(a, b) -> float:
    '''
    Basic function to extract the angle of vectors and compare them to each other
    '''
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def cluster_assign(embedding, file_name) -> None:
    '''
    function that takes the npy embedding of a picture and assigns it to a npy vector cluster based on cosine similarity
    '''
    os.makedirs(CLUSTERS_DIR, exist_ok=True)
    best_match = None
    best_score = 0

    for cluster_file in os.listdir(f'{CLUSTERS_DIR}/'):
        if cluster_file.endswith(".npy"):
            cluster_embeddings = np.load(f"{CLUSTERS_DIR}/{cluster_file}")
            representative = np.mean(cluster_embeddings, axis = 0)
            score = cosine_similarity(embedding, representative)
            if score > best_score:
                best_score = score
                best_match = cluster_file
    if best_score > 0.6:
        existing = np.load(f"{CLUSTERS_DIR}/{best_match}")
        updated = np.vstack([existing, embedding ])
        np.save(f"{CLUSTERS_DIR}/{best_match}", updated)
    
    else:
        existing_clusters = [f for f in os.listdir(f"{CLUSTERS_DIR}/") if f.endswith(".npy")]
        if existing_clusters:
            numbers = [int(f.replace("person_", "").replace(".npy", "")) for f in existing_clusters]
            next_id = max(numbers) + 1
        else:
            next_id = 1
    
        np.save(f"{CLUSTERS_DIR}/person_{next_id:03d}.npy", embedding.reshape(1, -1))
        json_filename = f"{CLUSTERS_DIR}/person_{next_id:03d}.json"
        metadata = {
            "label" : f"unknown_{next_id:03d}",
            "person_id" : next_id,
            "status": "unverified"
        }
        with open(json_filename, "w") as f:
            json.dump(metadata, f, indent=4)
        save_person(metadata)

def enroll_new_faces(app) -> None:
    """
    Function that takes a jpg image and creates a npy embedding 
    using insight face then calls the cluster assign function
    """
    for filename in os.listdir(FACES_DIR):
        if filename.endswith(".jpg"):
            print(f"processing {filename}")
            img_path = os.path.join(FACES_DIR, filename)
            npy_path = img_path.replace(".jpg", ".npy")
            if os.path.exists(npy_path):
                print(f"already has embedding, skipping")
                continue
            img = cv2.imread(img_path)
            faces = app.get(img)
            print(f"faces detected: {len(faces)}")
            if faces:
                embedding = faces[0].embedding
                np.save(npy_path, embedding)
                cluster_assign(embedding, filename)
                os.makedirs(f"{FACES_DIR}/processed", exist_ok=True)
                os.rename(img_path, f"{FACES_DIR}/processed/{filename}")
                os.rename(npy_path, f"{FACES_DIR}/processed/{filename.replace('.jpg', '.npy')}")
                print(f"saved embedding for {filename}")
            else:
                print(f"no face found in {filename}")

def run() -> None:
    # build an object of insightface's FaceAnalysis
    app = FaceAnalysis(root=INSIGHTFACE_ROOT)
    app.prepare(ctx_id=0) # ctx_id=0 indicates that you want to use gpu for processes make sure you have cuda installed
    while True:
        # enrolls new faces detected every 5 minutes
        enroll_new_faces(app)
        time.sleep(300)