![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow.svg)

# Sistema de Gerenciamento de Relacionamento com o Cliente (CRM)

Sistema de CRM (Customer Relationship Management) desenvolvido em Python como projeto acadêmico da disciplina de Projeto de Software.
## 🚀 Funcionalidades

### ✅ Implementadas

- **📋 Gerenciamento de Contatos**: Armazena e gerencie informações completas de contato (nome, e-mail, telefone).
- **📈 Funil de Vendas**: Gerencia as etapas do processo de vendas com histórico de mudanças de estágio.
- **📝 Rastreamento de Atividades**: Registre interações como chamadas, e-mails e reuniões.
- **⏰ Agendamento de Tarefas**: Organiza tarefas e compromissos com datas específicas.
- **📧 Campanhas de E-mail**: Crie e envie campanhas segmentadas por estágio de vendas.
- **🎯 Gerenciamento de Leads**: Rastreio de leads e conversão em contatos.
- **📊 Relatórios e Análises**: Visualize resumos de vendas e distribuição por estágio.
- **🎨 Painéis Personalizáveis**: Menus customizáveis por perfil de usuário.
- **📁 Gerenciamento de Documentos**: Armazenamento de arquivos relacionados a vendas.

## 🆕 Refatoração
### ⚠️ Implementação Parcial
**Mobile Access**
**Funcionalidades Implementadas:**
- **Acesso via QR Code**: O sistema gera automaticamente um QR code para acesso móvel.
- **Interface Web Responsiva**: O dashboard HTML é acessível via navegador móvel.
- **API REST Completa**: Todos os endpoints podem ser consumidos por apps móveis.

**Funcionalidades Não Implementadas:**
- **App Nativo**: Não há aplicativo iOS/Android dedicado.
- **Push Notifications**: Notificações push não implementadas.
- **Sincronização Offline**: Requer conexão com internet.
### 🆙 Melhorias
- Normalizei os inputs e como os dados são tratados.
- Na mudança de Lead para Contato, agora a base é Prospecto e não Lead.
- Adicionei score para os Lead
- Melhorei a organização das definições dos Lead e Contato

## 🛠️ Instalação e Execução

### Pré-requisitos

- Python 3.8 ou superior instalado

### Como executar

1. **Clone o repositório**
   ```bash
   git clone github.com/https://github.com/LarissaFDS/crm-tool-PS-OO-main
   cd crm-tool-PS-OO
   ```
2. **Baixe as bibliotecas necessárias**
   ```bash
   pip install -r requirements.txt
   ```
   
3. **Execute o sistema**
   ```bash
   python main.py
   ```

4. **Navegue pelo menu**
   - O programa apresentará um menu interativo.
   - Digite o número da opção desejada e pressione Enter.
   - Para iniciar o servidor online, é necessário ler o QR code.
   - Os dados são salvos automaticamente em `crm_data.json`.


## 🧶 **Design Patterns**
## Creational
### 1. Singleton
- O que é e por quê?

   O padrão Singleton garante que uma classe tenha apenas uma única instância em toda a aplicação. CRM é a candidata perfeita. Só deve existir um "cérebro" para o sistema, que gerencia todas as listas de contatos, leads, etc. Isso evita a criação acidental de um segundo objeto CRM, o que poderia levar a inconsistências de dados.

- Onde coloquei

   A implementação foi feita diretamente na classe CRM no arquivo core/crm.py.

### 2. Factory Method 
- O que é e por quê?

   O padrão Factory encapsula a lógica de criação de objetos. Em vez de chamar o construtor de uma classe diretamente (ex: Atividade("email", ...)), pede a uma "fábrica" para criar o objeto. Isso é útil porque centraliza a lógica de criação. No caso, o programa cria diferentes tipos de Atividade ("chamada", "email", "reunião"). Uma AtividadeFactory poderia simplificar isso e até permitir a implementação de subclasses de Atividade no futuro sem alterar o código que solicita a criação.

- Onde coloquei (ainda nao implementei)

   Criei uma classe AtividadeFactory dentro do arquivo models/atividade.py. Em vez de chamar Atividade(tipo, desc), chamo AtividadeFactory.criar(tipo, desc).

### 3. Builder
- O que é e por quê?

   O padrão Builder é usado para construir objetos complexos passo a passo. Ele é ideal para objetos que têm muitos atributos, especialmente opcionais. A classe Contato é um ótimo exemplo: ela tem nome, email, telefone, e também empresa (opcional), notas (opcional), além de listas de atividades e tarefas que são adicionadas com o tempo. Um ContatoBuilder tornaria a criação de um contato mais legível e flexível.

- Onde coloquei (ainda nao implementei)

   Criei uma nova classe ContatoBuilder dentro do arquivo models/contact.py. A criação de um contato, que antes era é c = Contato(...), se tornaria algo como:

   ```bash
      builder = ContatoBuilder("Nome", "email@exemplo.com", "9999-9999")
      contato = builder.com_empresa("Empresa X").com_notas("Nota importante").build()
   ```

## 🏗️ Estrutura do Projeto

```
crm-tool-PS-OO/
├── 📁 core/
│   ├── __init__.py
│   └── crm.py                 # Classe principal do CRM
├── 📁 models/
│   ├── __init__.py
│   ├── base.py               # Classes abstratas e enums
│   ├── contact.py            # Contato e Lead
│   ├── atividade.py          # Registro de atividades
│   ├── task.py               # Tarefas e lembretes
│   ├── document.py           # Documentos
│   └── campanha.py           # Campanhas de email
├── main.py                   # Ponto de entrada
├── app.py                    # FastApi
├── index.html                # FrontEnd
├── requirements.txt          # Bibliotecas necessárias
├── LICENSE                   # Licença MIT
├── README.md                 # Este arquivo
└── crm_data.json             # Dados persistidos 
```

## 💻 Como Usar

### 1. **Primeiro Acesso**
- Execute `python main.py`
- O sistema inicia como "cliente" - escolha um perfil
- Selecione seu perfil (1 - Admin, 2- Vendedor, 3 - Marketing)

### 2. **Fluxo Básico (Administrador)**
```
1. Adicionar lead (fonte: Website, Redes Sociais, etc.)
2. Converter lead em contato (adiciona telefone e empresa)
3. Registrar atividades (chamadas, emails, reuniões)
4. Atualizar estágio de venda (Lead → Prospecto → Proposta → Negociação → Fechado)
5. Criar campanha de email segmentada
6. Enviar campanha para contatos específicos
7. Visualizar relatórios
```

### 3. **Perfis de Usuário**

#### 👨‍💼 **Administrador**
- Acesso completo a todas as funcionalidades
- Gestão de leads, contatos, campanhas
- Relatórios completos

#### 💼 **Vendedor**
- Foco em gestão de contatos
- Registro de atividades e tarefas
- Controle do pipeline de vendas
- Documentos relacionados a vendas

#### 📊 **Marketing**
- Gestão de leads e campanhas
- Conversão de leads qualificados
- Relatórios de campanhas