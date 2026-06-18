# NetCheck ACS - Módulo de Automação Proativa 📡

O **NetCheck ACS** é um ecossistema desenvolvido para a **Jectix Telecomunicações** focado na extração automatizada, tratamento e persistência de telemetria de Wi-Fi e inventário de CPEs (modems) integrados via servidores TR-069/TR-181 (GenieACS).

O repositório é dividido entre o motor principal de sincronização em tempo real (Node.js) e os scripts de análise e validação inicial de dados (Python).

---

## 📂 Estrutura do Repositório

- **`jectix-backend/`**: Servidor principal em Node.js que gerencia a API, conexão com o banco de dados e rotinas de varredura automáticas.
- **`Bancada_de_Teste/`**: Scripts e automações em Python utilizados para testes locais, engenharia reversa das árvores de parâmetros do GenieACS e análise preliminar da telemetria.

---

## 🚀 Funcionalidades (Módulo Node.js)

- **Sincronização Periódica Autônoma:** Integration contínua (via `setInterval`) que consulta a API do GenieACS automaticamente a cada 5 minutos, eliminando a necessidade de reinicializações manuais.
- **Mapeamento de Hardware Inteligente:** Classificação automatizada de fabricantes (ex: ZTE, TP-Link) através da validação dinâmica de strings de firmware e prefixos de MAC Address (OUI), como o tratamento do prefixo `8C902D` para modelos XC220.
- **Varredura Dinâmica Multi-Padrão:** Algoritmo preparado para processar tanto árvores de parâmetros TR-069 (`InternetGatewayDevice.`) quanto TR-181 (`Device.`).
- **Persistência Inteligente:** Armazenamento estruturado no MongoDB utilizando operações de `upsert` para evitar duplicidade de registros e manter o histórico atualizado.

---

## 🛠️ Tecnologias Utilizadas

### Backend (Node.js)
- **Runtime:** Node.js & Express
- **Banco de Dados:** MongoDB & Mongoose
- **Comunicação HTTP:** Axios & GenieACS API
- **Monitoramento:** Nodemon & Dotenv

### Bancada (Python)
- **Runtime:** Python 3.x
- **Ambiente:** Isolação via Virtual Environment (`.venv`)

---

## 📥 Pré-requisitos (O que você precisa instalar antes)

Se esta for a primeira vez rodando o projeto na máquina, faça o download e a instalação dos programas abaixo:

1. **Node.js (Versão LTS):** Baixe e instale do site oficial. Ele é necessário para rodar o backend.
2. **Python 3.x:** Baixe da Microsoft Store ou site oficial. **Importante:** Marque a caixa "Add Python to PATH" durante a instalação.
3. **MongoDB Community Server:** Baixe e instale o banco de dados para rodar localmente na porta padrão `27017`.
4. **MongoDB Compass:** A interface visual para você visualizar as tabelas e dados salvos do banco.

---

## 🏃‍♂️ Como Ligar o Projeto (Passo a Passo)

Para rodar o sistema completo no seu computador, você vai precisar abrir **duas janelas de terminal** separadas no VS Code.

### 🗄️ PASSO 1: O Banco de Dados (MongoDB)
Antes de ligar o código, o banco de dados precisa estar funcionando.
1. Abra o aplicativo **MongoDB Compass** no seu computador.
2. Clique no botão verde **Connect** (deixe a URL padrão `mongodb://localhost:27017`).
3. Deixe o Compass aberto de lado.

---

### 📡 PASSO 2: Ligar o Servidor (Node.js)
Agora vamos colocar o motor do backend para rodar.
1. Abra um terminal no VS Code.
2. Digite o comando abaixo para entrar na pasta do servidor, instalar as dependências e iniciar o projeto:
   ```bash
   cd jectix-backend

   # Comando para instalar os pacotes e dependências do Node.js
   npm install

   # Comando para rodar o servidor em modo de desenvolvimento
   npm run dev
