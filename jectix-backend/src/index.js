// ==========================================================================
// PROJETO: NetCheck ACS - Módulo de Automação Proativa
// EMPRESA: Jectix Telecomunicações
// ARQUIVO: src/index.js
// DESCRIÇÃO: Ponto de entrada (Entry Point) do servidor backend do NetCheck.
// Inicializa as variáveis de ambiente, levanta o servidor Express, conecta ao MongoDB e       
// gerencia a sincronização periódica com o GenieACS.
// EQUIPE: Matheus Flores / Sr. Jefferson
// ==========================================================================

require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose'); // Importa o Mongoose
const { testarConexaoAcs } = require('./services/genieAcsService');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(express.json());

app.get('/', (req, res) => {
    res.json({
        status: "online",
        projeto: "NetCheck API - Jectix",
        versao: "1.0.0",
        database: mongoose.connection.readyState === 1 ? "conectado" : "desconectado",
        timestamp: new Date()
    });
});

async function inicializarSistema() {
    console.log("==================================================");
    console.log(`🚀 [NetCheck] Inicializando Backend...`);
    console.log("==================================================");

    // 1. Conexão com o Banco de Dados (MongoDB)
    const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/netcheck';
    
    try {
        console.log("🗄️ Conectando ao Banco de Dados...");
        await mongoose.connect(MONGO_URI);
        console.log("✅ BANCO DE DADOS CONECTADO COM SUCESSO!");
        console.log("==================================================");
    } catch (erro) {
        console.log("⚠️ Alerta: Banco de dados local não detectado. Rodando em modo memória.");
        console.log("--------------------------------------------------");
    }

    // 2. Liga o servidor HTTP
    app.listen(PORT, () => {
        console.log(`📡 Servidor HTTP rodando na porta: ${PORT}`);
        console.log(`🔗 Link local: http://localhost:${PORT}`);
        console.log("==================================================");
    });

    // 3. Roda a primeira carga do GenieACS assim que o sistema inicia
    await testarConexaoAcs();

    // 4. AUTOMATIZAÇÃO: Roda a busca no GenieACS a cada 5 minutos sozinho
    // 5 minutos = 5 * 60 * 1000 = 300.000 milissegundos
    setInterval(async () => {
        console.log("\n🔄 [NetCheck] Executando rotina automática de varredura no GenieACS...");
        await testarConexaoAcs();
    }, 300000);
}

inicializarSistema();