from abc import ABC, abstractmethod
from .base import LeadSource

class PessoaFactory(ABC): 
    @abstractmethod
    def create_person(self, **kwargs):
        pass
    
    def create_with_validation(self, **kwargs): #validação comum
        self._validate_basic_data(kwargs)
        return self.create_person(**kwargs)
    
    def _validate_basic_data(self, data): #qualqur pessoa
        if not data.get('name') or not data.get('name').strip():
            raise ValueError("Nome é obrigatório ;)")
        if not data.get('email') or not data.get('email').strip():
            raise ValueError("Email válido é obrigatório ;)")
        
class ContatoFactory(PessoaFactory):
    def create_person(self, **kwargs):
        
        from models.contact import Contato
        
        if not kwargs.get('telefone'):
            raise ValueError("Contato deve ter telefone ;)")
        
        return Contato(
            name=kwargs['name'],
            email=kwargs['email'],
            telefone=kwargs['telefone'],
            empresa=kwargs.get('empresa', ''),
            notas=kwargs.get('notas', '')
        )
        

class LeadFactory(PessoaFactory):
    def create_person(self, **kwargs):
        
        from models.contact import Lead
        
        source = kwargs.get('source', 'Website')
        
        valid_sources = [s.value for s in LeadSource]
        if source not in valid_sources:
            raise ValueError(f"Fonte inválida :( Use: {valid_sources}")
        return Lead(
            name=kwargs['name'],
            email=kwargs['email'],
            source=source
        )
        
class PessoaFactoryManager:
    _factories = {
        'contato': ContatoFactory(),
        'lead': LeadFactory()
    }
    
    @classmethod
    def create_person(cls, kind: str, **kwargs):
        kind_lower = kind.lower()
        
        if kind_lower not in cls._factories:
            raise ValueError(f"Tipo '{kind}' não suportado :( Tipos disponíveis: {list(cls._factories.keys())}")
        
        factory  = cls._factories[kind_lower]
        return factory.create_with_validation(**kwargs)
    
    @classmethod
    def register_factory(cls, kind: str, factory: PessoaFactory):
        cls._factories[kind.lower()] = factory