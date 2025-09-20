from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import FileResponse
from starlette import status

from core import CRM 
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from models.contact import Contato, Lead
from models.campanha import EmailCampanha

#----------------- Modelo para Contato -------------------
class ContatoSchema(BaseModel): #criar contato
    name: str
    email: EmailStr #ja valida o email
    telefone: str
    empresa: Optional[str] = None
    notas: Optional[str] = None

class ContatoResponse(ContatoSchema): #enviar a estrutura de dados de volta
    id: int
    sales_stage: str
    
    class Config:
        from_attributes = True
        
#----------------- Modelo para Lead -------------------
class LeadSchema(BaseModel):
    name: str
    email: EmailStr
    source: Optional[str] = "Website"
    
class LeadResponse(LeadSchema):
    id: int
    score: int
    converted: bool
    
    class Config:
        from_attributes = True
        
#----------------- Modelo para Campanha -------------------       
class CampanhaSchema(BaseModel):
    title: str
    description: str
    target_stage: str

class CampanhaResponse(CampanhaSchema):
    id: int
    created_at: str
    sent_to: List[int] = []

    class Config:
        from_attributes = True
        
#----------------- Modelos para Atividade -------------------
class AtividadeSchema(BaseModel):
    type: str
    description: str

class AtividadeResponse(AtividadeSchema):
    date: str
    
    class Config:
        from_attributes = True

#----------------- Modelos para Task -------------------
class TaskSchema(BaseModel):
    title: str
    date: str

class TaskResponse(TaskSchema):
    completed: bool
    
    class Config:
        from_attributes = True
        
#-------------------- Segurança minima ------------------        
API_KEY_SECRETA = "secreto123"

async def verificar_api_key(api_key_header: str = Header(..., alias="x-api-key")):
    if api_key_header != API_KEY_SECRETA:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave de API inválida ou ausente",
        )

#-------------------- Inicializar a API ------------------------        
app = FastAPI(
    title="CRM API",
    description="API para gerenciar contatos, leads e outras funcionalidades do CRM.",
    version="1.0.0"
)

crm = CRM() 

#---------------- Rota principal -------------------
@app.get("/", response_class=FileResponse)
def pegar_html_interface(): #rota para o front-end em HTML
    return "index.html"

#-------------------------- Rotas para Contato ------------------------
@app.get("/contatos", response_model=List[ContatoResponse], dependencies=[Depends(verificar_api_key)])
def listar_contatos(): #Retorna uma lista com todos os contatos cadastrados.
    #o FastAPI converte a lista de objetos Python para JSON automaticamente.
    return crm.contatos

@app.get("/contatos/{contato_id}", response_model=ContatoResponse, dependencies=[Depends(verificar_api_key)])
def buscar_contato_por_id(contato_id: int): #busca UM contato por id, caso não seja encontrado, retorna erro 404
    for contato in crm.contatos:
        if contato.id == contato_id:
            return contato #se econtrar retorna o codigo 200 (padrão)

    raise HTTPException(
        status_code=404,
        detail=f"Contato com ID {contato_id} não encontrado :("
    )

#----------------- Pegar dados de Contato -----------------------
@app.post("/contatos", response_model=ContatoResponse, status_code=201, dependencies=[Depends(verificar_api_key)]) #usa 2xx pq é codigo de sucesso, assim como 4xx é de erro do cliente, por exemplo.
def criar_contato(contato_data: ContatoSchema): #cria um novo contato no sistema
    novo_contato = Contato(
        name=contato_data.name,
        email=contato_data.email,
        telefone=contato_data.telefone,
        empresa=contato_data.empresa or "",
        notas=contato_data.notas or ""
    )

    crm.contatos.append(novo_contato)
    crm.save_data()
    
    return novo_contato

#-------------------- Interagir com Contato --------------------------
@app.delete("/contatos/{contato_id}", status_code=204, dependencies=[Depends(verificar_api_key)])
def deletar_contato(contato_id: int): #deleta contato por ID
    contato_encontrado = None
    for contato in crm.contatos:
        if contato.id == contato_id:
            contato_encontrado = contato
            break

    if not contato_encontrado: #Se o contato não foi encontrado, da erro 404
        raise HTTPException(
            status_code=404,
            detail=f"Contato com ID {contato_id} não encontrado"
        )

    #Se foi encontrado, remove-o da lista e salva a alteração
    crm.contatos.remove(contato_encontrado)
    crm.save_data()

    return

