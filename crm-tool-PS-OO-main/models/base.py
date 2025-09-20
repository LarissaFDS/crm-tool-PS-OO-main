from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

# Enum para tipos de usuário (usar para dashboards e permissões dps)
class UserRole(Enum):
    ADM = "administrador"
    VENDEDOR = "vendedor"
    MARKETING = "marketing"
    CLIENTE = "cliente"

# Classe abstrata base para entidades que podem ser persistidas
class Serializavel(ABC):
    @abstractmethod
    def to_dict(self):
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data):
        pass

# Classe base para pessoas (implementando herança)
class Pessoa(Serializavel):
    def __init__(self, name, email):
        self._name = name  # Atributo privado para melhor encapsulamento
        self._email = email
        self._created_at = datetime.now().strftime("%d/%m/%Y")
    
    # Properties para encapsulamento
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        if not value or not value.strip():
            raise ValueError("Nome não pode estar vazio")
        self._name = value.strip()
    
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, value):
        if "@" not in value:
            raise ValueError("Email inválido")
        self._email = value
