import json
from pathlib import Path
import unicodedata

from models.base import UserRole, LeadSource
from models.contact import Contato, Lead, SalesStage
from models.campanha import EmailCampanha
from models.document import Document
from models.atividade import Atividade
from models.task import Task

from models.factory import PessoaFactoryManager
from models.builder import create_contact, create_lead, create_campaign, get_director

from .strategy import * #sei que nao é uma boa maneira, mas tava com preguiça
from .observer import Subject, Observer
from .adapters import LeadAdapter

DATA_FILE = Path(__file__).resolve().parent.parent / "crm_data.json"

class CRM(Subject):
    _instance = None
    _initialized = False
    def __new__ (cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CRM, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not CRM._initialized:
            CRM._initialized = True
        #print("\n--- DEBUG: 1. Iniciando a criação do objeto CRM... ---")
            self.contatos = []
            self.campanhas = []
            self.leads = []
            self.documents = []
            self.current_user_role = None  #user inicial
            
            self._menu_strategies = {
                UserRole.ADM: AdminMenuStrategy(),
                UserRole.CLIENTE: ClienteMenuStrategy(),
                UserRole.MARKETING: MarketingMenuStrategy(),
                UserRole.VENDEDOR: VendedorMenuStrategy()
            }
            
            self._observers: list[Observer] = []
            
            self.load_data()

       #print("--- DEBUG: 4. Finalizando a criação do objeto CRM. ---\n")
        
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
                
                #print("\n--- DEBUG: IDs dos Contatos Carregados na Memória ---")
                #for contato in self.contatos:
                #   print(f"Nome: {contato.name}, ID na memória: {contato.id}, Tipo do ID: {type(contato.id)}")
                #print("---------------------------------------------------\n")
        except Exception as e:
            print(f"--- DEBUG: Erro ao processar o JSON: {e} ---")
            
            self.contatos = []
            self.campanhas = []
            self.leads = []
            self.documents = []

    def add_contato(self):
        print("\n=== Novo contato ===")
        name = self._get_normalized_input("Nome: ", case="title")
        email = self._get_normalized_input("Email: ", case="lower")
        telefone = self._get_normalized_input("Telefone: ")
        empresa = self._get_normalized_input("Empresa (opcional): ", case="title")
        notes = self._get_normalized_input("Notas (opcional): ")
        
        print("\nDeseja adicionar informações extras (tarefas, estágio diferente, etc.)? (s/n)")
        extras = self._get_normalized_input("", case="lower") == 's'
        
        try:
            builder = create_contact().with_basic_info(name, email, telefone)
            
            if empresa:
                builder.with_empresa(empresa)
            if notes:
                builder.with_notas(notes)
            
            if extras:
                print("\n--- Informações Extras ---")
                
                #Atividade inicial
                ativ_tipo = self._get_normalized_input("Tipo de primeira atividade (chamada/email/reunião): ", case="lower")
                if ativ_tipo:
                    ativ_desc = self._get_normalized_input("Descrição da atividade: ")
                    builder.with_activity(ativ_tipo, ativ_desc)
                
                #Tarefa
                print("Deseja criar uma tarefa inicial? (s/n)")
                if self._get_normalized_input("", case="lower") == 's':
                    task_title = self._get_normalized_input("Título da tarefa: ")
                    task_date = self._get_normalized_input("Data (dd/mm/aaaa): ")
                    builder.with_task(task_title, task_date)
                
                #Estágio inicial diferente
                print("Deseja definir estágio inicial diferente de 'Prospecto'? (s/n)")
                if self._get_normalized_input("", case="lower") == 's':
                    print(f"Estágios: {[stage.value for stage in SalesStage]}")
                    stage = self._get_normalized_input("Estágio: ", case="title")
                    if stage in [s.value for s in SalesStage]:
                        builder.with_sales_stage(stage)
            else:
                #Adiciona atividade básica de cadastro
                builder.with_activity("cadastro", "Contato cadastrado no sistema")
            
            contato = builder.build()
            self.contatos.append(contato)
            self.save_data()
            print("Contato criado com sucesso!")
            
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
        print("\n=== Novo Documento ===")
        title = self._get_normalized_input("Título do documento: ", case="title")
        file_path = self._get_normalized_input("Caminho do arquivo: ")
        doc_type = self._get_normalized_input("Tipo (proposta/contrato/outro): ", case="lower")
        if not doc_type:
            doc_type = "outro"
        
        doc = Document(title, file_path, doc_type)
        self.documents.append(doc)
        
        #Opção de associar a um contato
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
            new_lead = PessoaFactoryManager.create_person(
                'lead',
                name=name,
                email=email,
                source=source
            )
            self.leads.append(new_lead)
            
            self.save_data()
            print(f"Lead adicionado com sucesso! Pontuação inicial: {new_lead.score}")
        except ValueError as e:
            print(f"Erro: {e}")

    def add_lead_from_external_source(self, lead_adapter: LeadAdapter):
        print("\n=== Importando lead externo (via adapter) ===")
        try:
            compatible_data = lead_adapter.get_crm_compatible_data()
            new_lead = PessoaFactoryManager.create_person(
                'lead',
                **compatible_data
            )
            
            self.leads.append(new_lead)
            self.save_data()
            print(f"✅ Lead importado e adaptado com sucesso! ({new_lead.name})")

        except Exception as e: 
            print(f"Erro inesperado durante adaptação: {e}")
        
    def attach(self, observer):
        self._observers.append(observer)
        
    def detach(self, observer):
        self._observers.remove(observer)
    
    def notify(self, event, data):
        for observer in self._observers:
            try:
                if observer.can_handle(event):
                    observer.update(self, event, data)
            except Exception as e:
                print(f"Erro ao notificar {observer.__class__.__name__}: {e}")
        
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
                
                contato = PessoaFactoryManager.create_person(
                    'contato',
                    name=lead.name,
                    email=lead.email,
                    telefone=telefone,
                    empresa=empresa,
                    notas=notes
                )
                self.contatos.append(contato)
                lead.converted = True
                self.save_data()
                print("Lead convertido em contato!")
                self.notify(event="lead_converted", data=contato) #observer
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
                
                new_activity = Atividade(tipo, desc)
                self.contatos[idx].activities.append(new_activity)
                self.save_data()
                
                self.notify("activity_added", {
                    "contato": self.contatos[idx],
                    "activity": new_activity
                })
                
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
                
    def completar_task(self):
        if not self.contatos:
            print("Nenhum contato cadastrado.")
            return
            
        self.listar_contatos()
        try:
            idx_input = self._get_normalized_input("Escolha o contato para ver as tarefas (número): ")
            idx = int(idx_input) - 1
            if not (0 <= idx < len(self.contatos)):
                print("Contato inválido.")
                return
                
            contato = self.contatos[idx]
            tarefas_pendentes = [task for task in contato.tasks if not task.completed]
            
            if not tarefas_pendentes:
                print(f"O contato {contato.name} não possui tarefas pendentes.")
                return
                
            print(f"\n--- Tarefas Pendentes de {contato.name} ---")
            for i, task in enumerate(tarefas_pendentes):
                print(f"{i+1}. {task.title} - Data: {task.date}")
                
            task_idx_input = self._get_normalized_input("Escolha a tarefa para marcar como concluída (número): ")
            task_idx = int(task_idx_input) - 1
            
            if 0 <= task_idx < len(tarefas_pendentes):
                tarefa_concluida = tarefas_pendentes[task_idx]
                tarefa_concluida.completed = True
                
                contato.activities.append(
                    Atividade("tarefa_concluida", f"Tarefa concluída: {tarefa_concluida.title}")
                )
                
                self.save_data()
                
                self.notify("task_completed", {
                    "contato": contato,
                    "task": tarefa_concluida
                })
                
                print(f"✅ Tarefa '{tarefa_concluida.title}' marcada como concluída!")
                print("📝 Atividade de conclusão registrada automaticamente.")
            else:
                print("Seleção de tarefa inválida.")
                
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
                contato = self.contatos[idx]
                old_stage = contato.sales_stage
                print(f"Estágios: {[stage.value for stage in SalesStage]}")
                novo = self._get_normalized_input("Novo estágio: ", case="title")
                
                if novo not in [stage.value for stage in SalesStage]:
                    print ("Erro: Estágio inválido :(\n)")
                    return
                
                self.contatos[idx].sales_stage = novo
                self.contatos[idx].stage_history.append(novo)
                self.save_data()
                
                self.notify("stage_changed",{
                    "contato": contato,
                    "old_stage": old_stage,
                    "new_stage": novo
                })
                
                print("Estágio de venda atualizado!")
            else:
                print("Contato inválido.")
        except (ValueError, IndexError):
            print("Entrada inválida.")

    def add_email_campanha(self):
        print("\n=== Nova campanha de email ===")
        title = self._get_normalized_input("Título da campanha: ", case="title")
        description = self._get_normalized_input("Descrição: ")
        target_stage = self._get_normalized_input("Estágio alvo (Lead/Prospecto/Proposta/Negociação/Venda fechada/Todos): ", case="title")
        
        print("\nDeseja configurações avançadas? (s/n)")
        advanced = self._get_normalized_input("", case="lower") == 's'
        
        try:           
            builder = create_campaign().with_basic_info(title, description, target_stage)
            
            if advanced:
                print("\n--- Configurações Avançadas ---")
                
                print("Deseja pré-selecionar destinatários específicos? (s/n)")
                if self._get_normalized_input("", case="lower") == 's':
                    self.listar_contatos()
                    recipient_ids = []
                    
                    while True:
                        contact_input = self._get_normalized_input("ID do contato (ou 'fim' para terminar): ")
                        if contact_input.lower() == 'fim':
                            break
                        
                        try:
                            contact_id = int(contact_input)
                            #Verifica se o contato existe
                            if any(c.id == contact_id for c in self.contatos):
                                recipient_ids.append(contact_id)
                                print(f"Contato {contact_id} adicionado à lista.")
                            else:
                                print(f"Contato {contact_id} não encontrado.")
                        except ValueError:
                            print("ID inválido.")
                    
                    if recipient_ids:
                        builder.with_recipients(recipient_ids)
            
            campanha = builder.build()
            self.campanhas.append(campanha)
            self.save_data()
            
            print("Campanha criada com sucesso usando Builder!")
            if hasattr(campanha, 'sent_to') and campanha.sent_to:
                print(f"Pré-configurada para {len(campanha.sent_to)} destinatário(s) específico(s).")
                
        except ValueError as e:
            print(f"Erro: {e}")

    
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
                
                #print(f"\nDEBUG Processando campanha: {campanha.title}")
                #print(f"DEBUG Estágio alvo: '{campanha.target_stage}'")
                
                for contato in self.contatos:
                    #Normaliza ambos os estágios para comparação
                    contato_stage_norm = self._normalize_text(contato.sales_stage, case="title")
                    target_stage_norm = self._normalize_text(campanha.target_stage, case="title")
                    
                    #print(f"DEBUG Contato: {contato.name} - Estágio: '{contato_stage_norm}' vs Alvo: '{target_stage_norm}'")
                    
                    stage_match = (contato_stage_norm == target_stage_norm or target_stage_norm == "Todos")
                    not_sent = contato.id not in campanha.sent_to
                    
                    if stage_match and not_sent:
                        campanha.sent_to.append(contato.id)
                        contato.activities.append(Atividade("Email", f"Enviado: {campanha.title}"))
                        enviados += 1
                    #   print(f" DEBUG ✓ Email enviado para {contato.name}")
                    #elif not not_sent:
                    #   print(f"DEBUG - Email já enviado para {contato.name}")
                    #else:
                    #   print(f"DEBUG - {contato.name} não se encaixa no critério")
                
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
        
        #Relatório por estágio - normaliza os estágios para agrupamento consistente
        estagios_padrao = ["Lead", "Prospecto", "Proposta", "Negociação", "Venda Fechada"]
        por_estagio = {estagio: 0 for estagio in estagios_padrao}
        
        for c in self.contatos:
            stage_normalizado = self._normalize_text(c.sales_stage, case="title")
            if stage_normalizado in por_estagio:
                por_estagio[stage_normalizado] += 1
            else:
                #Se o estágio não está nos padrões, adiciona como "Outros"
                if "Outros" not in por_estagio:
                    por_estagio["Outros"] = 0
                por_estagio["Outros"] += 1
        
        print("\n--- Distribuição por Estágio ---")
        for estagio, qtd in por_estagio.items():
            if qtd > 0:  #Só mostra estágios que têm contatos
                print(f"{estagio}: {qtd} contato(s)")

    def get_menu_by_role(self):
        strategy = self._menu_strategies.get(self.current_user_role, ClienteMenuStrategy())
        return strategy.get_menu()        
    
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