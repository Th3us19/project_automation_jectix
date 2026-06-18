// ==============================================================================
// PROJETO: NetCheck ACS - Módulo de Automação Proativa
// EMPRESA: Jectix Telecomunicações
// ARQUIVO: src/services/genieAcsService.js
// DESCRIÇÃO: Serviço com varredura dinâmica TR-069 para extração de telemetria de Wi-Fi (sinal/canal) independente do modelo/fabricante.
// EQUIPE: Matheus Flores / Sr. Jefferson
// ==============================================================================

const axios = require('axios');
const Modem = require('../models/Modem');

const GENIEACS_URL = process.env.GENIEACS_URL || 'http://acs.jectix.net.br:7557';
const TIMEOUT = parseInt(process.env.GENIEACS_TIMEOUT) || 10000;

/**
 * Varre o objeto recursivamente procurando por configurações de Wi-Fi (WLANConfiguration)
 * para capturar canais e sinais dinamicamente.
 */
function extrairDadosWifiDinamico(objetoBruto) {
    let telemetria = { sinal2g: 'N/A', sinal5g: 'N/A', canal2g: 0, canal5g: 0 };
    
    // Converte o objeto para string para fazermos buscas rápidas de caminhos existentes
    const stringfied = JSON.stringify(objetoBruto);
    
    try {
        const landevice = objetoBruto?.InternetGatewayDevice?.LANDevice?.['1'];
        if (!landevice || !landevice.WLANConfiguration) return telemetria;

        // Varre todos os índices de WLANConfiguration (1, 2, 3, 4, 5...)
        Object.keys(landevice.WLANConfiguration).forEach(indice => {
            const wlan = landevice.WLANConfiguration[indice];
            if (!wlan) return;

            const canal = wlan.Channel?._value ? Number(wlan.Channel._value) : 0;
            
            // Tenta capturar a potência/sinal de dispositivos associados (ZTE ou TP-Link)
            let sinalDetectado = null;
            if (wlan.AssociatedDevice?.['1']?.SignalStrength?._value !== undefined) {
                sinalDetectado = wlan.AssociatedDevice['1'].SignalStrength._value;
            } else if (wlan['X_ZTE-COM_AssociatedDevice']?.['1']?.SignalStrength?._value !== undefined) {
                sinalDetectado = wlan['X_ZTE-COM_AssociatedDevice']['1'].SignalStrength._value;
            }

            // Diferenciação por Canal/Frequência (Canais altos = 5G, Canais baixos = 2G)
            if (canal > 14) {
                if (canal && !telemetria.canal5g) telemetria.canal5g = canal;
                if (sinalDetectado) telemetria.sinal5g = `${sinalDetectado} dBm`;
            } else if (canal > 0 && canal <= 14) {
                if (canal && !telemetria.canal2g) telemetria.canal2g = canal;
                if (sinalDetectado) telemetria.sinal2g = `${sinalDetectado} dBm`;
            }
        });

    } catch (e) {
        console.log(`   ⚠️ Erro na varredura dinâmica de Wi-Fi: ${e.message}`);
    }

    return telemetria;
}

/**
 * Filtra, classifica e persiste os dados reais no banco
 */
async function processarESalvarModem(dadosBrutos) {
    const idDispositivo = dadosBrutos._id || "Não identificado";
    const idUpper = idDispositivo.toUpperCase();
    
    let fabricante = 'DESCONHECIDO';
    let modelo = 'UNMAPPED';

    // 1. Classificação por Fabricante/Modelo
    if (idUpper.includes('F670L')) {
        fabricante = 'ZTE';
        modelo = 'F670L';
    } else if (idUpper.includes('XC220')) {
        fabricante = 'TP-Link';
        modelo = 'XC220';
    } else if (idUpper.includes('XX530V')) {
        fabricante = 'TP-Link';
        modelo = 'XX530v';
    } else if (idUpper.includes('DEVICE2')) {
        fabricante = 'Furukawa';
        modelo = 'Device2';
    }

    // 2. Extração inteligente e dinâmica do Wi-Fi
    const wifiReal = extrairDadosWifiDinamico(dadosBrutos);

    try {
        // 3. Atualiza o MongoDB com os dados garimpados
        await Modem.findOneAndUpdate(
            { idDispositivo: idDispositivo },
            { 
                idDispositivo,
                fabricante,
                modelo,
                status: 'online',
                wifi: wifiReal
            },
            { upsert: true, returnDocument: 'after' }
        );

        console.log(`   💾 [BANCO DE DADOS]: ${fabricante} (${modelo}) sincronizado com sucesso!`);
    } catch (erro) {
        console.log(`   ❌ [ERRO BANCO]: Falha ao salvar o modem ${idDispositivo}. Motivo: ${erro.message}`);
    }
}

/**
 * Consulta a API do GenieACS
 */
async function testarConexaoAcs() {
    console.log("\n📡 [NetCheck Backend] Iniciando comunicação com o servidor da Jectix...");
    const endpoint = `${GENIEACS_URL}/devices?projection=InternetGatewayDevice.LANDevice.1.WLANConfiguration`;

    try {
        const resposta = await axios.get(endpoint, { timeout: TIMEOUT });

        if (resposta.status === 200) {
            const listaDeModems = resposta.data;

            console.log("\n==================================================");
            console.log("✅ CONEXÃO COM O GENIEACS REALIZADA COM SUCESSO!");
            console.log(`📊 Mapeando e tratando telemetria de ${listaDeModems.length} CPEs...`);
            console.log("==================================================\n");

            for (let i = 0; i < listaDeModems.length; i++) {
                console.log(`🔹 [${i + 1}] Escaneando: ${listaDeModems[i]._id}`);
                await processarESalvarModem(listaDeModems[i]);
                console.log("--------------------------------------------------");
            }

            return listaDeModems;
        }

    } catch (erro) {
        console.log("\n==================================================");
        console.log("❌ ERRO CRÍTICO NA COMUNICAÇÃO COM O GENIEACS");
        console.log("==================================================");
        console.log(`DIAGNÓSTICO: ${erro.message}\n`);
    }
}

module.exports = {
    testarConexaoAcs
};