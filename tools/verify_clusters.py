import os
import json
import glob
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from data.people.people_db import save_person
CLUSTERS_DIR = os.path.join(BASE_DIR, "data", "clusters")

def verify_unknown():
    json_files = glob.glob(os.path.join(CLUSTERS_DIR, "person_*.json"))

    if not json_files:
        print("No metadata files found")
        return
    unverified_count = 0
    for file_path in sorted(json_files):
        with open(file_path, "r") as f:
            try:
                metadata = json.load(f)
            except json.JSONDecodeError:
                print("error getting metadata")
                continue
        
        if metadata.get("status") == "unverified":
            unverified_count += 1
            current_label = metadata.get("label", "unknown")
            person_id = metadata.get("person_id")
            print("\n" + "=" * 50)
            print(f"Found Unverified Cluster : {current_label} (ID: {person_id})")
            print("=" *50)
            new_name = input(f"Input a name for {current_label} : ")
            if not new_name:
                print(f"skipped {current_label}")
                continue
            metadata["label"] = new_name
            metadata["status"] = "verified"
            with open(file_path, "w") as f:
                json.dump(metadata, f, indent=4)
            save_person(metadata)
            file = os.path.splitext(os.path.basename(file_path))[0]
            os.rename(f"{CLUSTERS_DIR}/{file}.json", f"{CLUSTERS_DIR}/{new_name}.json")
            os.rename(f"{CLUSTERS_DIR}/{file}.npy", f"{CLUSTERS_DIR}/{new_name}.npy")


def main():
    verify_unknown()

if __name__ == "__main__":
    main()