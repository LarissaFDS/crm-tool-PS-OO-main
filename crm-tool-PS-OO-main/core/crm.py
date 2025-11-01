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

from .validators import SafeInput, Validators, ValidationError

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
        except FileNotFoundError:
            print(f"ERRO CRÍTICO: Arquivos de dados '{DATA_FILE.name}' não foi encontrado, mas existia antes.")
            self.contatos, self.campanhas, self.leads, self.documents = [], [], [], []
            
        except json.JSONDecodeError:
            print(f"ERRO CRÍTICO: O arquivo de dados '{DATA_FILE.name}' está corrompido (JSON inválido).")
            print("Carregando o sistema com dados vazios para evitar perda de dados.")
            self.contatos, self.campanhas, self.leads, self.documents = [], [], [], []
             
        except Exception as e:
            print(f"--- DEBUG: Erro inesperado ao carregar dados: {e} ---")
            self.contatos, self.campanhas, self.leads, self.documents = [], [], [], []

    def add_contato(self):
        print("\n=== Novo contato ===")
        
        name = SafeInput.get_name("Nome: ")
        if name is None:
            print("Operação cancelada.")
            return
        
        email = SafeInput.get_email("Email (nome@email.com): ")
        if email is None:
            print("Operação cancelada.")
            return
        
        telefone = SafeInput.get_phone("Telefone: ")
        if telefone is None:
            print("Operação cancelada.")
            return
        
        empresa = SafeInput.get_name("Empresa (opcional): ", required=False) or ""
        notes = input("Notas (opcional): ").strip()
        
        print("\nDeseja adicionar informações extras (tarefas, estágio diferente, etc.)? (s/n)")
        extras = SafeInput.get_choice("", ['s', 'n'], case_sensitive=False)
        
        if extras is None:
            extras = 'n'
        
        try:
            builder = create_contact().with_basic_info(name, email, telefone)
            
            if empresa:
                builder.with_empresa(empresa)
            if notes:
                builder.with_notas(notes)
            
            if extras == 's':
                print("\n--- Informações extras ---")

                valid_activities = ['chamada', 'email', 'reunião', 'cadastro']
                print(f"\nTipos de atividade:")
                for i, activity in enumerate(valid_activities, 1):
                    print(f"{i}. {activity}")
                
                print("\nEscolha o tipo de atividade (número ou nome, enter para pular):")
                ativ_input = input("Tipo: ").strip()
                
                ativ_tipo = None
                if ativ_input:
                    try:
                        ativ_idx = int(ativ_input)
                        if 1 <= ativ_idx <= len(valid_activities):
                            ativ_tipo = valid_activities[ativ_idx - 1]
                    except ValueError:
                        ativ_tipo = SafeInput.get_choice(
                            f"Confirme se '{ativ_input}' existe. Tente reescrever.: ",
                            valid_activities,
                            case_sensitive=False
                        )
                
                if ativ_tipo:
                    ativ_desc = input("Descrição da atividade: ").strip()
                    if ativ_desc:
                        builder.with_activity(ativ_tipo, ativ_desc)

                print("\nDeseja criar uma tarefa inicial? (s/n)")
                criar_task = SafeInput.get_choice("", ['s', 'n'], case_sensitive=False)
                
                if criar_task == 's':
                    task_title = input("Título da tarefa: ").strip()
                    if task_title:
                        task_date = SafeInput.get_date("Data (dd/mm/aaaa): ")
                        if task_date:
                            builder.with_task(task_title, task_date)

                print("\nDeseja definir estágio inicial diferente de 'Prospecto'? (s/n)")
                mudar_stage = SafeInput.get_choice("", ['s', 'n'], case_sensitive=False)
                
                if mudar_stage == 's':
                    stages = [stage.value for stage in SalesStage]
                    print(f"\nEstágios disponíveis:")
                    for i, stage in enumerate(stages, 1):
                        print(f"{i}. {stage}")
                    
                    print("\nEscolha o estágio (digite o número ou o nome):")
                    stage_input = input("Estágio: ").strip()
                    
                    stage = None
                    try:
                        stage_idx = int(stage_input)
                        if 1 <= stage_idx <= len(stages):
                            stage = stages[stage_idx - 1]
                        else:
                            print(f"❌ Número inválido. Usando estágio padrão 'Prospecto'.")
                    except ValueError:
                        stage = SafeInput.get_choice(
                            f"Confirme se o estágio '{stage_input}' existe. Tente reescrever.: ",
                            stages,
                            case_sensitive=False
                        )
                    
                    if stage:
                        builder.with_sales_stage(stage)
            else:
                builder.with_activity("cadastro", "Contato cadastrado no sistema")
            
            contato = builder.build()
            self.contatos.append(contato)
            self.save_data()
            print("✅ Contato criado com sucesso!")
            
        except ValidationError as e:
            print(f"❌ Erro de validação: {e}")
        except ValueError as e:
            print(f"❌ Erro: {e}")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

    def listar_contatos(self):
        if not self.contatos:
            print("Nenhum contato cadastrado.")
            return
        
        print("\n=== Lista de contatos ===")
        for i, c in enumerate(self.contatos):
            print(f"{i+1}. {c.name} - {c.email} - {c.sales_stage}")

    def change_user_role(self):
        print("\nPerfis disponíveis:")
        print("1. Gerente")
        print("2. Vendedor") 
        print("3. Marketing")
        
        choice = SafeInput.get_choice(
            "Escolha seu perfil: ",
            ['1', '2', '3']
        )
        
        if choice is None:
            print("Operação cancelada. Mantendo perfil atual.")
            return
        
        role_map = {
            "1": UserRole.ADM,
            "2": UserRole.VENDEDOR,
            "3": UserRole.MARKETING
        }
        
        self.current_user_role = role_map[choice]
        print(f"✅ Perfil alterado para: {self.current_user_role.value}")

    def add_document(self):
        print("\n=== Novo documento ===")
        
        titulo = input("Título do documento: ").strip()
        if not titulo:
            print("❌ Título não pode estar vazio.")
            return
        
        file_path = input("Caminho do arquivo: ").strip()
        if not file_path:
            print("❌ Caminho não pode estar vazio.")
            return
        
        valid_doc_types = ['proposta', 'contrato', 'outro', 'geral']
        print(f"Tipos disponíveis: {', '.join(valid_doc_types)}")
        
        doc_type = SafeInput.get_choice(
            "Tipo: ",
            valid_doc_types,
            case_sensitive=False
        )
        
        if doc_type is None:
            doc_type = "outro"
            print(f"Usando tipo padrão: {doc_type}")
        
        try:
            doc = Document(titulo, file_path, doc_type)
            self.documents.append(doc)
            
            print("\nDeseja associar a um contato? (s/n)")
            response = SafeInput.get_choice("", ['s', 'n'], case_sensitive=False)
            
            associado = False
            
            if response == 's':
                self.listar_contatos()
                
                idx = SafeInput.get_number(
                    "Escolha o contato (número): ",
                    min_val=1,
                    max_val=len(self.contatos)
                )
                
                if idx:
                    contato_selecionado = self.contatos[idx - 1]
                    contato_selecionado.documents.append(doc)
                    print(f"✅ Documento associado ao contato {contato_selecionado.name}.")
                    associado = True
            
            self.save_data()
            
            if not associado:
                print("✅ Documento adicionado ao sistema, mas sem associação.")
        
        except Exception as e:
            print(f"❌ Erro ao adicionar documento: {e}")


    def list_documentos(self):
        if not self.documents:
            print("Nenhum documento encontrado.")
            return
        
        print("\n=== Documentos ===")
        for i, doc in enumerate(self.documents):
            print(f"{i+1}. {doc.title} ({doc.doc_type}) - {doc.created_at}")

    def add_lead(self):
        print("\n=== Novo lead ===")
        
        name = SafeInput.get_name("Nome: ")
        if name is None:
            print("Operação cancelada.")
            return
        
        email = SafeInput.get_email("Email (nome@email.com): ")
        if email is None:
            print("Operação cancelada.")
            return
        
        fontes_disponiveis = [source.value for source in LeadSource]
        print(f"\nFontes disponíveis:")
        for i, fonte in enumerate(fontes_disponiveis, 1):
            print(f"{i}. {fonte}")
        
        print("\nEscolha a fonte (digite o número ou o nome):")
        fonte_input = input("Fonte: ").strip()
        
        source = None
        if not fonte_input:
            source = LeadSource.WEBSITE.value
            print(f"Usando fonte padrão: {source}")
        else:
            try:
                fonte_idx = int(fonte_input)
                if 1 <= fonte_idx <= len(fontes_disponiveis):
                    source = fontes_disponiveis[fonte_idx - 1]
                else:
                    print(f"❌ Número inválido. Usando fonte padrão 'Website'.")
                    source = LeadSource.WEBSITE.value
            except ValueError:
                source = SafeInput.get_choice(
                    f"Confirme se a fonte '{fonte_input}' existe. Tente reescrever.: ",
                    fontes_disponiveis,
                    case_sensitive=False
                )
                if source is None:
                    source = LeadSource.WEBSITE.value
                    print(f"Usando fonte padrão: {source}")
        
        try:
            new_lead = PessoaFactoryManager.create_person(
                'lead',
                name=name,
                email=email,
                source=source
            )
            self.leads.append(new_lead)
            self.save_data()
            print(f"✅ Lead adicionado com sucesso! Pontuação inicial: {new_lead.score}")
            
        except ValidationError as e:
            print(f"❌ Erro de validação: {e}")
        except ValueError as e:
            print(f"❌ Erro: {e}")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

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

        print("\n=== Leads para converter ===")
        for i, l in enumerate(ativos):
            print(f"{i+1}. {l.name} - {l.email} - Fonte: {l.source}")
        
        idx = SafeInput.get_number(
            "Escolha um lead (número): ",
            min_val=1,
            max_val=len(ativos)
        )
        
        if idx is None:
            print("Operação cancelada.")
            return
        
        lead = ativos[idx - 1]
        
        telefone = SafeInput.get_phone("Telefone: ")
        if telefone is None:
            print("Operação cancelada.")
            return
        
        empresa = SafeInput.get_name("Empresa (opcional): ", required=False) or ""
        notes = f"Convertido de lead (Fonte: {lead.source})"
        
        try:
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
            print("✅ Lead convertido em contato!")
            self.notify(event="lead_converted", data=contato)
            
        except ValidationError as e:
            print(f"❌ Erro de validação: {e}")
        except ValueError as e:
            print(f"❌ Erro: {e}")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

    def add_atividade(self):
        if not self.contatos:
            print("Nenhum contato cadastrado.")
            return
        
        self.listar_contatos()
        
        idx = SafeInput.get_number(
            "Escolha o contato (número): ",
            min_val=1,
            max_val=len(self.contatos)
        )
        
        if idx is None:
            print("Operação cancelada.")
            return
        
        contato_selecionado = self.contatos[idx - 1]
        
        valid_activities = ['chamada', 'email', 'reunião', 'cadastro', 'outro']
        print(f"\nTipos de atividade:")
        for i, activity in enumerate(valid_activities, 1):
            print(f"{i}. {activity}")
        
        print("\nEscolha o tipo (digite o número ou o nome):")
        tipo_input = input("Tipo: ").strip()
        
        tipo = None
        try:
            tipo_idx = int(tipo_input)
            if 1 <= tipo_idx <= len(valid_activities):
                tipo = valid_activities[tipo_idx - 1]
            else:
                print(f"❌ Número inválido. Escolha entre 1 e {len(valid_activities)}.")
                return
        except ValueError:
            tipo = SafeInput.get_choice(
                f"Confirme se o tipo '{tipo_input}' existe. Tente reescrever.: ",
                valid_activities,
                case_sensitive=False
            )
            if tipo is None:
                print("Operação cancelada.")
                return
        
        desc = input("Descrição: ").strip()
        if not desc:
            print("❌ Descrição não pode estar vazia.")
            return
        
        try:
            new_activity = Atividade(tipo, desc)
            contato_selecionado.activities.append(new_activity)
            self.save_data()
            
            self.notify("activity_added", {
                "contato": contato_selecionado,
                "activity": new_activity
            })
            
            print("✅ Atividade registrada!")
            
        except Exception as e:
            print(f"❌ Erro ao registrar atividade: {e}")
        
    def add_task(self):
        if not self.contatos:
            print("Nenhum contato cadastrado.")
            return
        
        self.listar_contatos()
        
        idx = SafeInput.get_number(
            "Escolha o contato (número): ",
            min_val=1,
            max_val=len(self.contatos)
        )
        
        if idx is None:
            print("Operação cancelada.")
            return
        
        contato = self.contatos[idx - 1]
        
        titulo = input("Título da tarefa: ").strip()
        if not titulo:
            print("❌ Título não pode estar vazio.")
            return
        
        data = SafeInput.get_date("Data (dd/mm/aaaa): ")
        if data is None:
            print("Operação cancelada.")
            return
        
        try:
            contato.tasks.append(Task(titulo, data))
            self.save_data()
            print("✅ Tarefa adicionada!")
            
        except Exception as e:
            print(f"❌ Erro ao adicionar tarefa: {e}")
        
                
    def completar_task(self):
        if not self.contatos:
            print("Nenhum contato cadastrado.")
            return
        
        self.listar_contatos()
        
        idx = SafeInput.get_number(
            "Escolha o contato para ver as tarefas (número): ",
            min_val=1,
            max_val=len(self.contatos)
        )
        
        if idx is None:
            print("Operação cancelada.")
            return
        
        contato = self.contatos[idx - 1]
        
        tarefas_pendentes = [task for task in contato.tasks if not task.completed]
        
        if not tarefas_pendentes:
            print(f"O contato {contato.name} não possui tarefas pendentes.")
            return
        
        print(f"\n--- Tarefas Pendentes de {contato.name} ---")
        for i, task in enumerate(tarefas_pendentes):
            print(f"{i+1}. {task.title} - Data: {task.date}")
        
        task_idx = SafeInput.get_number(
            "Escolha a tarefa para marcar como concluída (número): ",
            min_val=1,
            max_val=len(tarefas_pendentes)
        )
        
        if task_idx is None:
            print("Operação cancelada.")
            return
        
        try:
            tarefa_concluida = tarefas_pendentes[task_idx - 1]
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
            
        except Exception as e:
            print(f"❌ Erro ao completar tarefa: {e}")
            
    def update_sales_stage(self):
        if not self.contatos:
            print("Nenhum contato cadastrado.")
            return
        
        self.listar_contatos()
        
        idx = SafeInput.get_number(
            "Escolha o contato (número): ",
            min_val=1,
            max_val=len(self.contatos)
        )
        
        if idx is None:
            print("Operação cancelada.")
            return
        
        contato = self.contatos[idx - 1]
        old_stage = contato.sales_stage
        
        print(f"\nEstágio atual: {old_stage}")
        
        stages = [stage.value for stage in SalesStage]
        print(f"\nEstágios disponíveis:")
        for i, stage in enumerate(stages, 1):
            print(f"{i}. {stage}")
        
        print("\nEscolha o novo estágio (digite o número ou o nome):")
        stage_input = input("Novo estágio: ").strip()
        
        novo = None
        try:
            stage_idx = int(stage_input)
            if 1 <= stage_idx <= len(stages):
                novo = stages[stage_idx - 1]
            else:
                print(f"❌ Número inválido. Escolha entre 1 e {len(stages)}.")
                return
        except ValueError:
            novo = SafeInput.get_choice(
                f"Confirme se o estágio '{stage_input}' existe. Tente reescrever.: ",
                stages,
                case_sensitive=False
            )
            if novo is None:
                print("Operação cancelada.")
                return
        
        try:
            contato.sales_stage = novo
            contato.stage_history.append(novo)
            self.save_data()
            
            self.notify("stage_changed", {
                "contato": contato,
                "old_stage": old_stage,
                "new_stage": novo
            })
            
            print(f"✅ Estágio atualizado: {old_stage} → {novo}")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar estágio: {e}")


    def add_email_campanha(self):
        print("\n=== Nova campanha de email ===")
        
        titulo = input("Título da campanha: ").strip()
        if not titulo:
            print("❌ Título não pode estar vazio.")
            return
        
        descricao = input("Descrição: ").strip()
        if not descricao:
            print("❌ Descrição não pode estar vazia.")
            return
        
        stages = [stage.value for stage in SalesStage] + ["Todos"]
        print(f"\nEstágios disponíveis:")
        for i, stage in enumerate(stages, 1):
            print(f"{i}. {stage}")
        
        print("\nEscolha o estágio alvo (digite o número ou o nome):")
        stage_input = input("Estágio: ").strip()
        
        target_stage = None
        try:
            stage_idx = int(stage_input)
            if 1 <= stage_idx <= len(stages):
                target_stage = stages[stage_idx - 1]
            else:
                print(f"❌ Número inválido. Escolha entre 1 e {len(stages)}.")
                return
        except ValueError:
            target_stage = SafeInput.get_choice(
                f"Confirme se o estágio '{stage_input}' existe. Tente reescrever.: ",
                stages,
                case_sensitive=False
            )
            if target_stage is None:
                print("Operação cancelada.")
                return
        
        print("\nDeseja configurações avançadas? (s/n)")
        advanced = SafeInput.get_choice("", ['s', 'n'], case_sensitive=False)
        
        if advanced is None:
            advanced = 'n'
        
        try:
            builder = create_campaign().with_basic_info(titulo, descricao, target_stage)
            
            if advanced == 's':
                print("\n--- Configurações avançadas ---")
                
                print("Deseja pré-selecionar destinatários específicos? (s/n)")
                pre_select = SafeInput.get_choice("", ['s', 'n'], case_sensitive=False)
                
                if pre_select == 's':
                    self.listar_contatos()
                    recipient_ids = []
                    
                    print("\nDigite o número do contato da lista (UM por vez, 'fim' para terminar):")
                    while True:
                        contact_input = input("Número do contato: ").strip().lower()
                        if contact_input == 'fim':
                            break
                        
                        try:
                            contact_idx = int(contact_input)
                            if 1 <= contact_idx <= len(self.contatos):
                                contact_id = self.contatos[contact_idx - 1].id
                                contact_name = self.contatos[contact_idx - 1].name
                                
                                if contact_id not in recipient_ids:
                                    recipient_ids.append(contact_id)
                                    print(f"✅ Contato '{contact_name}' adicionado à lista.")
                                else:
                                    print(f"⚠️  Contato '{contact_name}' já foi adicionado.")
                            else:
                                print(f"❌ Número inválido. Escolha entre 1 e {len(self.contatos)}.")
                        except ValueError:
                            print("❌ Digite um número válido ou 'fim' para terminar.")
                    
                    if recipient_ids:
                        builder.with_recipients(recipient_ids)
            
            campanha = builder.build()
            self.campanhas.append(campanha)
            self.save_data()
            
            print("✅ Campanha criada com sucesso!")
            if hasattr(campanha, 'sent_to') and campanha.sent_to:
                print(f"📧 Pré-configurada para {len(campanha.sent_to)} destinatário(s) específico(s).")
        
        except ValidationError as e:
            print(f"❌ Erro de validação: {e}")
        except ValueError as e:
            print(f"❌ Erro: {e}")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")

    
    def send_email_campanha(self):
        if not self.campanhas:
            print("Nenhuma campanha criada.")
            return

        print("\n=== Campanhas disponíveis ===")
        for i, c in enumerate(self.campanhas):
            print(f"{i+1}. {c.title} - Alvo: {c.target_stage}")

        idx = SafeInput.get_number(
            "Escolha a campanha (número): ",
            min_val=1,
            max_val=len(self.campanhas)
        )
        
        if idx is None:
            print("Operação cancelada.")
            return
        
        try:
            campanha = self.campanhas[idx - 1]
            enviados = 0
            
            for contato in self.contatos:
                contato_stage_norm = self._normalize_text(contato.sales_stage, case="title")
                target_stage_norm = self._normalize_text(campanha.target_stage, case="title")
                
                stage_match = (contato_stage_norm == target_stage_norm or target_stage_norm == "Todos")
                not_sent = contato.id not in campanha.sent_to
                
                if stage_match and not_sent:
                    campanha.sent_to.append(contato.id)
                    contato.activities.append(Atividade("Email", f"Enviado: {campanha.title}"))
                    enviados += 1
            
            if enviados > 0:
                self.save_data()
                print(f"✅ Campanha enviada com sucesso para {enviados} contato(s).")
            else:
                print("⚠️  Nenhum contato encontrado para esta campanha.")
        
        except Exception as e:
            print(f"❌ Erro ao enviar campanha: {e}")

    def report_summary(self):
        print("\n=== Relatório geral ===")
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
        
        print("\n--- Distribuição por estágio ---")
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