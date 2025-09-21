from datetime import datetime
from .base import Serializavel

class Atividade(Serializavel):
    def __init__(self, type, description):
        self.type = type
        self.description = description
        self.date = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    def to_dict(self):
        return {
            "type": self.type,
            "description": self.description,
            "date": self.date
        }
    
    @classmethod
    def from_dict(cls, data):
        atividade = cls(data["type"], data["description"])
        atividade.date = data.get("date", datetime.now().strftime("%d/%m/%Y %H:%M"))
        return atividade


# todo tracking vou nao hahaa