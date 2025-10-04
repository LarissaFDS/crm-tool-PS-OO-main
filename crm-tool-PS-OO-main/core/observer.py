from abc import ABC, abstractmethod
from typing import Any

class Observer(ABC):
    @abstractmethod
    def update(self, subject: Any, event: str, data: Any = None) -> None:
        pass
    
    def can_handle(self, event):
        return True
    
class Subject(ABC):
    @abstractmethod
    def attach(self, observer: Observer) -> None:
        pass
    
    @abstractmethod
    def detach(self, observer):
        pass
    
    @abstractmethod
    def notify(self, event: str, data: Any) -> None:
        pass
    
class EmailNotifier(Observer):
    def update(self, subject, event, data = None):
        if event == "lead_converted":
            contato = data
            print(f"📧 Enviando email de boas-vindas para {contato.name} - ({contato.email}).")
        
        elif event == "task_completed":
            contato = data["contato"]
            task = data["task"]
            print(f"📧 Notificando {contato.name} sobre conclusão da tarefa '{task.title}'.")
        
        elif event == "stage_changed":
            contato = data["contato"]
            new_stage = data["new_stage"]
            print(f"📧 Email automático enviado: {contato.name} avançou para '{new_stage}'.")

class AnalyticsUpdater(Observer):
    def update(self, subject, event, data = None):
        if event == "lead_converted":
            contato = data
            print(f"📊 Registrando evento de conversão para o contato '{contato.name}'.")
        
        elif event == "activity_added":
            contato = data["contato"]
            activity = data["activity"]
            print(f"📊 Nova atividade '{activity.type}' registrada para {contato.name}.")
        
        elif event == "stage_changed":
            old_stage = data["old_stage"]
            new_stage = data["new_stage"]
            print(f"📊 Métrica atualizada: Transição {old_stage} → {new_stage}.")

class SalesNotifier(Observer):
    def update(self, subject, event, data = None):
        if event == "lead_converted":
            contato = data
            print(f"🔔 Notificando time de vendas sobre novo contato: {contato.name}.")

        elif event == "stage_changed":
            contato = data["contato"]
            new_stage = data["new_stage"]
            if new_stage in ["Proposta", "Negociação"]:
                print(f"🔔 ALERTA VENDAS: {contato.name} está em '{new_stage}' - requer atenção!")