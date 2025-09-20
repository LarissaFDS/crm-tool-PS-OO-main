# Exportar todas as classes dos modelos pra facilitar
from .base import UserRole, Serializavel, Pessoa
from .contact import Contato, Lead
from .atividade import Atividade
from .task import Task
from .document import Document
from .campanha import EmailCampanha

__all__ = [
    'UserRole',
    'Serializavel', 
    'Pessoa',
    'Contato',
    'Lead',
    'Atividade',
    'Task',
    'Document',
    'EmailCampanha'
]
