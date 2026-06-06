import insightface
from insightface.app import FaceAnalysis
import os
from data.people.people_db import is_person_known, save_person
import numpy as np
import json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSIGHTFACE_ROOT = os.path.join(BASE_DIR, "models", "insightface")

"""
Steps:
    Retrieve photo
    run photo through faceRecognition with task_id
    match person with photo associate task_id with person
    return back to alerts
"""
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CLUSTERS_DIR = os.path.join(BASE_DIR, "data", "clusters")
def cosine_similarity(a, b) -> float:
    '''
    Basic function to extract the angle of vectors and compare them to each other
    '''
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def find_face(embedding):
    person = None
    best_score = 0
    best_match = None
    for cluster_file in os.listdir(f'{CLUSTERS_DIR}'):
        if cluster_file.endswith('.npy'):
            cluster_embeddings = np.load(f"{CLUSTERS_DIR}/{cluster_file}")
            representative = np.mean(cluster_embeddings, axis = 0)
            score = cosine_similarity(representative, embedding)
            if score > best_score:
                best_score = score
                best_match = cluster_file
    if best_score > 0.6:
        print("found match")
        json_path = os.path.join(CLUSTERS_DIR, os.path.splitext(best_match)[0] + ".json")
        with open(json_path, "r") as f:
            cluster_metadata = json.load(f)
        status = cluster_metadata.get("status")
        if not is_person_known(cluster_metadata) or status == "unverified":
            
        
    else:
        print("no person found")
        #alrt

def run(retrieve_queue) -> None:
    app = FaceAnalysis(root=INSIGHTFACE_ROOT)
    app.prepare(ctx_id=0)
    while True:
        frame = retrieve_queue.get()
        face = app.get(frame)
        if face:
            embedding = face[0].embedding
            find_face(embedding)

