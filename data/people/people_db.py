import json
import os
DBFILE = "people.json"

def load_people():
    if not os.path.exists(DBFILE):
        return []
    try:
        with open(DBFILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_people(data):
    with open(DBFILE, "w") as f:
        json.dump(data, f, indent = 4)

def save_person(metadata_dict):
    incoming_label = metadata_dict.get("label", "").strip()
    if not clean_name:
        print("cant save an empty name")
        return False

    current_people = load_people()
    if any(p.get("label", "").lower == incoming_label.lower() for p in current_people):
        print(f"{incoming_label} already in registry")
        return True
    current_people.append(metadata_dict)
    save_person(current_people)
    return True

def is_person_known(metadata_dict):
    incoming_label = metadata_dict.get("label", "").strip().lower()
    if not incoming_label:
        return False
    current_people = load_people()
    return any(p.get("label", "").lower() == clean_name for p in current_people)