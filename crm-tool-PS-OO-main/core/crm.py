import json
from pathlib import Path
import unicodedata

from models.base import UserRole, LeadSource
from models.contact import Contato, Lead, SalesStage
from models.campanha import EmailCampanha
from models.document import Document
from models.atividade import Atividade
from models.task import Task

DATA_FILE = Path(__file__).resolve().parent.parent / "crm_data.json"

class CRM:
    #------------------- SINGLETON --------------------------
    _instace = None
    _initialized = False
    def __new__ (cls, *args, **kwargs):
        if cls._instace is None:
            cls._instace = super(CRM, cls).__new__(cls)
        return cls._instace
    
    def __init__(self):
        if not CRM._initialized:
            CRM._initialized = True
    #--------------------------------------------------------
        # print("\n--- DEBUG: 1. Iniciando a criação do objeto CRM... ---")
            self.contatos = []
            self.campanhas = []
            self.leads = []
            self.documents = []
            self.current_user_role = None  # user inicial
            self.load_data()

       # print("--- DEBUG: 4. Finalizando a criação do objeto CRM. ---\n")
        
    def save_data(self): 
        data = {
            "contatos": [c.to_dict() for c in self.contatos],
            "campanhas": [c.to_dict() for c in self.campanhas],
            "leads": [l.to_dict() for l in self.leads],
            "documents": [d.to_dict() for d in self.documents]
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_data(self): 
        #print("--- DEBUG: 2. Entrando na função load_data... ---")
        
        if not DATA_FILE.exists(): #garante que nao vai ter erro se o arquivo nao existir na primeira vez
            print("--- DEBUG: Erro! O arquivo DATA_FILE não foi encontrado. ---")
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                #print("--- DEBUG: 3. Arquivo JSON aberto com sucesso. Lendo dados... ---")
                
                data = json.load(f)
                self.contatos = [Contato.from_dict(c) for c in data.get("contatos", [])]
                self.campanhas = [EmailCampanha.from_dict(c) for c in data.get("campanhas", [])]
                self.leads = [Lead.from_dict(l) for l in data.get("leads", [])]
                self.documents = [Document.from_dict(d) for d in data.get("documents", [])]
                
                # print("\n--- DEBUG: IDs dos Contatos Carregados na Memória ---")
                # for contato in self.contatos:
                #     print(f"Nome: {contato.name}, ID na memória: {contato.id}, Tipo do ID: {type(contato.id)}")
                # print("---------------------------------------------------\n")
        except Exception as e:
            print(f"--- DEBUG: Erro ao processar o JSON: {e} ---")
            
            self.contatos = []
            self.campanhas = []
            self.leads = []
            self.documents = []

    def add_contato(self):
        print("\n=== Novo Contato ===")
        name = self._get_normalized_input("Nome: ", case="title")
        email = self._get_normalized_input("Email: ", case="lower")
        telefone = self._get_normalized_input("Telefone: ")
        empresa = self._get_normalized_input("Empresa (opcional): ", case="title")
        notes = self._get_normalized_input("Notas (opcional): ")
        
        try:
            c = Contato(name, email, telefone, empresa, notes)
            self.contatos.append(c)
            self.save_data()
            print("Contato adicionado com sucesso!")
        except ValueError as e:
            print(f"Erro: {e}")

    def listar_contatos(self):
        if not self.contatos:
            print("Nenhum contato cadastrado.")
            return
        
        print("\n=== Lista de Contatos ===")
        for i, c in enumerate(self.contatos):
            print(f"{i+1}. {c.name} - {c.email} - {c.sales_stage}")

    def change_user_role(self):
        """trocar o perfil do usuário"""
        print("\nPerfis disponíveis:")
        print("1. Gerente")
        print("2. Vendedor") 
        print("3. Marketing")
        choice = self._get_normalized_input("Escolha seu perfil: ")
        
        if choice == "1":
            self.current_user_role = UserRole.ADM
        elif choice == "2":
            self.current_user_role = UserRole.VENDEDOR
        elif choice == "3":
            self.current_user_role = UserRole.MARKETING
        
        print(f"Perfil alterado para: {self.current_user_role.value}")

    def add_document(self):
        """Adiciona documento ao sistema"""
        print("\n=== Novo Documento ===")
        title = self._get_normalized_input("Título do documento: ", case="title")
        file_path = self._get_normalized_input("Caminho do arquivo: ")
        doc_type = self._get_normalized_input("Tipo (proposta/contrato/outro): ", case="lower")
        if not doc_type:
            doc_type = "outro"
        
        doc = Document(title, file_path, doc_type)
        self.documents.append(doc)
        
        # Opção de associar a um contato
        print("\nDeseja associar a um contato? (s/n)")
        response = self._get_normalized_input("", case="lower")
        if response == 's':
            self.listar_contatos()
            try:
                idx_input = self._get_normalized_input("Escolha o contato (número): ")
                idx = int(idx_input) - 1
                if 0 <= idx < len(self.contatos):
                    self.contatos[idx].documents.append(doc)
            except (ValueError, IndexError):
                print("Contato inválido, documento salvo apenas no sistema.")
        
        self.save_data()
        print("Documento adicionado com sucesso!")

    def list_documentos(self):
        """Lista todos os documentos"""
        if not self.documents:
            print("Nenhum documento encontrado.")
            return
        
        print("\n=== documentos ===")
        for i, doc in enumerate(self.documents):
            print(f"{i+1}. {doc.title} ({doc.doc_type}) - {doc.created_at}")

    def add_lead(self):
        print("\n=== Novo Lead ===")
        name = self._get_normalized_input("Nome: ", case="title")
        email = self._get_normalized_input("Email: ", case="lower")
        fontes_disponiveis = [source.value for source in LeadSource]
        fontes_disponiveis_normalizadas = [self._normalize_text(source, case="title") for source in fontes_disponiveis]
        print(f"Fontes disponíves: {', '.join(fontes_disponiveis)}")
        source = None
        
        while True:
            source_input = self._get_normalized_input("Fonte: ", case="title")
            if not source_input:
                source = LeadSource.WEBSITE.value
                break
            if source_input in fontes_disponiveis_normalizadas:
                idx = fontes_disponiveis_normalizadas.index(source_input)
                source = fontes_disponiveis[idx]
                break
            else:
                print(f"Erro: Fonte inválida :(. Escolha uma fonte válida.)")
                
        try:
            lead = Lead(name, email, source)
            self.leads.append(lead)
            self.save_data()
            print(f"Lead adicionado com sucesso! Pontuação inicial: {lead.score}")
        except ValueError as e:
            print(f"Erro: {e}")

    def converter_lead(self):
        ativos = [l for l in self.leads if not l.converted]
        if not ativos:
            print("Nenhum lead disponível para conversão.")
            return

        print("\n=== Leads para Converter ===")
        for i, l in enumerate(ativos):
            print(f"{i+1}. {l.name} - {l.email} - Fonte: {l.source}")
        try:
            idx_input = self._get_normalized_input("Escolha um lead (número): ")
            idx = int(idx_input) - 1
            if 0 <= idx < len(ativos):
                lead = ativos[idx]
                telefone = self._get_normalized_input("Telefone: ")
                empresa = self._get_normalized_input("Empresa (opcional): ", case="title")
                notes = f"Convertido de lead (Fonte: {lead.source})"
                contato = Contato(lead.name, lead.email, telefone, empresa, notes)
                self.contatos.append(contato)
                lead.converted = True
                self.save_data()
                print("Lead convertido em contato!")
            else:
                print("Lead inválido.")
        except (ValueError, IndexError):
            print("Entrada inválida.")

    def add_atividade(self):
        if not self.contatos:
            print("Nenhum contato cadastrado.")
            return
        self.listar_contatos()
        try:
            idx_input = self._get_normalized_input("Escolha o contato (número): ")
            idx = int(idx_input) - 1
            if 0 <= idx < len(self.contatos):
                tipo = self._get_normalized_input("Tipo (chamada/email/reunião): ", case="lower")
                desc = self._get_normalized_input("Descrição: ")
                self.contatos[idx].activities.append(Atividade(tipo, desc))
                self.save_data()
                print("Atividade registrada!")
            else:
                print("Contato inválido.")
        except (ValueError, IndexError):
            print("Entrada inválida.")   

    def add_task(self):
        if not self.contatos:
            print("Nenhum contato cadastrado.")
            return
        self.listar_contatos()
        try:
            idx_input = self._get_normalized_input("Escolha o contato (número): ")
            idx = int(idx_input) - 1
            if 0 <= idx < len(self.contatos):
                titulo = self._get_normalized_input("Título da tarefa: ", case="title")
                data = self._get_normalized_input("Data (dd/mm/aaaa): ")
                self.contatos[idx].tasks.append(Task(titulo, data))
                self.save_data()
                print("Tarefa adicionada!")
            else:
                print("Contato inválido.")
        except (ValueError, IndexError):
            print("Entrada inválida.")

    def update_sales_stage(self):
        if not self.contatos:
            print("Nenhum contato cadastrado.")
            return
        self.listar_contatos()
        try:
            idx_input = self._get_normalized_input("Escolha o contato (número): ")
            idx = int(idx_input) - 1
            if 0 <= idx < len(self.contatos):
                print(f"Estágios: {[stage.value for stage in SalesStage]}")
                novo = self._get_normalized_input("Novo estágio: ", case="title")
                if novo not in [stage.value for stage in SalesStage]:
                    print ("Erro: Estágio inválido :(\n)")
                    return
                self.contatos[idx].sales_stage = novo
                self.contatos[idx].stage_history.append(novo)
                self.save_data()
                print("Estágio de venda atualizado!")
            else:
                print("Contato inválido.")
        except (ValueError, IndexError):
            print("Entrada inválida.")

    def add_email_campanha(self):
        print("\n=== Nova Campanha de Email ===")
        title = self._get_normalized_input("Título da campanha: ", case="title")
        description = self._get_normalized_input("Descrição: ")
        target_stage = self._get_normalized_input("Estágio alvo (Lead/Prospecto/Proposta/Negociação/Venda fechada/Todos): ", case="title")
        camp = EmailCampanha(title, description, target_stage)
        self.campanhas.append(camp)
        self.save_data()
        print("Campanha criada com sucesso!")
    
    def send_email_campanha(self):
        if not self.campanhas:
            print("Nenhuma campanha criada.")
            return

        print("\n=== Campanhas Disponíveis ===")
        for i, c in enumerate(self.campanhas):
            print(f"{i+1}. {c.title} - Alvo: {c.target_stage}")

        try:
            idx_input = self._get_normalized_input("Escolha a campanha (número): ")
            idx = int(idx_input) - 1
            if 0 <= idx < len(self.campanhas):
                campanha = self.campanhas[idx]
                enviados = 0
                
                # print(f"\nDEBUG Processando campanha: {campanha.title}")
                # print(f"DEBUG Estágio alvo: '{campanha.target_stage}'")
                
                for contato in self.contatos:
                    # Normaliza ambos os estágios para comparação
                    contato_stage_norm = self._normalize_text(contato.sales_stage, case="title")
                    target_stage_norm = self._normalize_text(campanha.target_stage, case="title")
                    
                    #print(f"DEBUG Contato: {contato.name} - Estágio: '{contato_stage_norm}' vs Alvo: '{target_stage_norm}'")
                    
                    stage_match = (contato_stage_norm == target_stage_norm or target_stage_norm == "Todos")
                    not_sent = contato.id not in campanha.sent_to
                    
                    if stage_match and not_sent:
                        campanha.sent_to.append(contato.id)
                        contato.activities.append(Atividade("Email", f"Enviado: {campanha.title}"))
                        enviados += 1
                    #     print(f" DEBUG ✓ Email enviado para {contato.name}")
                    # elif not not_sent:
                    #     print(f"DEBUG - Email já enviado para {contato.name}")
                    # else:
                    #     print(f"DEBUG - {contato.name} não se encaixa no critério")
                
                if enviados > 0:
                    self.save_data()
                    print(f"\nCampanha enviada com sucesso para {enviados} contato(s).")
                else:
                    print("\nNenhum contato encontrado para esta campanha.")
            else:
                print("Campanha inválida.")
        except (ValueError, IndexError):
            print("Entrada inválida.")

    def report_summary(self):
        print("\n=== Relatório Geral ===")
        print(f"Total de contatos: {len(self.contatos)}")
        print(f"Total de leads: {len([l for l in self.leads if not l.converted])}")
        print(f"Total de campanhas: {len(self.campanhas)}")
        print(f"Total de documentos: {len(self.documents)}")
        
        # Relatório por estágio - normaliza os estágios para agrupamento consistente
        estagios_padrao = ["Lead", "Prospecto", "Proposta", "Negociação", "Venda Fechada"]
        por_estagio = {estagio: 0 for estagio in estagios_padrao}
        
        for c in self.contatos:
            stage_normalizado = self._normalize_text(c.sales_stage, case="title")
            if stage_normalizado in por_estagio:
                por_estagio[stage_normalizado] += 1
            else:
                # Se o estágio não está nos padrões, adiciona como "Outros"
                if "Outros" not in por_estagio:
                    por_estagio["Outros"] = 0
                por_estagio["Outros"] += 1
        
        print("\n--- Distribuição por Estágio ---")
        for estagio, qtd in por_estagio.items():
            if qtd > 0:  # Só mostra estágios que têm contatos
                print(f"{estagio}: {qtd} contato(s)")

    def get_menu_by_role(self):
        """Retorna opções de menu baseadas no perfil do usuário"""

        base_menu = [
            "1. Escolher Perfil"
        ]

        if self.current_user_role == UserRole.CLIENTE:
            return base_menu
        
        if self.current_user_role == UserRole.ADM:
            return base_menu + [
                "2. Adicionar contato",
                "3. Listar contatos", 
                "4. Adicionar lead",
                "5. Converter lead em contato",
                "6. Registrar atividade",
                "7. Criar tarefa",
                "8. Atualizar estágio de venda",
                "9. Criar campanha de email",
                "10. Enviar campanha de email",
                "11. Adicionar documento",
                "12. Listar documentos",
                "13. Relatórios e Analytics",
                "14. Iniciar servidor online",
                "15. Sair"
            ]
        elif self.current_user_role == UserRole.VENDEDOR:
            return base_menu + [
                "2. Adicionar contato",
                "3. Listar contatos",
                "4. Registrar atividade",
                "5. Criar tarefa", 
                "6. Atualizar estágio de venda",
                "7. Adicionar documento",
                "8. Relatórios básicos",
                "9. Sair"
            ]
        else:  # MARKETING
            return base_menu + [
                "2. Adicionar lead",
                "3. Converter lead em contato",
                "4. Listar contatos",
                "5. Criar campanha de email",
                "6. Enviar campanha de email",
                "7. Relatórios de campanhas",
                "8. Sair"
            ]
            
    def _get_normalized_input(self, prompt, case="none"):
        value = input(prompt).strip() 
        if case == "lower":
            return value.lower()
        elif case == "title":
            return value.title()
        elif case == "upper":
            return value.upper()
        return value
    
    def _normalize_text(self, text, case="none"):
        if not text:
            return ""
    
        normalized_text = unicodedata.normalize('NFD', text)\
                                    .encode('ascii', 'ignore')\
                                    .decode('utf-8')

        value = normalized_text.strip()
        if case == "lower":
            return value.lower()
        elif case == "title":
            return value.title()
        elif case == "upper":
            return value.upper()
        return value
    
    def _get_normalized_input(self, prompt, case="none"):
        value = input(prompt)
        return self._normalize_text(value, case=case)