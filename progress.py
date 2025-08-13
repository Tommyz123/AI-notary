# progress.py

import json
import os

PROGRESS_FILE = "progress.json"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="ISO-8859-1") as f:
            data = json.load(f)
            return data.get("current_index", 0)
    return 0

def save_progress(index):
    with open(PROGRESS_FILE, "w", encoding="ISO-8859-1") as f:
        json.dump({"current_index": index}, f, indent=2)
