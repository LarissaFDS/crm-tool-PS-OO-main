import os

from core.facade_crm import CRMFacade
from models.base import UserRole

from core.commands import *
from core.observer import EmailNotifier, AnalyticsUpdater, SalesNotifier

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    
class MenuInvoker:
    def __init__(self):
        self._commands = {}
        
    def register_command(self, key, command):
        self._commands[key] = command
        
    def execute_command(self, key):
        command = self._commands.get(key)
        if command:
            command.execute()
        else:
            print("Opção inválida :(")

def main():
    crm = CRMFacade()
    
    email_service = EmailNotifier()
    analytics_service = AnalyticsUpdater()
    sales_team_channel = SalesNotifier()
    
    crm.attach(email_service)
    crm.attach(analytics_service)
    crm.attach(sales_team_channel)
    
    invoker = MenuInvoker()
    exit_command = ExitCommand(crm)

    while not exit_command.should_exit:
        clear_screen()
        
        if crm.current_user_role is None:
            crm.change_user_role()
            #print(f"teste {crm.current_user_role}")
            continue
        
        invoker = MenuInvoker() #a cada interação reinicia e registra os comandos para o perfil atual
        invoker.register_command("1", ChangeUserRoleCommand(crm))
        
        if crm.current_user_role == UserRole.ADM:
            invoker.register_command("2", LoggingCommandDecorator(AddContactCommand(crm)))
            invoker.register_command("3", LoggingCommandDecorator(ListContactsCommand(crm)))
            invoker.register_command("4", LoggingCommandDecorator(AddLeadCommand(crm)))
            invoker.register_command("5", LoggingCommandDecorator(ConvertLeadCommand(crm)))
            invoker.register_command("6", LoggingCommandDecorator(AddActivityCommand(crm)))
            invoker.register_command("7", LoggingCommandDecorator(AddTaskCommand(crm)))
            invoker.register_command("8", LoggingCommandDecorator(CompleteTaskCommand(crm)))
            invoker.register_command("9", LoggingCommandDecorator(UpdateSalesStageCommand(crm)))
            invoker.register_command("10", LoggingCommandDecorator(AddEmailCampaignCommand(crm)))
            invoker.register_command("11", LoggingCommandDecorator(SendEmailCampaignCommand(crm)))
            invoker.register_command("12", LoggingCommandDecorator(AddDocumentCommand(crm)))
            invoker.register_command("13", LoggingCommandDecorator(ListDocumentsCommand(crm)))
            invoker.register_command("14", LoggingCommandDecorator(ReportSummaryCommand(crm)))
            invoker.register_command("15", LoggingCommandDecorator(ImportExternalLeadCommand(crm)))
            invoker.register_command("16", LoggingCommandDecorator(StartServerCommand(crm)))
            invoker.register_command("17", exit_command)
        
        elif crm.current_user_role == UserRole.VENDEDOR:
            invoker.register_command("2", LoggingCommandDecorator(AddContactCommand(crm)))
            invoker.register_command("3", LoggingCommandDecorator(ListContactsCommand(crm)))
            invoker.register_command("4", LoggingCommandDecorator(AddActivityCommand(crm)))
            invoker.register_command("5", LoggingCommandDecorator(AddTaskCommand(crm)))
            invoker.register_command("6", LoggingCommandDecorator(CompleteTaskCommand(crm)))
            invoker.register_command("7", LoggingCommandDecorator(UpdateSalesStageCommand(crm)))
            invoker.register_command("8", LoggingCommandDecorator(AddDocumentCommand(crm)))
            invoker.register_command("9", LoggingCommandDecorator(ReportSummaryCommand(crm)))
            invoker.register_command("10", exit_command)
        
        elif crm.current_user_role == UserRole.MARKETING:
            invoker.register_command("2", LoggingCommandDecorator(AddLeadCommand(crm)))
            invoker.register_command("3", LoggingCommandDecorator(ConvertLeadCommand(crm)))
            invoker.register_command("4", LoggingCommandDecorator(ListContactsCommand(crm)))
            invoker.register_command("5", LoggingCommandDecorator(AddEmailCampaignCommand(crm)))
            invoker.register_command("6", LoggingCommandDecorator(SendEmailCampaignCommand(crm)))
            invoker.register_command("7", LoggingCommandDecorator(ReportSummaryCommand(crm)))
            invoker.register_command("8", exit_command)
            
        menu_options = crm.get_menu_by_role()
        print(f"\n--- CRM - {crm.current_user_role.value.upper()} ---")
        for option in menu_options:
            print(option)
            
        opcao = input("Escolha uma opção: ")
        invoker.execute_command(opcao)
        
        if not exit_command.should_exit:
            input("\nPressione Enter para continuar...")
            
if __name__ == "__main__":
    main()