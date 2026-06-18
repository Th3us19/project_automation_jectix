# ==============================================================================
# PROJETO: NetCheck ACS - Módulo de Automação Proativa
# EMPRESA: Jectix Telecomunicações
# ARQUIVO: mapear_modelos.py
# DESCRIÇÃO: Motor de homologação em lote. Lê uma lista de dispositivos,
#            consulta a API NBI do GenieACS e gera arquivos JSON individuais
#            com a árvore de parâmetros (Data Model TR-069) de cada CPE.
# EQUIPE: Matheus Flores / Sr. Jefferson
# ==============================================================================

import requests  # Biblioteca para realizar as requisições HTTP GET na API do GenieACS
import json      # Biblioteca para manipular dados e salvar os arquivos no formato JSON

# URL da API Northbound Interface (NBI) do GenieACS dedicada à consulta de dispositivos
URL_NBI = "http://acs.jectix.net.br:7557/devices"


def exportar_arvore_parametro(device_id, nome_modelo):
    """
    Consulta o GenieACS para extrair a árvore completa de parâmetros de um 
    dispositivo específico e grava as informações em um arquivo JSON exclusivo.
    
    :param device_id: ID único (Número de Série) do modem registrado no ACS.
    :param nome_modelo: Nome amigável do modelo (Ex: ZTE_F670L, TPLink_XC220).
    """
    print(f"📡 [NetCheck] Coletando dados para o modelo: {nome_modelo}...")
    
    # Define o filtro de busca no formato de objeto exigido pela API NBI do GenieACS
    query = {"_id": device_id}
    
    try:
        # Realiza o disparo HTTP GET. O parâmetro 'query' precisa ser convertido 
        # de dicionário Python para uma String JSON pura (json.dumps).
        resposta = requests.get(URL_NBI, params={"query": json.dumps(query)}, timeout=10)
        
        # HTTP Status 200: O servidor respondeu com sucesso
        if resposta.status_code == 200:
            dados_api = resposta.json()
            
            # Se a lista vier vazia, o ID configurado não existe na base do GenieACS
            if not dados_api:
                print(f"❌ [NetCheck] Dispositivo '{device_id}' não localizado na base do GenieACS.")
                return
                
            # Como a API do GenieACS sempre retorna uma lista [], capturamos o primeiro 
            # e único objeto válido da resposta usando o índice [0]
            dados_modem = dados_api[0]
            
            # ------------------------------------------------------------------
            # REGRA DE NOMENCLATURA EXCLUSIVA:
            # Isolamos os últimos 6 caracteres do ID para criar um sufixo curto.
            # Isso impede que roteadores do mesmo modelo sobrescrevam o arquivo um do outro.
            # Exemplo: '3C64CF-XC220%2DG3-224958...' vira o sufixo '224958'
            # ------------------------------------------------------------------
            sufixo_id = device_id.split("-")[-1][:6] if "-" in device_id else device_id[:6]
            nome_arquivo = f"mapeamento_{nome_modelo.lower()}_{sufixo_id}.json"
            
            # Abre (or cria) o arquivo em modo de escrita ('w') usando codificação UTF-8
            with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
                # json.dump grava o objeto no arquivo físico.
                # indent=4 formata o texto com recuos de 4 espaços para leitura humana.
                # ensure_ascii=False garante que caracteres especiais e acentos não quebrem.
                json.dump(dados_modem, arquivo, indent=4, ensure_ascii=False)
                
            print(f"💾 [NetCheck] Sucesso! Arquivo '{nome_arquivo}' gerado com a árvore do TR-069.")
            
        else:
            print(f"❌ [NetCheck] Erro na API do GenieACS. Código de Status: {resposta.status_code}")
            
    except requests.exceptions.RequestException as erro:
        # Captura falhas físicas de rede, timeouts ou quedas de conexão com a VPS
        print(f"❌ [NetCheck] Falha crítica de rede ou timeout ao conectar ao servidor: {erro}")
    except Exception as erro_geral:
        # Rede de proteção para capturar qualquer outro erro imprevisto
        print(f"❌ [NetCheck] Ocorreu um erro inesperado: {erro_geral}")


# ==============================================================================
# BLOCO DE EXECUÇÃO EM LOTE (PONTO DE ENTRADA DO SCRIPT)
# ==============================================================================
if __name__ == "__main__":
    import os

    # Arquivo local que serve de ponte entre o script de busca e o mapeador
    arquivo_lista = "modems.txt"

    # Verifica se o arquivo de texto existe na pasta antes de tentar abrir
    if not os.path.exists(arquivo_lista):
        print(f"❌ [NetCheck] Erro: O arquivo '{arquivo_lista}' não foi encontrado.")
    else:
        print(f"📂 [NetCheck] Lendo lista de equipamentos em '{arquivo_lista}'...")
        
        # Abre o arquivo de texto em modo de leitura ('r')
        with open(arquivo_lista, "r", encoding="utf-8") as f:
            linhas = f.readlines()
            
            # Print de DEBUG para o técnico acompanhar o volume de dados lidos
            print(f"🔍 [DEBUG] O arquivo tem {len(linhas)} linhas detectadas.")
            print(f"🔍 [DEBUG] Conteúdo bruto Lido: {linhas}\n")
            
            # Percorre o arquivo linha por linha para processar os modems
            for linha in linhas:
                
                # .strip() limpa espaços inúteis e quebras de linha (\n) do início e fim do texto
                linha = Self_linha = linha.strip()
                
                # Regra de Segurança: Se a linha for vazia ou não tiver vírgula, pula para a próxima
                if not linha or "," not in linha:
                    continue
                
                # split(",", 1) divide a string na primeira vírgula.
                # O que está antes vira o ID da CPE; o que está depois vira o modelo.
                id_equipamento, nome_modelo = linha.split(",", 1)
                
                # Dispara o motor de mapeamento passando os parâmetros limpos e sem espaços
                exportar_arvore_parametro(id_equipamento.strip(), nome_modelo.strip())
                
        print("\n✅ [NetCheck] Processamento em lote concluído com sucesso!")