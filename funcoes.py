import os
import requests
import base64


def pegar_token_api_propria():
    uri = 'https://yanmano.pythonanywhere.com/'
    
    try:
        res = requests.get(uri, timeout=10)
        if res.status_code == 200:
            print("Sucesso (200): Conectado na micro API e Token recebido.")
            return res.json()
        else:
            print("Erro na micro API de token. Status:", res.status_code)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão com a micro API: {e}")
        return None


def limpar_tabelas(tabelas, saida_json_final):
    for tabela in tabelas:
        if os.path.exists(tabela):
            os.remove(tabela)
    if os.path.exists(saida_json_final):
        os.remove(saida_json_final)
