# teaching_controller.py

import pandas as pd

class TeachingController:
    def __init__(self, csv_path):
        df = pd.read_csv(csv_path, encoding='ISO-8859-1')
        self.lessons = df.to_dict(orient="records")
        self.index = 0

    def set_index(self, i):
        if 0 <= i < len(self.lessons):
            self.index = i

    def has_next(self):
        return self.index < len(self.lessons)

    def next_lesson(self):
        if not self.has_next():
            return None
        lesson = self.lessons[self.index]
        self.index += 1
        return {
            "id": str(lesson.get("No", self.index)),
            "title": lesson.get("Title", ""),
            "content": lesson.get("Content", "")
        }

    def show_catalog(self):
        print("\n📚 教学目录：")
        for i, l in enumerate(self.lessons):
            print(f"{i + 1}. {l.get('Title')}")
