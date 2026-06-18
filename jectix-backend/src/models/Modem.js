// ==============================================================================
// PROJETO: NetCheck ACS - Módulo de Automação Proativa
// EMPRESA: Jectix Telecomunicações
// ARQUIVO: src/models/Modem.js
// DESCRIÇÃO: Modelo (Schema) de dados para o armazenamento do histórico de sinal e mapeamento das CPEs no MongoDB.
// EQUIPE: Matheus Flores / Sr. Jefferson
// ==============================================================================

const mongoose = require('mongoose');

const ModemSchema = new mongoose.Schema({
    idDispositivo: { type: String, required: true, unique: true }, // ID do ACS
    fabricante: { type: String, required: true },                  // ZTE, TP-Link, Furukawa
    modelo: { type: String, required: true },                      // F670L, XC220, etc.
    status: { type: String, default: 'online' },
    wifi: {
        sinal2g: { type: String, default: 'N/A' },
        sinal5g: { type: String, default: 'N/A' },
        canal2g: { type: Number, default: 0 },
        canal5g: { type: Number, default: 0 }
    },
    ultimaColeta: { type: Date, default: Date.now }
});

// Toda vez que salvarmos, ele atualiza a data automaticamente
ModemSchema.pre('save', function(next) {
    this.ultimaColeta = Date.now();
    next();
});

module.exports = mongoose.model('Modem', ModemSchema);