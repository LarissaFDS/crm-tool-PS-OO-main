from datetime import datetime
import time
from .base import Pessoa
from .atividade import Atividade
from .task import Task
from .document import Document

class Contato(Pessoa):  # Herda de Pessoa
    def __init__(self, name, email, telefone, empresa="", notas="", id=None):
        super().__init__(name, email)  # Chama construtor da classe pai
        self.id = id if id is not None else int(time.time() * 1000) #Se um ID for fornecido, usa. Senão, cria um novo baseado no tempo.
        self.telefone = telefone
        self.empresa = empresa
        self.notas = notas
        self.sales_stage = "Lead"
        self.stage_history = ["Lead"]
        self.activities = []
        self.tasks = []
        self.documents = []  # documentos

    def to_dict(self):
        return {
            "id": self.id,
            "name": self._name,  # atributo privado
            "email": self._email,
            "telefone": self.telefone,
            "empresa": self.empresa,
            "notas": self.notas,
            "sales_stage": self.sales_stage,
            "stage_history": self.stage_history,
            "created_at": self._created_at,
            "activities": [a.to_dict() for a in self.activities],
            "tasks": [t.to_dict() for t in self.tasks],
            "documents": [d.to_dict() for d in self.documents]
        }

    @classmethod
    def from_dict(cls, data):
        c = cls(data["name"], data["email"], data["telefone"], 
                data.get("empresa", ""), data.get("notas", ""), id=data.get("id"))
        #c.id = data["id"] tirei isso e coloquei direto no construtor
        c.sales_stage = data.get("sales_stage", "Lead")
        c.stage_history = data.get("stage_history", ["Lead"])
        c._created_at = data.get("created_at", datetime.now().strftime("%d/%m/%Y"))
        c.activities = [Atividade.from_dict(a) for a in data.get("activities", [])]
        c.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        c.documents = [Document.from_dict(d) for d in data.get("documents", [])]
        return c

    def add_document(self, title, file_path, doc_type="general"):
        """Adiciona documento ao contato"""
        doc = Document(title, file_path, doc_type)
        self.documents.append(doc)

class Lead(Pessoa):  # Herda de Pessoa
    def __init__(self, name, email, source="Website", id=None):
        super().__init__(name, email)
        self.id = id if id is not None else int(time.time() * 1000)
        self.source = source
        self.score = 0
        self.converted = False

    def to_dict(self):
        return {
            "id": self.id,
            "name": self._name,
            "email": self._email,
            "source": self.source,
            "created_at": self._created_at,
            "score": self.score,
            "converted": self.converted
        }

    @classmethod
    def from_dict(cls, data):
        lead = cls(data["name"], data["email"], data.get("source", "Website"), id=data.get("id"))
        lead._created_at = data.get("created_at", datetime.now().strftime("%d/%m/%Y"))
        lead.score = data.get("score", 0)
        lead.converted = data.get("converted", False)
        return lead