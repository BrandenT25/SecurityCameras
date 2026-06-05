import insightface
from insightface.app import FaceAnalysis
import os
from data.people.people_db import is_person_kown, save_person
"""
Steps:
    Retrieve photo
    run photo through faceRecognition with task_id
    match person with photo associate task_id with person
    return back to alerts
"""
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
        if cluster_file.endswith('npy'):
            cluster_embeddings = np.load(f"{CLUSTERS_DIR}/{cluster_file}")
            representative = np.mean(cluster_embeddings, axis = 0)
            score = cosine_similarity(representative, embedding)
            if score > best_score:
                best_score = score
                best_match = cluster_file
    if best_score > 0.6:
        print("found match")
        with open("{os.path.splittest(cluster_file)[0]}", "r") as f:
            cluster_metadata = json.load(f)
        status = cluster_metadata.get("status")
        if not is_person_known(cluster_metadata) || status == "unverified":
            #ALERT
        
    else:
        print("no person found")
        #alrt

def run(retrieve_queue: Queue) -> None:
    while True:
        frame = retrieve_queue.get()
        app = FaceAnalysis()
        face = app.get(frame)
        if face:
            embedding = face[0].embedding
            find_face(embedding):

