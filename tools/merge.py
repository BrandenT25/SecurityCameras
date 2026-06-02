import numpy as np
import os
import sys

def merge_clusters(cluster_a, cluster_b):
    path_a = f"clusters/{cluster_a}"
    path_b = f"clusters/{cluster_b}"
    
    if not os.path.exists(path_a) or not os.path.exists(path_b):
        print("one or both clusters not found")
        return
    
    embeddings_a = np.load(path_a)
    embeddings_b = np.load(path_b)
    
    merged = np.vstack([embeddings_a, embeddings_b])
    np.save(path_a, merged)
    os.remove(path_b)
    
    print(f"merged {cluster_b} into {cluster_a} — {len(merged)} total embeddings")

def label_cluster(cluster, name):
    old_path = f"clusters/{cluster}"
    new_path = f"clusters/{name}.npy"
    
    if not os.path.exists(old_path):
        print("cluster not found")
        return
    
    os.rename(old_path, new_path)
    print(f"renamed {cluster} to {name}.npy")

if __name__ == "__main__":
    command = sys.argv[1]
    
    if command == "merge":
        merge_clusters(sys.argv[2], sys.argv[3])
    elif command == "label":
        label_cluster(sys.argv[2], sys.argv[3])
    elif command == "list":
        for f in os.listdir("clusters/"):
            embeddings = np.load(f"clusters/{f}")
            print(f"{f} — {len(embeddings)} samples")