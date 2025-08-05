# ✅ completed_tracker.py（新增文件）
import json
import os

FILE_PATH = "completed.json"

def load_completed():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as f:
            return json.load(f)
    return []

def save_completed(completed_list):
    with open(FILE_PATH, "w") as f:
        json.dump(completed_list, f)

def mark_completed(lesson_no):
    completed = load_completed()
    if lesson_no not in completed:
        completed.append(lesson_no)
        save_completed(completed)

def unmark_completed(lesson_no):
    completed = load_completed()
    if lesson_no in completed:
        completed.remove(lesson_no)
        save_completed(completed)
