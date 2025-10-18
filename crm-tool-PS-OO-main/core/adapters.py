from abc import ABC, abstractmethod

class LeadAdapter(ABC): #interface que o crm espera
    @abstractmethod
    def get_crm_compatible_data(self) -> dict:
        pass
    
class ExternalLeadSystemAdapter(LeadAdapter):
    def __init__(self, external_data: dict):
        self._external_data = external_data
        print(f"\n [Adapter] Recebido dado externo incompatível: {self._external_data}")
        
    def get_crm_compatible_data(self): #mapeamento
        crm_data = {
            "name": self._external_data.get("full_name"),
            "email": self._external_data.get("contact_email"),
            "source": self._external_data.get("origin_platform")
        }
        
        source_normalizada = crm_data.get("source", "").strip().lower()
        try:
            if source_normalizada == "palestra":
                crm_data["source"] = "Evento"
                
            elif not source_normalizada:
                crm_data["source"] = "Outro" #valor padrao
        except Exception as e:
            print(f"ERRO {e}")        
        print(f"[Adapter] Dado traduzido para o formato do CRM: {crm_data}")
        return crm_data