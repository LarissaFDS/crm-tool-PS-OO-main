import os

from core.crm import CRM
from models.base import UserRole
from app import inicio

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    crm = CRM()
    while True:
        clear_screen()
        
        if crm.current_user_role is None:
            crm.change_user_role()
            continue

        menu_options = crm.get_menu_by_role()
        
        print(f"\n--- CRM - {crm.current_user_role.value.upper()} ---")
        for option in menu_options:
            print(option)
        
        opcao = input("Escolha uma opção: ")

        # Ve se é para sair, antes de rodar tudo 
        is_exit_option = (
            (opcao == "15" and crm.current_user_role == UserRole.ADM) or
            (opcao == "9" and crm.current_user_role == UserRole.VENDEDOR) or
            (opcao == "8" and crm.current_user_role == UserRole.MARKETING)
        )
        if is_exit_option:
            crm.save_data()
            print("Saindo... dados salvos.")
            break
        
        # opção comum para trocar de perfil
        if opcao == "1":
            crm.change_user_role()
            continue
        
        # Opções específicas por perfil
        elif crm.current_user_role == UserRole.ADM:
            match opcao:
                case "2": crm.add_contato()
                case "3": crm.listar_contatos()
                case "4": crm.add_lead()
                case "5": crm.converter_lead()
                case "6": crm.add_atividade()
                case "7": crm.add_task()
                case "8": crm.update_sales_stage()
                case "9": crm.add_email_campanha()
                case "10": crm.send_email_campanha()
                case "11": crm.add_document()
                case "12": crm.list_documentos()
                case "13": crm.report_summary()
                case "14": inicio()
                case _: print("Opção inválida.")
        
        elif crm.current_user_role == UserRole.VENDEDOR:
            match opcao:
                case "2": crm.add_contato()
                case "3": crm.listar_contatos()
                case "4": crm.add_atividade()
                case "5": crm.add_task()
                case "6": crm.update_sales_stage()
                case "7": crm.add_document()
                case "8": crm.report_summary()
                case _: print("Opção inválida.")
        
        elif crm.current_user_role == UserRole.MARKETING:
            match opcao:
                case "2": crm.add_lead()
                case "3": crm.converter_lead()
                case "4": crm.listar_contatos()
                case "5": crm.add_email_campanha()
                case "6": crm.send_email_campanha()
                case "7": crm.report_summary()
                case _: print("Opção inválida.")
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()