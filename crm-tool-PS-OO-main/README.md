![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow.svg)

# Sistema de Gerenciamento de Relacionamento com o Cliente (CRM)

Sistema de CRM (Customer Relationship Management) desenvolvido em Python como projeto acadêmico da disciplina de Projeto de Software com Orientação a Objetos. O sistema demonstra a aplicação prática dos principais conceitos de POO: herança, encapsulamento, polimorfismo e classes abstratas.

## 🚀 Funcionalidades

### ✅ Implementadas

- **📋 Gerenciamento de Contatos**: Armazena e gerencie informações completas de contato (nome, e-mail, telefone)
- **📈 Funil de Vendas**: Gerencia as etapas do processo de vendas com histórico de mudanças de estágio
- **📝 Rastreamento de Atividades**: Registre interações como chamadas, e-mails e reuniões
- **⏰ Agendamento de Tarefas**: Organiza tarefas e compromissos com datas específicas
- **📧 Campanhas de E-mail**: Crie e envie campanhas segmentadas por estágio de vendas
- **🎯 Gerenciamento de Leads**: Rastreio de leads e conversão em contatos
- **📊 Relatórios e Análises**: Visualize resumos de vendas e distribuição por estágio
- **🎨 Painéis Personalizáveis**: Menus customizáveis por perfil de usuário
- **📁 Gerenciamento de Documentos**: Armazenamento de arquivos relacionados a vendas

### ❌ Não Implementadas

- **📱 Acesso Mobile**: Funcionalidade para dispositivos móveis


### Conceitos POO Demonstrados

- ✅ Abstração: Classes representam entidades do mundo real
- ✅ Encapsulamento: Dados protegidos com validação
- ✅ Herança: Reutilização e especialização de código
- ✅ Polimorfismo: Interface uniforme, comportamentos diferentes

## 🛠️ Instalação e Execução

### Pré-requisitos

- Python 3.8 ou superior instalado

### Como executar

1. **Clone o repositório**
   ```bash
   git clone github.com/jwaozera/crm-tool-PS-OO
   cd crm-tool-PS-OO
   
3. **Execute o sistema**
   ```bash
   python main.py
   ```

4. **Navegue pelo menu**
   - O programa apresentará um menu interativo
   - Digite o número da opção desejada e pressione Enter
   - Os dados são salvos automaticamente em `crm_data.json`

## 📁 Estrutura de Dados

O sistema utiliza um arquivo JSON (`crm_data.json`) para persistência de dados, contendo:

- **Contatos**: Informações pessoais e histórico de vendas
- **Leads**: Potenciais clientes em prospecção
- **Atividades**: Registro de interações
- **Tarefas**: Compromissos agendados
- **Campanhas**: Histórico de e-mail marketing

## 🎯 Estágios de Vendas

O sistema gerencia os seguintes estágios:

- **Lead**: Primeiro contato identificado
- **Prospecto**: Lead qualificado em avaliação
- **Proposta**: Apresentação de soluções
- **Negociação**: Discussão de termos
- **Venda Fechada**: Conversão bem-sucedida

## 📈 Relatórios Disponíveis

- Total de contatos cadastrados
- Distribuição por estágio de vendas



## 🧬 Conceitos POO Aplicados

### 1. **Classes Abstratas**
```python
class Serializavel(ABC):
    @abstractmethod
    def to_dict(self):
        pass
```
**Aplicação**: Garante que todos os objetos implementem métodos de serialização

### 2. **Herança**
```python
class Contato(Pessoa):  # Herda de Pessoa
class Lead(Pessoa):     # Herda de Pessoa
```
**Aplicação**: Reutilização de código para atributos comuns (name, email, created_at)

### 3. **Encapsulamento**
```python
class Pessoa:
    def __init__(self, name, email):
        self._name = name      # Atributo privado
        
    @property
    def name(self):            # Getter
        return self._name
        
    @name.setter
    def name(self, value):     # Setter com validação
        if not value.strip():
            raise ValueError("Nome não pode estar vazio")
        self._name = value.strip()
```
**Aplicação**: Proteção e validação de dados críticos

### 4. **Polimorfismo**
```python
# Cada classe implementa to_dict() de forma específica
contato.to_dict()  # Retorna dados específicos do contato
lead.to_dict()     # Retorna dados específicos do lead
```
**Aplicação**: Interface uniforme para diferentes tipos de objetos

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
│   ├── task.py              # Tarefas e lembretes
│   ├── document.py          # Documentos
│   └── campanha.py          # Campanhas de email
├── main.py                  # Ponto de entrada
├── LICENSE                  # Licença MIT
├── README.md               # Este arquivo
└── crm_data.json           # Dados persistidos (auto-gerado)
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

