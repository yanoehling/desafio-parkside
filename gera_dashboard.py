import pandas
import json


def gerar_pseudo_dashboard(todas_tabelas, saida_json_final):
    tabela_artista, tabela_lancamento, tabela_musica, tabela_relacao = todas_tabelas
    # lê tabelas
    tabela_artista = pandas.read_csv(tabela_artista, sep=';', encoding='utf-8-sig')
    tabela_lancamentos = pandas.read_csv(tabela_lancamento, sep=';', encoding='utf-8-sig')
    tabela_musicas = pandas.read_csv(tabela_musica, sep=';', encoding='utf-8-sig')
    tabela_relacao = pandas.read_csv(tabela_relacao, sep=';', encoding='utf-8-sig')
    
    qtd_artistas_collabs = len(tabela_artista) - 1
    musicas_collab = tabela_relacao[tabela_relacao['tipo'] == 'Colaborador']['id_musica'].nunique()
    
    qtd_lancamentos = len(tabela_lancamentos)

    ids_albuns = tabela_lancamentos[tabela_lancamentos['tipo'] == 'album']['id']
    qtd_albuns = len(ids_albuns)
    qtd_singles = len(tabela_lancamentos[tabela_lancamentos['tipo'].isin(['single', 'ep'])])
    qtd_musicas = len(tabela_musicas)
    
    media_faixas_calc = tabela_lancamentos['total_faixas'].mean()
    media_faixas = round(float(media_faixas_calc), 1) if not pandas.isna(media_faixas_calc) else 0.0
    
    media_duracao_musica = tabela_musicas['duracao_s'].mean()
    if pandas.isna(media_duracao_musica):
        media_duracao_musica = 0.0
    media_s_musica = round(float(media_duracao_musica), 1)
    media_m_musica = str(int(media_s_musica // 60)) +'m'+ str(int(media_s_musica % 60)) +'s'

    musicas_de_albuns = tabela_musicas[tabela_musicas['id_lancamento'].isin(ids_albuns)]
    media_segundos_album = int(musicas_de_albuns.groupby('id_lancamento')['duracao_s'].sum().mean())

    if pandas.isna(media_segundos_album):
        media_segundos_album = 0.0
    media_minutos_album = int(media_segundos_album // 60)
    horas_a = media_minutos_album // 60
    minutos_a = media_minutos_album % 60
    segundos_a = int(media_segundos_album % 60)
    media_duracao_album = f"{horas_a}h{minutos_a}m{segundos_a}s"

    primeiro_lancamento = str(tabela_lancamentos['data'].min()) if not tabela_lancamentos.empty else "N/A"
    ultimo_lancamento = str(tabela_lancamentos['data'].max()) if not tabela_lancamentos.empty else "N/A"

    nome_principal = tabela_artista.iloc[0]['nome'] if not tabela_artista.empty else "Desconhecido"
    
    dashboard_dict = {
        'artista': nome_principal,
        'lancamentos': {
            'total': qtd_lancamentos,
            'albuns': qtd_albuns,
            'singles_eps': qtd_singles,
            'media_faixas_album': media_faixas,
            'duracao_media_album_seg': media_segundos_album,
            'duracao_media_album': media_duracao_album,
            'data_primeiro_lancamento': primeiro_lancamento,
            'data_lancamento_mais_recente': ultimo_lancamento
        },
        'musicas': {
            'total': qtd_musicas,
            'com_colaboracao': musicas_collab,
            'duracao_media_seg': media_s_musica,
            'duracao_media': media_m_musica
        },
        'quant_artistas_colaboradores': qtd_artistas_collabs
    }
    
    with open(saida_json_final, 'w', encoding='utf-8') as f:
        json.dump(dashboard_dict, f, ensure_ascii=False, indent=4)
        
    print('\nConcluído com sucesso!\n')
