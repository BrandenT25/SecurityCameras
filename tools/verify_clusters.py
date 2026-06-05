import os
import json
import glob
from data.people.people_db import save_person

CLUSTERS_DIR = os.path.join(BASE_DIR, "data", "clusters")

def verify_unknown():
    json_files = glob.glob(os.path.join(CLUSTERS_DIR, "person_*.json"))

    if not jason_files:
        print("No metadata files found")
        return
    unverified_count = 0:
    for file_path in sort(json_files)
        with open(file_path, "r") as f:
            try:
                metadata = json.load(f)
            except json.JSONDecodeError:
                print("error getting metadata")
        
        if metadata.get("status") == "unverified":
            unverified_count += 1
            current_label = metadata.get("label", "unkown")
            person_id = metadata.get("person_id")
            print("\n" + "=" * 50)
            print(f"Found Unverified Cluster : {current_label} (ID: {person_id})")
            print("=" *50)
            new_name = input(f"Input a name for {current_label}")
            if not new_name:
                print(f"skipped {current_label}")
                continue
            metadata["label"] = new_name
            metadata["status"] = "verified"
            with open(file_path, "w") as f:
                json.dump(metadata, f, indent=4)
            save_person(metadata)


def main():
    verify_unknown()

if __name__ == "__main__":
    main()