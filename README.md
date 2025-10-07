![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow.svg)

# Sistema de Gerenciamento de Relacionamento com o Cliente (CRM)

Sistema de CRM (Customer Relationship Management) desenvolvido em Python como projeto acadêmico da disciplina de Projeto de Software.

## 🚀 Funcionalidades Principais

| Funcionalidade                     | CLI (main.py) | API & Web (app.py) | Descrição                                                              |
| ---------------------------------- | :-----------: | :----------------: | ------------------------------------------------------------------------ |
| **Gerenciamento de Contatos e Leads**|       ✅       |         ✅         | Criação, listagem, atualização e deleção de contatos e leads.            |
| **Funil de Vendas & Estágios**|       ✅       |         ✅         | Atribui e atualiza estágios de venda para contatos, com histórico.       |
| **Rastreamento de Atividades**|       ✅       |         ❌         | Registra interações como chamadas, e-mails e reuniões.                   |
| **Gestão de Tarefas**|       ✅       |         ❌         | Cria tarefas, atribui a contatos e marca como concluídas.                |
| **Campanhas de E-mail Marketing** |       ✅       |         ✅         | Cria e gerencia campanhas segmentadas por estágio de vendas.             |
| **Dashboard Web Interativo**|       ❌       |         ✅         | Interface gráfica para visualizar e interagir com os dados em tempo real.  |
| **Relatórios e Análises**|       ✅       |         ✅         | Exibe métricas de conversão e distribuição no funil de vendas.         |
| **Acesso Móvel via QR Code**|       ✅       |         ✅         | Gera um QR Code no terminal para fácil acesso ao dashboard web pelo celular. |


### 🆙 Melhorias Implementadas
- **Normalização de dados**: Inputs são normalizados e tratados consistentemente.
- **Conversão aprimorada**: Lead convertido inicia como "Prospecto" em vez de "Lead".
- **Sistema de pontuação**: Leads recebem score baseado na fonte de origem
- **Organização melhorada**: Estrutura mais clara para definições de Lead e Contato.
- **Gestão de tarefas**: Possibilidade de marcar tarefas como concluídas.

## 🛠️ Instalação e Execução

### Pré-requisitos

- Python 3.8 ou superior instalado.

### Como executar

1. **Clone o repositório**
   ```bash
   git clone https://github.com/LarissaFDS/crm-tool-PS-OO-main
   cd crm-tool-PS-OO
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```
   
3. **Execute o sistema**
   
   **Interface CLI (Terminal):**
   ```bash
   python main.py
   ```
   
   **API e Dashboard Web:**
   - Execute o comando CLI e escolha a opção "Iniciar servidor online".
   - Escaneie o QR Code exibido no terminal para acesso móvel.

4. **Navegação**
   - **CLI**: Menu interativo no terminal.
   - **Web**: Acesse via navegador (URL exibida no terminal).
   - Os dados são persistidos automaticamente em `crm_data.json`.

## 🧶 **Design Patterns Implementados**

### Creational Patterns

#### 1. **Singleton**
- **Propósito**: Garante uma única instância do CRM em toda a aplicação.
- **Por que usar**: Evita inconsistências nos dados e centraliza o controle do sistema.
- **Localização**: `core/crm.py` na classe CRM.

#### 2. **Abstract Factory** 
- **Propósito**: Centraliza e simplifica a criação de diferentes tipos de "Pessoas".
- **Por que usar**: Desacopla a lógica de criação, facilita validações e extensibilidade.
- **Localização**: 
  - `models/factory.py`: Implementação das factories.
  - `models/builder.py`: Utilizado para validação e criação simples.

#### 3. **Builder**
- **Propósito**: Constrói objetos complexos passo a passo.
- **Por que usar**: Facilita criação de contatos com muitos atributos opcionais.
- **Localização**: 
  - `models/builder.py`: Implementação dos builders.
  - `core/crm.py`: Método `add_contato`.
  - `core/crm.py`: Método `add_email_campanha`.


### Behavioral Patterns

#### 1. **Command**
- **Propósito**: Transforma uma solicitação em objeto autonomo.
- **Por que usar**: Facilita a manutenção do menu.
- **Localização**: 
   - `core/commands.py`: Implementação dos commands.
   - `main.py`: Utilizado para melhoria no menu.