@app.put("/contatos/{contato_id}", response_model=ContatoResponse, dependencies=[Depends(verificar_api_key)])
def atualizar_contato(contato_id: int, contato_data: ContatoSchema): #pode atualizar informações
    contato_encontrado = None
    for contato in crm.contatos:
        if contato.id == contato_id:
            contato_encontrado = contato
            break
    
    if not contato_encontrado: #Se não encontrar o contato, retorna erro 404
        raise HTTPException(
            status_code=404,
            detail=f"Contato com ID {contato_id} não encontrado"
        )

    #atualiza todos os campos do objeto que encontramos, com os dados que vieram no corpo da requisição
    contato_encontrado.name = contato_data.name
    contato_encontrado.email = contato_data.email
    contato_encontrado.telefone = contato_data.telefone
    contato_encontrado.empresa = contato_data.empresa
    contato_encontrado.notas = contato_data.notas
    
    crm.save_data() #salva os dados atualizados no arquivo JSON
    
    return contato_encontrado #retorna o contato com as novas informações

#----------------------- Rotas para Lead ------------------------------
@app.get("/leads", response_model=List[LeadResponse], dependencies=[Depends(verificar_api_key)])
def listar_leads():
    #mostra apenas leads que ainda não foram convertidos em contatos
    leads_ativos = [lead for lead in crm.leads if not lead.converted]
    return leads_ativos

@app.get("/leads/{lead_id}", response_model=LeadResponse, dependencies=[Depends(verificar_api_key)])
def buscar_lead_por_id(lead_id: int): #Busca e retorna um único lead pelo seu ID.
    for lead in crm.leads:
        if lead.id == lead_id:
            return lead
    
    raise HTTPException(
        status_code=404,
        detail=f"Lead com ID {lead_id} não encontrado"
    )

#---------------------- Pegar dados de Lead -------------------------
@app.post("/leads", response_model=LeadResponse, status_code=201, dependencies=[Depends(verificar_api_key)])
def criar_lead(lead_data: LeadSchema): #Cria um novo lead no sistema.
    novo_lead = Lead(
        name=lead_data.name,
        email=lead_data.email,
        source=lead_data.source
    )
    crm.leads.append(novo_lead)
    crm.save_data()
    return novo_lead

#-------------------- Interagir com Lead --------------------------
@app.put("/leads/{lead_id}", response_model=LeadResponse, dependencies=[Depends(verificar_api_key)])
def atualizar_lead(lead_id: int, lead_data: LeadSchema):
    lead_encontrado = None
    for lead in crm.leads:
        if lead.id == lead_id:
            lead_encontrado = lead
            break

    if not lead_encontrado:
        raise HTTPException(
            status_code=404,
            detail=f"Lead com ID {lead_id} não encontrado"
        )

    #Atualiza os campos do objeto encontrado
    lead_encontrado.name = lead_data.name
    lead_encontrado.email = lead_data.email
    lead_encontrado.source = lead_data.source
    
    crm.save_data()
    return lead_encontrado

@app.delete("/leads/{lead_id}", status_code=204, dependencies=[Depends(verificar_api_key)])
def deletar_lead(lead_id: int): #Deleta um lead do sistema pelo seu ID.
    lead_encontrado = None
    for lead in crm.leads:
        if lead.id == lead_id:
            lead_encontrado = lead
            break

    if not lead_encontrado:
        raise HTTPException(
            status_code=404,
            detail=f"Lead com ID {lead_id} não encontrado"
        )

    crm.leads.remove(lead_encontrado)
    crm.save_data()
    return

#----------------------- Rotas para Campanha ------------------------------
@app.get("/campanhas", response_model=List[CampanhaResponse], dependencies=[Depends(verificar_api_key)])
def listar_campanhas(): #Retorna uma lista de todas as campanhas
    return crm.campanhas

@app.get("/campanhas/{campanha_id}", response_model=CampanhaResponse, dependencies=[Depends(verificar_api_key)])
def buscar_campanha_por_id(campanha_id: int): #Busca uma campanha específica pelo seu ID
    for campanha in crm.campanhas:
        if campanha.id == campanha_id:
            return campanha
    raise HTTPException(status_code=404, detail="Campanha não encontrada")

#---------------------- Pegar dados de Campanha -------------------------
@app.post("/campanhas", response_model=CampanhaResponse, status_code=201, dependencies=[Depends(verificar_api_key)])
def criar_campanha(campanha_data: CampanhaSchema): #Cria uma nova campanha de email
    nova_campanha = EmailCampanha(
        title=campanha_data.title,
        description=campanha_data.description,
        target_stage=campanha_data.target_stage
    )
    crm.campanhas.append(nova_campanha)
    crm.save_data()
    return nova_campanha

