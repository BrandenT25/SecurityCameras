import cv2
import numpy as np
import redis
from insightface.app import FaceAnalysis
import os

MODEL_PATH = os.environ.get("MODELS_DIR")
r = redis.Redis(host="redis", port=6379, db=0, decode_responses=False)
app = FaceAnalysis(root=MODEL_PATH)
app.prepare(ctx_id=0)


def create_embedding(frame, app):
    faces = app.get(frame)
    embedding = faces[0].embedding
    norm_embedding = embedding / np.linalg.norm(embedding)
    embedding_bytes = norm_embedding.astype(np.float32).tobytes()
    return embedding_bytes


def main():
    try:
        r.xgroup_create(
            "face_processing_stream", "insightface_workers", id="0", mkstream=True
        )
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise
    while True:
        messages = r.xreadgroup(
            groupname="insightface_workers",
            consumer_name="worker-1",
            streams={"face_processing_stream": ">"},
            count=1,
            block=2000,
        )
        if not messages:
            continue
        for stream, entries in messages:
            for message_id, data in entries:
                try:
                    jpg_bytes = data["frame"]
                    camera_name = data["camera"]
                    frame_time = data["time"]
                    nparray = np.frombuffer(jpg_bytes, dtype=np.uint8)
                    img = cv2.imdecode(nparray, cv2.IMREAD_COLOR)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    embedding = create_embedding(img, app)
                    r.xadd(
                        "face_identification_stream",
                        {
                            "camera": camera_name,
                            "time": frame_time,
                            "embedding": embedding,
                            "image": jpg_bytes,
                        },
                    )
                    r.xack("face_processing_stream", "insightface_workers", message_id)
                except Exception as e:
                    print(f"failed with {e}")


if __name__ == "__main__":
    main()
