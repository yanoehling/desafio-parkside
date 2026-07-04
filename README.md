## Desafio Parkside - Pipeline de Dados com a API do Spotify

### - API Utilizada

Foi usada API Web do Spotify (https://developer.spotify.com/documentation/web-api).

### - O que o script faz

Dado um artista escolhido pelo próprio usuário, o script:

1. Autentica com a API do Spotify, buscando o token necessário em uma micro API própria.
2. Pesquisa pelo nome do artista e deixa o usuário confirmar qual é o correto (para casos onde o nome é ambíguo).
3. Coleta a discografia completa - todos os lançamentos de álbuns, eps e singles, com paginação se o artista tiver muitos lançamentos.
4. Coleta todas as músicas de cada lançamento, também com paginação.
5. Transforma os dados em cada etapa de busca:
    - Filtra apenas os dados desejados 
    - Identifica colaborações: se uma música tem mais de um artista, todos são registrados com seus papéis na música (artista principal ou colaborador) em uma tabela de relacionamento.
6. Gera arquivos CSV relacionais (tabelas que podem se conectar por chaves estrangeiras), prontas para serem consumidas por outras aplicações.
7. Gera um arquivo JSON com as métricas calculadas a partir das tabelas em CSV: total de lançamentos (de cada tipo), médias de duração, contagem de collabs, datas do primeiro e último lançamento, link e nome do artista. Estas métricas simulam o que um Dashboard mostraria no Power BI.



## Como rodar
### - Pré-requisitos:

- Python 3.10+
- As seguintes bibliotecas instaladas (rodar o seguinte comando):

```
pip install requests pandas python-dotenv
```

O script usa uma micro API própria (https://yanmano.pythonanywhere.com/) para não expor as chaves pessoais da minha conta do Spotify no código. 

### - Rodando

```bash
python main.py
```

O script vai pedir o nome do artista no terminal, mostrar uma lista de resultados e aguardar a confirmação de qual é o correto. A partir daí, tudo roda automaticamente.



### - Onde ficam os arquivos gerados

Depois da execução, os arquivos são gerados em:

- 'csvs_tabelas/artista.csv' - id, nome e link do Spotify do artista principal e de seus artistas colaboradores.
- 'csvs_tabelas/lancamento.csv' - todos os álbuns e singles com id, nome, data, tipo e total de faixas.
- 'csvs_tabelas/musica.csv' - todas as músicas com id, nome, duração em segundos e id do lançamento no qual essa música foi lançada.
- 'csvs_tabelas/musica_artista.csv' - tabela de relacionamento músicas × artistas, com o papel do artista naquela música (Principal ou Colaborador).
- 'saida_json_final/dashboard.json' - métricas prontas para visualização e possível exportação.

Sempre que o script for executado, os arquivos gerados anteriormente são apagados e reescritos.



## Principais decisões

### - API do Spotify
A escolha principal foi por conta de familiaridade: já conhecia parte da estrutura dos dados e várias métricas disponíveis, o que diminuiu o tempo de reconhecimento das funções da API na prática, e dos sentidos dos seus endpoints, me facilitando a focar na lógica dos tratamentos. Além disso, é uma API que permite o cruzamento de informações de formas que realmente geram valor (ao menos para mim - tenho curiosidade genuína pelos dados que estou buscando), o que facilitou o pensamento do que faria sentido de analisar e entregar para um usuário final.

### - Tabelas relacionais e JSON que simula um Dashboard
A escolha de tabelas relacionais não foi só por conta da organização e da padronização: ao separar artistas, lançamentos, músicas, colaborações em tabelas diferentes com chaves estrangeiras, estas podem ser consumidas por ferramentas de análise de dados como o Power BI, onde o consumo de dados organizados e já preparados facilita muito o cruzamento de dados de forma eficiente e até automatizada. Assim, os dados brutos foram transformados em arquivos de saída que podem ser consumidos diretamente. Fazendo uma analogia com dados se uma equipe ou setor da empresa, as métricas de um artista no JSON final - como o total de lançamentos, médias de duração, colaborações, datas - são exatamente os tipos de métricas que eu exibiria em um Dashboard no PowerBI.

### - Requisição e tratamento dos dados
Optei por não separar completamente a camada de requisição da camada de transformação por uma razão prática: a transformação é mais eficiente ao acontecer no loop de paginação. Separar os dois em módulos independentes exigiria guardar os dados brutos na memória até o fim da paginação para então depois processar - o que, para discografias grandes, seria um custo desnecessário. Mantendo-os juntos, cada página já têm seus dados tratados antes de ser requisitada a próxima.

### - Interação com o usuário via terminal
Seria uma prática ruim exigir que o usuário do sistema soubesse o ID interno do artista no Spotify - isso tornaria o uso impraticável para qualquer pessoa que não estivesse disposta a copiar e procurar informações nos links de compartilhamento de um artista. A busca por nome com confirmação resolve isto e o problema de haverem artistas com nomes parecidos.

### - Micro API própria para o token
Para se autenticar na API do Spotify é necessário um Client ID e um Client Secret, que ficam vinculados a uma conta do Spotify. Expor essas chaves no código seria um risco, pois qualquer pessoa com acesso ao repositório poderia usar ou comprometer as minhas credenciais. A solução foi fazer deploy em uma micro API própria (hospedada no PythonAnywhere - https://yanmano.pythonanywhere.com/), que guarda seguramente minhas chaves e devolve apenas o token de acesso aos clientes. Assim, o script pode ser compartilhado e rodado em qualquer máquina sem precisar de configurações extras - basta ter acesso à URL da micro API.

### - Modularização em arquivos separados
O código foi dividido em três arquivos com responsabilidades distintas, além do arquivo main: 'funcoes.py' cuida da autenticação (token de acesso) e de utilitários, 'processamento.py' contém toda a lógica de requisição e transformação dos dados, e 'gera_dashboard.py' lida com os cálculos finais e a geração do JSON de simulação de métricas de dashboard. Essa separação facilitou a leitura, o debug e a manutenção do código.

### - Tratamento de erros
O script foi pensado para não travar com mensagens de erro confusas. Há tratamento para: entrada inválida do usuário, busca sem resultados, falha de conexão com timeout, rate limit e trava automática se a espera for maior que 5 minutos (indicativo de limite de cota diária na API do spotify), e valores nulos/dataframes vazios nos cálculos do dashboard. A ideia é que o script sempre encerre de forma limpa e com uma mensagem que deixe claro o que aconteceu.
