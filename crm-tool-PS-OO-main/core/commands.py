from abc import ABC, abstractmethod
import time

from .crm import CRM
from app import inicio

class Command(ABC):
    def __init__(self, crm_receiver: CRM):
        self._crm = crm_receiver
        
    @abstractmethod
    def execute(self) -> None:
        pass

class AddContactCommand(Command):
    def execute(self) -> None:
        self._crm.add_contato()
        
class ListContactsCommand(Command):
    def execute(self) -> None:
        self._crm.listar_contatos()
        
class AddLeadCommand(Command):
    def execute(self):
        self._crm.add_lead()
        
class ConvertLeadCommand(Command):
    def execute(self) -> None:
        self._crm.converter_lead()

class AddActivityCommand(Command):
    def execute(self) -> None:
        self._crm.add_atividade()

class AddTaskCommand(Command):
    def execute(self) -> None:
        self._crm.add_task()

class CompleteTaskCommand(Command):
    def execute(self) -> None:
        self._crm.completar_task()

class UpdateSalesStageCommand(Command):
    def execute(self) -> None:
        self._crm.update_sales_stage()

class AddEmailCampaignCommand(Command):
    def execute(self) -> None:
        self._crm.add_email_campanha()

class SendEmailCampaignCommand(Command):
    def execute(self) -> None:
        self._crm.send_email_campanha()

class AddDocumentCommand(Command):
    def execute(self) -> None:
        self._crm.add_document()

class ListDocumentsCommand(Command):
    def execute(self) -> None:
        self._crm.list_documentos()

class ReportSummaryCommand(Command):
    def execute(self) -> None:
        self._crm.report_summary()

class ChangeUserRoleCommand(Command):
    def execute(self) -> None:
        self._crm.change_user_role()

class StartServerCommand(Command):
    def execute(self) -> None:
        inicio()
        
class ExitCommand(Command):
    def __init__(self, crm_receiver):
        super().__init__(crm_receiver)
        self.should_exit = False
        
    def execute(self):
        self._crm.save_data()
        print("Saindo... dados salvos.")
        self.should_exit = True
        
        
#DECORATOR
class CommandDecorator(Command):
    def __init__(self, wrapped_command: Command):
        super().__init__(wrapped_command._crm)
        self._wrapped_command = wrapped_command
        
    @abstractmethod
    def execute(self) -> None:
        pass
    
class LoggingCommandDecorator(CommandDecorator):
    def __init__(self, wrapped_command):
        super().__init__(wrapped_command)
        
    def execute(self):
        command_name = self._wrapped_command.__class__.__name__
        print(f"\n--- [LOG] iniciando: {command_name} ---")
        start_time = time.time()
        
        try:
            self._wrapped_command.execute()
            end_time = time.time()
            duration = end_time - start_time
            print(f"--- [LOG] finalizado: {command_name} (duração: {duration:.4f}s) ---")
        
        except Exception as e:
            print(f"--- [LOG] ERRO em {command_name}: {e} ---")
            raise e