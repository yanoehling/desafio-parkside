import pandas
import json


def gerar_pseudo_dashboard(todas_tabelas):
    tabela_artista, tabela_lancamento, tabela_musica, tabela_relacao = todas_tabelas
    
    df_artista = pandas.read_csv(tabela_artista, sep=';', encoding='utf-8-sig')
    df_lancamentos = pandas.read_csv(tabela_lancamento, sep=';', encoding='utf-8-sig')
    df_musicas = pandas.read_csv(tabela_musica, sep=';', encoding='utf-8-sig')
    df_relacao = pandas.read_csv(tabela_relacao, sep=';', encoding='utf-8-sig')
    
    qtd_artistas_collabs = len(df_artista) - 1 
    musicas_collab = df_relacao[df_relacao['tipo'] == 'Colaborador']['id_musica'].nunique()
    
    qtd_lancamentos = len(df_lancamentos)
    qtd_albuns = len(df_lancamentos[df_lancamentos['tipo'] == 'album'])
    qtd_singles = len(df_lancamentos[df_lancamentos['tipo'].isin(['single', 'ep'])])
    
    media_faixas = df_lancamentos['total_faixas'].mean()
    media_duracao_musica = df_musicas['duracao_s'].mean()
    qtd_musicas = len(df_musicas)
    duracao_por_album = df_musicas.groupby('id_lancamento')['duracao_s'].sum().mean()
    
    nome_principal = df_artista.iloc[0]['nome']
    
    dashboard_dict = {
        "artista": nome_principal,
        "lancamentos": {
            "total": int(qtd_lancamentos),
            "albuns": int(qtd_albuns),
            "singles_eps": int(qtd_singles),
            "media_faixas": round(float(media_faixas), 1),
            "media_duracao_s": round(float(duracao_por_album), 1)
        },
        "musicas": {
            "total": int(qtd_musicas),
            "com_colaboracao": int(musicas_collab),
            "media_duracao_s": round(float(media_duracao_musica), 1)
        },
        "colaboradores_unicos": int(qtd_artistas_collabs)
    }
    
    with open('dashboard.json', 'w', encoding='utf-8') as f:
        json.dump(dashboard_dict, f, ensure_ascii=False, indent=4)
        
    print("\nConcluído com sucesso!\n")
