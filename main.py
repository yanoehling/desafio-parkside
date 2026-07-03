from funcoes import *
from processamento import *  
from dashboard import *


def main():
    dir = 'tabelas'
    tab_artista = dir + '/artista.csv'
    tab_lancamento = dir + '/lancamento.csv'
    tab_musica = dir + '/musica.csv'
    tab_musica_artista = dir + '/musica_artista.csv'
    todas_tabelas = [tab_artista, tab_lancamento, tab_musica, tab_musica_artista]
    
    limpar_tabelas(todas_tabelas)

    token_json = pegar_token_json()
    token = token_json["access_token"]

    nome_artista = input("Digite o nome do artista desejado para buscá-lo: ")
    artistas_similares = procurar_artista(nome_artista, token)
    itens_artistas = artistas_similares['artists']['items']

    print("\nResultado da busca:")
    for i in range(0, len(itens_artistas)):
        print(f"{i+1} - {itens_artistas[i]['name']}")
    n = int(input("\nSelecione o número do artista correto: "))

    artista_correto = itens_artistas[n-1]
    nome_correto = artista_correto['name']

    print(f"\nProcessando dados de {nome_correto}...\n")
    id_artista_principal = proc_dados_artista(artista_correto, tab_artista)

    print(f"\n\nProcessando lançamentos de {nome_correto}...\n")
    ids_lancamentos = proc_dados_lancamentos(id_artista_principal, token, tab_lancamento)

    print(f"\n\nProcessando músicas de {nome_correto}...\n")
    tabela_musicas = proc_todas_musicas(ids_lancamentos, id_artista_principal, token, tab_musica, tab_musica_artista, tab_artista)  

    gerar_pseudo_dashboard(todas_tabelas)

main()
