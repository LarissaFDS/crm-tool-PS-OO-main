from abc import ABC, abstractmethod
from datetime import datetime

from models.contact import Contato, Lead
from models.campanha import EmailCampanha
from models.document import Document
from models.task import Task
from models.atividade import Atividade
from models.factory import PessoaFactoryManager

class Builder(ABC):
    @abstractmethod
    def reset(self): #reseta o builder para começar um novo
        pass
    
    @abstractmethod
    def build(self): #constrói e retorna o produto final
        pass
    
class ContactBuilder(Builder): #builder para contato
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.name = ""
        self._email = ""
        self._telefone = ""
        self._empresa = ""
        self._notas = ""
        self._id = None
        self._sales_stage = None
        self._activities = []
        self._tasks = []
        self._documents = []
        return self
    
    def with_basic_info(self, name, email, telefone): #info obrigatórias
        self._name = name
        self._email = email
        self._telefone = telefone
        return self
    
    def with_empresa(self, empresa):
        self._empresa = empresa
        return self
    
    def with_notas(self, notas):
        self._notas = notas
        return self
    
    def with_id(self, id):
        self._id = id
        return self
    
    def with_sales_stage(self, stage):
        self._sales_stage = stage
        return self
    
    def with_activity(self, activity_type, description):
        self._activities.append(Atividade(activity_type, description))
        return self
    
    def with_task(self, title, date):
        self._tasks.append(Task(title, date))
        return self
    
    def with_documents(self, title, file_path, doc_type = "general"):
        self._documents.append(Document(title, file_path, doc_type))
        return self
    
    def build(self): #factory para validar e criar
        contato = PessoaFactoryManager.create_person(
            'contato',
            name= self._name,
            email= self._email,
            telefone= self._telefone,
            empresa= self._empresa,
            notas= self._notas,
        )
        if self._id:
            contato.id = self._id
        
        if self._sales_stage: #estagio de venda se especificar
            contato.sales_stage = self._sales_stage
            contato.stage_history = [self._sales_stage]
            
        contato.activities.extend(self._activities)
        contato.tasks.extend(self._tasks)
        contato.documents.extend(self._documents)
        
        return contato
    
class LeadBuilder(Builder): #builder para lead
    def __init__(self):
        self.reset()
        
    def reset(self):
        self._name = ""
        self._email = ""
        self._source= "Website"
        self._id = None
        self._score = None
        return self
    
    def with_basic_infos(self, name, email):
        self._name = name
        self._email = email
        return self
    
    def with_source(self, source):
        self._source = source
        return self
    
    def with_id(self, id):
        self._id = id
        return self
    
    def with_custom_score(self, score):
        self._score = score
        return self
    
    def build(self):        
        lead = PessoaFactoryManager.create_person(
            'lead',
            name= self._name,
            email= self._email,
            source=self._source
        )
        
        if self._id:
            lead.id = self._id
        
        if self._score is not None: #se foi redefinido
            lead.score = self._score
            
        return lead
    
class CampaignBuilder(Builder): #builder para camapnha de email
    def __init__(self):
        self.reset()
        
    def reset(self):
        self._title = ""
        self._description = ""
        self._target_stage = ""
        self._id = None
        self._sent_to = []
        return self
    
    def with_basic_info(self, title, description, target_stage):
        self._title = title
        self._description = description
        self._target_stage = target_stage
        return self
    
    def with_id(self, id):
        self._id = id
        return self
    
    def with_recipients(self, contact_ids):
        self._sent_to = contact_ids if isinstance(contact_ids, list) else [contact_ids]
        return self
    
    def build(self):
        if not self._title or not self._description or not self._target_stage:
            raise ValueError("Titulo, descrição e estágio alvo são obrigatórios")
        
        campanha = EmailCampanha(
            title=self._title,
            description=self._description,
            target_stage=self._target_stage,
            id = self._id
        )
        
        campanha.sent_to = self._sent_to.copy()
        return campanha
    

class BuilderDirector:
    def __init__(self):
        self._builder = None
        
    def set_builder(self, builder: Builder):
        self._builder = builder
        
    def build_simple_contact(self, name, email, telefone):
        return(self._builder
               .reset()
               .with_basic_info(name, email, telefone)
               .build())
        
    def build_complete_contact(self, name, email, telefone, empresa, notas):
          return (self._builder
                .reset()
                .with_basic_info(name, email, telefone)
                .with_empresa(empresa)
                .with_notas(notas)
                .build())
    
    def build_contact_with_activity(self, name, email, telefone, empresa=""):
        return(self._builder
               .reset()
               .with_basic_info(name, email, telefone)
               .with_activity("cadastro", "Contato cadastrado no sistema")
               .build())
        
    def build_high_value_lead(self, name, email):
        return(self._builder
               .reset()
               .with_basic_info(name, email)
               .with_source("Indicação")
               .build())
        
    def build_welcome_campaign(self):
        return(self._builder
               .reset()
               .with_basic_info("Camapanha de Boas-vindas", "Email de boas_vindas para novos leads", "Lead")
               .build())
        
#caso queira mais conveniente
def create_contact():
    return ContactBuilder()

def create_lead():
    return LeadBuilder()

def create_campaign():
    return CampaignBuilder()

def get_director():
    return BuilderDirector()