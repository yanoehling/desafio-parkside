import os
from dotenv import load_dotenv
import requests
import base64
import time

load_dotenv()
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']


def codificar(c_id, c_secret):
    string_original = c_id + ':' + c_secret
    string_em_bytes = string_original.encode('ascii')
    bytes_base64 = base64.b64encode(string_em_bytes)
    base64_em_ascii = bytes_base64.decode('ascii')
    return base64_em_ascii
    

def pegar_token_json():
    uri = 'https://accounts.spotify.com/api/token'
    
    dados_criptografados = codificar(CLIENT_ID, CLIENT_SECRET)
    headers = { 'Authorization': f'Basic {dados_criptografados}',
                'Content-Type': 'application/x-www-form-urlencoded' }
    data = { 'grant_type': f'client_credentials' }
    
    res = requests.post(uri, headers=headers, data=data)

    if res.status_code == 429:
        tempo_espera = int(res.headers.get('Retry-After', 5))
        print(f"Limite de requisições (429) atingido. Aguarde {tempo_espera} segundos antes de tentar de novo...")
    if res.status_code != 200:
        print(f"Erro na requisição: {uri}")
        print(f"Status: {res.status_code}")
        try:
            print(f"Mensagem da API: {res.json()}")
        except:
            print(f"Mensagem da API: {res.text}") # Se não for JSON, printa o texto puro para não quebrar
        return None

    print(f"Sucesso (200): {uri}")
    return res.json()


def limpar_tabelas(tabelas):
    for tabela in tabelas:
        if os.path.exists(tabela):
            os.remove(tabela)
