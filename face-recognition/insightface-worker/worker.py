import json
import time

import cv2
import host
import numpy as np
import redis
from insightface.app import FaceAnalysis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=False)


def create_embedding(frame, app):
    faces = app.get(frame)
    emedding = faces[0].emedding
    norm_embedding = embedding / np.linalg.norm(embedding)
    embedding_bytes = embedding.astype(np.float32).tobytes()
    return embedding_bytes


def main():
    app = FaceAnalysis(root=pathtomodel)
    app.prepate(ctx_id=0)
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
                    time = data["time"]
                    nparray = np.frombuffer(jpg_bytes, dtype=np.uint8)
                    img = cv2.imdecode(nparray, cv2.IMREAD_COLOR)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    embedding = create_embedding(img, app)
                    r.xadd(
                        "face_identification_stream",
                        {
                            "camera": camera_name,
                            "time": time,
                            "embedding": embedding,
                            "image": jpg_bytes,
                        },
                    )
                    r.xack("face_processing_stream", "insightface_workers", message_id)
                except:
                    pass

        frame = XREAD
