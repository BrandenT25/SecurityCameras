import json
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DBFILE = os.path.join(BASE_DIR, "people.json") 

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
    incoming_id = metadata_dict.get("person_id")
    incoming_label = metadata_dict.get("label", "").strip()
    if not incoming_label:
        print("cant save an empty name")
        return False

    current_people = load_people()
    for i, p in enumerate(current_people):
        if p.get("person_id") == incoming_id:
            current_people[i] = metadata_dict
            save_people(current_people)
            return True
            
    current_people.append(metadata_dict)
    save_people(current_people)
    return True

def is_person_known(metadata_dict):
    incoming_label = metadata_dict.get("label", "").strip().lower()
    if not incoming_label:
        return False
    current_people = load_people()
    return any(p.get("label", "").lower() == incoming_label for p in current_people)