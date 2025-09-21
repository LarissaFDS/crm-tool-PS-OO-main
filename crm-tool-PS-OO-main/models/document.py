from datetime import datetime
from .base import Serializavel

# classe para gerenciamento de documentos
class Document(Serializavel):
    def __init__(self, title, file_path, doc_type="general"):
        self.title = title
        self.file_path = file_path
        self.doc_type = doc_type  # proposta, contrato, outros
        self.created_at = datetime.now().strftime("%d/%m/%Y")
        self.size = "N/A"  # calcular tamanho real do arquivo?

    def to_dict(self):
        return {
            "title": self.title,
            "file_path": self.file_path,
            "doc_type": self.doc_type,
            "created_at": self.created_at,
            "size": self.size
        }

    @classmethod
    def from_dict(cls, data):
        doc = cls(data["title"], data["file_path"], data.get("doc_type", "general"))
        doc.created_at = data.get("created_at", datetime.now().strftime("%d/%m/%Y"))
        doc.size = data.get("size", "N/A")
        return doc