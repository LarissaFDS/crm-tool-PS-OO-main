from .base import Serializavel

class Task(Serializavel):
    def __init__(self, title, date):
        self.title = title
        self.date = date
        self.completed = False
    
    def to_dict(self):
        return {
            "title": self.title,
            "date": self.date,
            "completed": self.completed
        }
    
    @classmethod
    def from_dict(cls, data):
        task = cls(data["title"], data["date"])
        task.completed = data.get("completed", False)
        return task