#-------------------- Interagir com Campanha --------------------------
@app.put("/campanhas/{campanha_id}", response_model=CampanhaResponse, dependencies=[Depends(verificar_api_key)])
def atualizar_campanha(campanha_id: int, campanha_data: CampanhaSchema): #Atualiza as informações de uma campanha
    campanha_encontrada = None
    for campanha in crm.campanhas:
        if campanha.id == campanha_id:
            campanha_encontrada = campanha
            break
    if not campanha_encontrada:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    
    campanha_encontrada.title = campanha_data.title
    campanha_encontrada.description = campanha_data.description
    campanha_encontrada.target_stage = campanha_data.target_stage
    crm.save_data()
    return campanha_encontrada

@app.delete("/campanhas/{campanha_id}", status_code=204, dependencies=[Depends(verificar_api_key)])
def deletar_campanha(campanha_id: int): #Deleta uma campanha do sistema
    campanha_encontrada = None
    for campanha in crm.campanhas:
        if campanha.id == campanha_id:
            campanha_encontrada = campanha
            break
    if not campanha_encontrada:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    
    crm.campanhas.remove(campanha_encontrada)
    crm.save_data()
    return
    
#----------------- Conversão de Lead para Contato -------------------
@app.post("/leads/{lead_id}/converter", dependencies=[Depends(verificar_api_key)])
def converter_lead_para_contato(lead_id: int, contato_data: ContatoSchema):
    #Buscar o lead
    lead_encontrado = None
    for lead in crm.leads:
        if lead.id == lead_id:
            lead_encontrado = lead
            break
    
    if not lead_encontrado:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    
    if lead_encontrado.converted:
        raise HTTPException(status_code=400, detail="Lead já foi convertido")
    
    #Criar novo contato baseado no lead
    novo_contato = Contato(
        name=lead_encontrado.name,
        email=lead_encontrado.email,
        telefone=contato_data.telefone,
        empresa=contato_data.empresa or "",
        notas=f"Convertido do lead ID {lead_id}. Fonte: {lead_encontrado.source}"
    )
    
    lead_encontrado.converted = True
    crm.contatos.append(novo_contato)
    crm.save_data()
    
    return {
        "message": "Lead convertido com sucesso",
        "contato": novo_contato.to_dict(),
        "lead_id": lead_id
    }

#----------------- Atualizar Estágio de Vendas -------------------
@app.put("/contatos/{contato_id}/stage", dependencies=[Depends(verificar_api_key)])
def atualizar_estagio_vendas(contato_id: int, novo_estagio: dict):
    for contato in crm.contatos:
        if contato.id == contato_id:
            estagio_anterior = contato.sales_stage
            contato.sales_stage = novo_estagio["stage"]
            contato.stage_history.append(novo_estagio["stage"])
            
            #Adicionar atividade automaticamente
            from models.atividade import Atividade
            atividade = Atividade(
                "stage_change", 
                f"Estágio alterado de '{estagio_anterior}' para '{novo_estagio['stage']}'"
            )
            contato.activities.append(atividade)
            
            crm.save_data()
            return {"message": "Estágio atualizado com sucesso"}
    
    raise HTTPException(status_code=404, detail="Contato não encontrado")

#----------------- Relatórios -------------------
@app.get("/relatorios/conversao", dependencies=[Depends(verificar_api_key)])
def relatorio_conversao():
    total_leads_criados = len(crm.leads)
    leads_convertidos = len([l for l in crm.leads if l.converted])
    taxa_conversao = (leads_convertidos / total_leads_criados * 100) if total_leads_criados > 0 else 0
    
    return {
        "total_leads": total_leads_criados,
        "leads_convertidos": leads_convertidos,
        "taxa_conversao": round(taxa_conversao, 2)
    }

@app.get("/relatorios/info", dependencies=[Depends(verificar_api_key)])
def relatorio_info():
    info_detalhada = {}
    for contato in crm.contatos:
        stage = contato.sales_stage
        if stage not in info_detalhada:
            info_detalhada[stage] = []
        
        info_detalhada[stage].append({
            "id": contato.id,
            "nome": contato.name,
            "empresa": contato.empresa,
            "email": contato.email
        })
    
    return info_detalhada