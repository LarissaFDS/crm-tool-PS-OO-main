import os

from core.crm import CRM
from models.base import UserRole
from core.commands import *

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
    crm = CRM()
    invoker = MenuInvoker()
    exit_command = ExitCommand(crm)

    while not exit_command.should_exit:
        clear_screen()
        
        if crm.current_user_role is None:
            crm.change_user_role()
            continue
        
        invoker = MenuInvoker() #a cada interação reinicia e registra os comandos para o perfil atual
        invoker.register_command("1", ChangeUserRoleCommand(crm))
        
        if crm.current_user_role == UserRole.ADM:
            invoker.register_command("2", AddContactCommand(crm))
            invoker.register_command("3", ListContactsCommand(crm))
            invoker.register_command("4", AddLeadCommand(crm))
            invoker.register_command("5", ConvertLeadCommand(crm))
            invoker.register_command("6", AddActivityCommand(crm))
            invoker.register_command("7", AddTaskCommand(crm))
            invoker.register_command("8", CompleteTaskCommand(crm))
            invoker.register_command("9", UpdateSalesStageCommand(crm))
            invoker.register_command("10", AddEmailCampaignCommand(crm))
            invoker.register_command("11", SendEmailCampaignCommand(crm))
            invoker.register_command("12", AddDocumentCommand(crm))
            invoker.register_command("13", ListDocumentsCommand(crm))
            invoker.register_command("14", ReportSummaryCommand(crm))
            invoker.register_command("15", StartServerCommand(crm))
            invoker.register_command("16", exit_command)
        
        elif crm.current_user_role == UserRole.VENDEDOR:
            invoker.register_command("2", AddContactCommand(crm))
            invoker.register_command("3", ListContactsCommand(crm))
            invoker.register_command("4", AddActivityCommand(crm))
            invoker.register_command("5", AddTaskCommand(crm))
            invoker.register_command("6", CompleteTaskCommand(crm))
            invoker.register_command("7", UpdateSalesStageCommand(crm))
            invoker.register_command("8", AddDocumentCommand(crm))
            invoker.register_command("9", ReportSummaryCommand(crm))
            invoker.register_command("10", exit_command)
        
        elif crm.current_user_role == UserRole.MARKETING:
            invoker.register_command("2", AddLeadCommand(crm))
            invoker.register_command("3", ConvertLeadCommand(crm))
            invoker.register_command("4", ListContactsCommand(crm))
            invoker.register_command("5", AddEmailCampaignCommand(crm))
            invoker.register_command("6", SendEmailCampaignCommand(crm))
            invoker.register_command("7", ReportSummaryCommand(crm))
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