# ==============================================================================
# PROJETO: NetCheck ACS - Módulo de Automação Proativa
# EMPRESA: Jectix Telecomunicações
# ARQUIVO: teste_acs.py
# DESCRIÇÃO: Script de teste inicial (Prova de Conceito) para validar se a
#            nossa máquina local consegue conversar com o GenieACS na nuvem.
# EQUIPE: Matheus Flores / Sr. Jefferson
# ==============================================================================

import requests  # Biblioteca para fazer requisições HTTP (coletar dados da web)

# --- CONFIGURAÇÕES DE ACESSO DO SERVIDOR JECTIX ---

# URL da API Northbound Interface (NBI) do GenieACS.
# A porta padrão para consultar dispositivos (modems) é a 7557.
# O endpoint '/devices' nos devolve a lista de todas as CPEs registradas.
URL_GENIEACS_API = "http://acs.jectix.net.br:7557/devices"

# Tempo limite de segurança (em segundos) que o Python vai esperar o servidor responder.
# Se o firewall da VPS estiver bloqueando o nosso IP, o script não fica travado para sempre;
TEMPO_LIMITE_CONEXAO = 10

# ==============================================================================
# PARTE 4: BLOCO DE TENTATIVA DE CONEXÃO (EXECUÇÃO REAL)
# ==============================================================================
# Mensagens iniciais no terminal para o técnico saber que o script começou a rodar
print("\n📡 [NetCheck] Iniciando comunicação com o servidor da Jectix...")
print(f"🔗 Conectando ao alvo: {URL_GENIEACS_API}")

try:
    # O comando 'requests.get' faz o disparo HTTP real para a NBI API do GenieACS.
    # Passamos a nossa URL imutável e o nosso tempo limite de segurança.
    resposta = requests.get(URL_GENIEACS_API, timeout=TEMPO_LIMITE_CONEXAO)
    
    # HTTP Status 200: O servidor da Jectix recebeu a requisição e deu sinal verde.
    if resposta.status_code == 200:
        # O GenieACS devolve uma lista de dados brutos (JSON). 
        # O comando '.json()' transforma esse texto bruto em uma lista legível para o Python.
        lista_de_modems = resposta.json()
        
        print("\n==================================================")
        print("✅ CONEXÃO COM O GENIEACS REALIZADA COM SUCESSO!")
        print(f"📊 Total de modems (CPEs) localizados na rede: {len(lista_de_modems)}")
        print("==================================================\n")
        
        # --- EXIBIÇÃO FORMATADA DOS DADOS ---
        # Usamos o 'enumerate' para criar um contador automático (1, 2, 3...) para cada modem da lista
        for indice, modem in enumerate(lista_de_modems, start=1):
            # O GenieACS identifica unicamente cada roteador através da chave '_id'
            id_dispositivo = modem.get("_id", "Não identificado")
            print(f"🔹 [{indice}] Equipamento -> ID no ACS: {id_dispositivo}")
            
        # ==============================================================================
        # 🚀 NOVA PARTE AUTOMATIZADA: ALIMENTAÇÃO DO ARQUIVO DE BANCADA
        # ==============================================================================
        print("\n📝 [NetCheck] Atualizando a lista de bancada 'modems.txt'...")
        
        # Abre o arquivo limpando o conteúdo antigo ('w') para colocar a lista fresca
        with open("modems.txt", "w", encoding="utf-8") as arquivo_txt:
            for modem in lista_de_modems:
                id_dispositivo = modem.get("_id", "")
                
                # Regra de identificação por modelo com base no ID retornado
                if "F670L" in id_dispositivo:
                    modelo = "ZTE_F670L"
                elif "XC220" in id_dispositivo:
                    modelo = "TPLink_XC220"
                else:
                    # Pula o DISCOVERYSERVICE e qualquer outro que não seja foco de homologação
                    continue
                
                # Escreve a linha perfeitamente formatada para o mapeador ler depois
                arquivo_txt.write(f"{id_dispositivo},{modelo}\n")
                
        print("💾 [NetCheck] Sucesso! O arquivo 'modems.txt' foi atualizado dinamicamente.")
        # ==============================================================================
            
    # Caso o servidor responda, mas com uma mensagem de erro (ex: Porta errada ou sem permissão)
    else:
        print(f"\n⚠️ O servidor foi alcançado, mas recusou o pedido. Status retornado: {resposta.status_code}")
        print(" Observação para a equipe: Verifique se as permissões da API NBI mudaram na VM.")
        
        # --- FECHAMENTO DA REDE DE PROTEÇÃO (TRATAMENTO DE ERROS) ---

# Caso 1: O servidor demorou mais de 10 segundos para responder (Bloqueio de Firewall)
except requests.exceptions.Timeout:
    print("\n==================================================")
    print("ERRO CRÍTICO: Tempo limite de conexão esgotado (Timeout).")
    print("==================================================")
    print("DIAGNÓSTICO PARA A EQUIPE (Matheus / Jefferson):")
    print("   O script tentou acessar a porta 7557, mas não obteve nenhuma resposta.")
    print("   Isso comprova que a porta 7557 da VPS está bloqueada por Firewall para redes externas.")
    print("   AÇÃO NECESSÁRIA: Solicitar ao Sr. Jefferson a liberação do seu IP público atual")
    print("   nas regras do UFW/Iptables da VM ou conectar-se à VPN da Jectix.\n")

# Caso 2: O domínio está errado ou o servidor está completamente desligado
except requests.exceptions.ConnectionError:
    print("\n ERRO: Não foi possível alcançar o servidor da Jectix.")
    print(" DIAGNÓSTICO PARA A EQUIPE:")
    print("   O domínio 'acs.jectix.net.br' não pôde ser resolvido ou o servidor está offline.")
    print("   Ação: Verificar se a VM do GenieACS está ligada e com o serviço ativo.\n")

# Caso 3: Qualquer outro erro desconhecido (falta de internet local, etc.)
except Exception as erro_inesperado:
    print(f"\n Ocorreu um erro inesperado no script: {erro_inesperado}\n")