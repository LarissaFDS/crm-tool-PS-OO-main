from core.crm import CRM

class CRMFacade:
    def __init__(self):
        self._crm = CRM()
        self._CRMFacade = self
        self.current_user_role = self._crm.current_user_role
        self.menu_options = self
        
    def save_data(self):
        self._crm.save_data()
    
    def load_data(self):
        self._crm.load_data()
        
    def add_contato(self):
        self._crm.add_contato()
        
    def listar_contato(self):
        self._crm.listar_contatos()
        
    def change_user_role(self):
        self._crm.change_user_role()
        
    def add_document(self):
        self._crm.add_document()
        
    def list_documentos(self):
        self._crm.list_documentos()
        
    def add_lead(self):
        self._crm.add_lead()
        
    def attach(self, email_service):
        self._crm.attach(email_service)
        
    def detach(self, analytics_service):
        self._crm.detach(analytics_service)
        
    def notify(self, sales_team_channel):
        self._crm.notify(sales_team_channel)
        
    def converter_lead(self):
        self._crm.converter_lead()
        
    def add_atividade(self):
        self._crm.add_atividade()
        
    def add_task(self):
        self._crm.add_task()
    
    def completar_task(self):
        self._crm.completar_task()
    
    def update_sales_stage(self):
        self._crm.update_sales_stage()
        
    def add_email_campanha(self):
        self._crm.add_email_campanha()
        
    def send_email_campanha(self):
        self._crm.send_email_campanha()
        
    def report_summary(self):
        self._crm.report_summary()
    
    def get_menu_by_role(self):
        self._crm.get_menu_by_role()