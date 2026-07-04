from funcoes import *
from processamento import *  
from gera_dashboard import *


dir = 'csvs_tabelas'
tab_artista = dir + '/artista.csv'
tab_lancamento = dir + '/lancamento.csv'
tab_musica = dir + '/musica.csv'
tab_musica_artista = dir + '/musica_artista.csv'
todas_tabelas = [tab_artista, tab_lancamento, tab_musica, tab_musica_artista]
saida_json_final = 'saida_json_final/dashboard.json'


def main():
    limpar_tabelas(todas_tabelas, saida_json_final)

    token_json = pegar_token_api_propria()
    if not token_json or "access_token" not in token_json:
        print("\nNão foi possível obter token. Verificar conexão com a micro API.")
        return
    token = token_json["access_token"]

    nome_artista = input("\nDigite o nome do artista desejado para buscá-lo: ")
    artistas_similares = procurar_artista(nome_artista, token)
    if not artistas_similares:
        print("\nErro ao buscar artista na API. Verifique a sua conexão.")
        return
    itens_artistas = artistas_similares.get('artists', {}).get('items', [])
    if not itens_artistas:
        print("\nNenhum artista encontrado com esse nome, ou erro na API. Encerrando.")
        return

    print("\nResultado da busca:")
    for i in range(0, len(itens_artistas)):
        print(f"{i+1} - {itens_artistas[i]['name']}")
    print("0 - Encerrar programa")

    while True:
        try:
            n = int(input("\nSelecione o número do artista correto: "))
            if n == 0:
                print("\nOperação cancelada.")
                return
            if n < 1:
                raise IndexError
            artista_correto = itens_artistas[n-1]
            break
        except (ValueError, IndexError):
            print("Numero inválido. Digite novamente")

    nome_correto = artista_correto['name']

    print(f"\nProcessando dados de '{nome_correto}'...")
    id_artista_principal = trat_dados_artista(artista_correto, tab_artista)

    print(f"\nProcessando lançamentos de '{nome_correto}'...\n")
    ids_lancamentos = proc_dados_lancamentos(id_artista_principal, token, tab_lancamento)

    print(f"\nProcessando músicas de cada lançamento de '{nome_correto}'...\n")
    tabela_musicas = proc_todas_musicas(ids_lancamentos, id_artista_principal, token, tab_musica, tab_musica_artista, tab_artista)  

    gerar_pseudo_dashboard(todas_tabelas, saida_json_final)


main()
