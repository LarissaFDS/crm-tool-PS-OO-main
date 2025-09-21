![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow.svg)

# Sistema de Gerenciamento de Relacionamento com o Cliente (CRM)

Sistema de CRM (Customer Relationship Management) desenvolvido em Python como projeto acadêmico da disciplina de Projeto de Software com Orientação a Objetos. 

## 🚀 Funcionalidades

### ⚠️ Implementação Parcial**
**Mobile Access**
**Funcionalidades Implementadas:**
- **Acesso via QR Code**: O sistema gera automaticamente um QR code para acesso móvel
- **Interface Web Responsiva**: O dashboard HTML é acessível via navegador móvel
- **API REST Completa**: Todos os endpoints podem ser consumidos por apps móveis

**Funcionalidades Não Implementadas:**
- **App Nativo**: Não há aplicativo iOS/Android dedicado
- **Push Notifications**: Notificações push não implementadas
- **Sincronização Offline**: Requer conexão com internet


## 🛠️ Instalação e Execução

### Pré-requisitos

- Python 3.8 ou superior instalado

### Como executar

1. **Clone o repositório**
   ```bash
   git clone https://github.com/LarissaFDS/crm-tool-PS-OO-main
   cd crm-tool-PS-OO-main
   pip install -r requirements.txt

3. **Execute o sistema**
   - Para rodar no terminal
      ```bash
      python main.py 
      ```
   - Para testar a implementação no celular
      É necessário ler o QR code.

4. **Navegue pelo menu**
   - O programa apresentará um menu interativo
   - Digite o número da opção desejada e pressione Enter
   - Os dados são salvos automaticamente em `crm_data.json`