#### 2. **Strategy** 
- **Propósito**: Varia independentemente do que é utilizado.
- **Por que usar**: Principio aberto/fechado, responsabilidade única e facilidade na manutenção.
- **Localização**: 
   - `core/strategy.py`: Implementação do strategy (possibilita criação de novos perfis).
   - `core/crm.py`: Delega a construção para o strategy. Não precisa modificar o get_menu_by_role().

#### 3. **Observer**
- **Propósito**: Define a dependência de um para muitos. (atualiza tudo)
- **Por que usar**: Desacopla a lógica principal, principio aberto/fechado e melhora a manutenibilidade.
- **Localização**: 
   - `core/observer.py`: Definição das interfaces e dos observers concretos.
   - `core/crm.py`: A classe CRM atua como o Subject, notificando os observers sobre eventos importantes.
   - `main.py`: Chamada da aplicação, onde os observers são "inscritos" no CRM.


### Structural Patterns

#### 1. **Facade**
- **Propósito**: 
- **Por que usar**: 
- **Localização**: 
   - `.py`: 
   - `.py`: 

#### 2. **Decorator** 
- **Propósito**: 
- **Por que usar**: 
- **Localização**: 
   - `.py`: 
   - `.py`: 

#### 3. **Adapter**
- **Propósito**:
- **Por que usar**: 
- **Localização**: 
   - `.py`: 
   - `.py`:
   - `.py`:

## 🏗️ Estrutura do Projeto

```
crm-tool-PS-OO/
├── 📁 core/
│   ├── __init__.py
│   └── crm.py                # Classe principal do CRM (Singleton)
├── 📁 models/
│   ├── __init__.py
│   ├── base.py               # Classes abstratas e enums
│   ├── contact.py            # Contato e Lead
│   ├── atividade.py          # Registro de atividades
│   ├── task.py               # Tarefas e lembretes
│   ├── document.py           # Documentos
│   ├── factory.py            # Factory Method para Pessoas
│   ├── builder.py            # Builder Pattern
│   └── campanha.py           # Campanhas de email
├── main.py                   # Interface CLI
├── app.py                    # API FastAPI e servidor web
├── index.html                # Dashboard web responsivo
├── requirements.txt          # Dependências Python
├── LICENSE                   # Licença MIT
├── README.md                 # Documentação
└── crm_data.json             # Persistência de dados
```

## 💻 Como Usar

### 1. **Primeiro Acesso**
- Mude para o seu caminho do index no app.py na linha 102
- Execute `python main.py`
- Escolha seu perfil de usuário (Admin/Vendedor/Marketing)
- O sistema guiará você pelas opções disponíveis

### 2. **Fluxo Básico (Administrador)**
```
1. Adicionar lead (Website, Redes Sociais, Indicação, etc.)
2. Converter lead qualificado em contato
3. Registrar atividades (chamadas, emails, reuniões)
4. Atualizar estágio: Lead → Prospecto → Proposta → Negociação → Venda Fechada
5. Criar campanhas de email segmentadas
6. Enviar campanhas para público-alvo
7. Acompanhar relatórios e métricas
```

### 3. **Perfis de Usuário e Permissões**

#### 👨‍💼 **Administrador**
- ✅ Acesso completo a todas as funcionalidades
- ✅ Gestão de leads, contatos e campanhas
- ✅ Relatórios e análises detalhadas
- ✅ Configuração do servidor web

#### 💼 **Vendedor**
- ✅ Gestão de contatos existentes
- ✅ Registro de atividades e tarefas
- ✅ Controle do pipeline de vendas
- ✅ Gestão de documentos
- ❌ Criação de leads e campanhas

#### 📊 **Marketing**
- ✅ Gestão completa de leads
- ✅ Criação e envio de campanhas
- ✅ Conversão de leads qualificados
- ✅ Relatórios de performance
- ❌ Gestão detalhada de contatos

## 🔧 Tecnologias Utilizadas

- **Backend**: Python 3.8+, FastAPI
- **Frontend**: HTML, JavaScript
- **Persistência**: JSON (arquivo local)
- **Servidor**: Uvicorn
- **Bibliotecas**: qrcode, pydantic, unicodedata

## 📱 Acesso Móvel

O sistema gera automaticamente um QR Code no terminal que permite acesso imediato via dispositivos móveis, facilitando o uso em campo pelos vendedores.

## 🔐 Segurança

A API utiliza autenticação via header `x-api-key` para fins demonstrativos (chave = secreto123). Em produção, recomenda-se implementar autenticação mais robusta (JWT, OAuth, etc.).

---

**Nota**: Este é um projeto acadêmico focado na aplicação prática de Design Patterns.