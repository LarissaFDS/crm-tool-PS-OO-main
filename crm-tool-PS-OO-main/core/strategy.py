from abc import ABC, abstractmethod
from typing import List


class MenuStrategy(ABC):
    @abstractmethod
    def get_menu(self) -> List[str]:
        pass
    
class ClienteMenuStrategy(MenuStrategy):
    def get_menu(self):
        return["1. Escolher perfil"]
    
class AdminMenuStrategy(MenuStrategy):
    def get_menu(self):
        base_menu = ClienteMenuStrategy().get_menu()
        return base_menu + [
            "2. Adicionar contato",
            "3. Listar contatos", 
            "4. Adicionar lead",
            "5. Converter lead em contato",
            "6. Registrar atividade",
            "7. Criar tarefa",
            "8. Completar tarefa",
            "9. Atualizar estágio de venda",
            "10. Criar campanha de email",
            "11. Enviar campanha de email",
            "12. Adicionar documento",
            "13. Listar documentos",
            "14. Relatórios e Analytics",
            "15. Importar lead externo",
            "16. Iniciar servidor online",
            "17. Sair"
        ]
        
class VendedorMenuStrategy(MenuStrategy):
    def get_menu(self):
        base_menu = ClienteMenuStrategy().get_menu()
        return base_menu + [
            "2. Adicionar contato",
            "3. Listar contatos",
            "4. Registrar atividade",
            "5. Criar tarefa", 
            "6. Completar tarefa",
            "7. Atualizar estágio de venda",
            "8. Adicionar documento",
            "9. Relatórios básicos",
            "10. Sair"
        ]
        
class MarketingMenuStrategy(MenuStrategy):
    def get_menu(self):
        base_menu = ClienteMenuStrategy().get_menu()
        return base_menu + [
            "2. Adicionar lead",
            "3. Converter lead em contato",
            "4. Listar contatos",
            "5. Criar campanha de email",
            "6. Enviar campanha de email",
            "7. Relatórios de campanhas",
            "8. Sair"
        ]