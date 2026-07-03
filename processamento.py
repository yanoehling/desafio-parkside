import requests
import pandas
import time


url_base = 'https://api.spotify.com'


def fazer_requisicao_get(uri, headers):
    while True:
        res = requests.get(uri, headers=headers)
        
        if res.status_code == 429:
            tempo_espera = int(res.headers.get('Retry-After', 5))
            print(f"Limite de requisições (429) atingido. Aguardando {tempo_espera} segundos antes de tentar de novo...")
            time.sleep(tempo_espera)
            continue
        if res.status_code != 200:
            print(f"Erro na requisição: {uri}")
            print(f"Status: {res.status_code}")
            try:
                print(f"Mensagem da API: {res.json()}")
            except:
                print(f"Mensagem da API: {res.text}") # Se não for JSON, printa o texto puro para não quebrar
            return None
            
        print(f"Sucesso (200): {uri}")
        time.sleep(0.4) # BLINDAGEM MÁXIMA: Espera 0.4s entre todas as requisições, não importa o que aconteça
        return res.json()


def procurar_artista(nome_artista, token):
    uri = url_base + f'/v1/search?q={nome_artista}&type=artist'
    headers = { 'Authorization': f'Bearer {token}' }
    return fazer_requisicao_get(uri, headers)


def proc_dados_artista(json_artista, arquivo_saida):
    tabela_artista = pandas.DataFrame({
        'id': [json_artista['id']],
        'nome': [json_artista['name']],
        'link_spotify': [json_artista['external_urls']['spotify']]
    })
    tabela_artista.to_csv(arquivo_saida, index=False, sep=';', encoding='utf-8-sig')
    return json_artista['id']


def proc_dados_lancamentos(id_artista, token, arquivo_saida):
    # BLINDAGEM 2: Filtrar apenas álbuns e singles do próprio artista (ignorar compilações e centenas de participações pequenas que inflam o rate limit)
    uri = url_base + f'/v1/artists/{id_artista}/albums' + '?include_groups=album,single' + '&limit=50'
    ids, nomes, datas, tipos, totais_de_faixas = [], [], [], [], []
    while uri:
        headers = { 'Authorization': f'Bearer {token}' }
        res_json = fazer_requisicao_get(uri, headers)
        if res_json == None:
            break

        for lancamento in res_json['items']:
            ids.append(lancamento['id'])
            nomes.append(lancamento['name'])
            datas.append(lancamento['release_date'])
            tipos.append(lancamento['album_type'])
            totais_de_faixas.append(lancamento['total_tracks'])

        uri = res_json.get('next')

    tabela_lancamentos = pandas.DataFrame({
        'id': ids,
        'nome': nomes,
        'data': datas,
        'tipo': tipos,
        'total_faixas': totais_de_faixas
    })
    tabela_lancamentos.to_csv(arquivo_saida, index=False, sep=';', encoding='utf-8-sig')
    return ids


def proc_todas_musicas(ids_lancamentos, id_artista_princ, token, arquivo_musicas, arquivo_relacao, arquivo_artista):
    ids_lanc_musicas, ids_musicas, nomes, duracoes = [], [], [], []
    cruzam_id_musica, cruzam_id_artista, cruzam_tipo = [], [], []
    novos_artistas_id, novos_artistas_nome, novos_artistas_link = [], [], []

    # Fatiar a lista de álbuns em lotes de 20 (limite da API do Spotify)
    for i in range(0, len(ids_lancamentos), 20):
        lote_ids = ids_lancamentos[i:i + 20]
        ids_juntos = ",".join(lote_ids)
        uri = url_base + f'/v1/albums?ids={ids_juntos}'

        headers = { 'Authorization': f'Bearer {token}' }
        res_json = fazer_requisicao_get(uri, headers)
        if res_json == None or 'albums' not in res_json:
            continue

        for album in res_json['albums']:
            if not album: # Prevenção caso a API retorne nulo para algum ID
                continue
            
            id_lanc = album['id']
            # O endpoint /v1/albums já traz as faixas em album['tracks']['items']
            for musica in album['tracks']['items']:
                ids_lanc_musicas.append(id_lanc)
                ids_musicas.append(musica['id'])
                nomes.append(musica['name'])

                duracao_s = round(musica['duration_ms'] / 1000)
                duracoes.append(duracao_s)

                for artista in musica['artists']:
                    cruzam_id_musica.append(musica['id'])
                    cruzam_id_artista.append(artista['id'])
                    if artista['id'] == id_artista_princ:
                        cruzam_tipo.append("Principal")
                    else:
                        cruzam_tipo.append("Colaborador")
                        if artista['id'] not in novos_artistas_id:
                            novos_artistas_id.append(artista['id'])
                            novos_artistas_nome.append(artista['name'])
                            novos_artistas_link.append(artista['external_urls']['spotify'])

    tabela_musicas = pandas.DataFrame({
        'id_lancamento': ids_lanc_musicas,
        'id': ids_musicas,
        'nome': nomes,
        'duracao_s': duracoes,
    })
    tabela_cruzam = pandas.DataFrame({
        'id_musica': cruzam_id_musica,
        'id_artista': cruzam_id_artista,
        'tipo': cruzam_tipo
    })
    tabela_musicas.to_csv(arquivo_musicas, index=False, sep=';', encoding='utf-8-sig')
    tabela_cruzam.to_csv(arquivo_relacao, index=False, sep=';', encoding='utf-8-sig')

    if len(novos_artistas_id) > 0:
        tabela_novos_artistas = pandas.DataFrame({
            'id': novos_artistas_id,
            'nome': novos_artistas_nome,
            'link_spotify': novos_artistas_link
        })
        tabela_novos_artistas.to_csv(arquivo_artista, mode='a', header=False, index=False, sep=';', encoding='utf-8-sig')
    
    return ids_musicas

