# =============================================================================
# Autor.........: Cristian Matias de Souza
# Cargo/Nível...: Analista de Dados (N3)
# Criado em.....: 19/08/2026 22:09
# Versão........: 1.0
# -----------------------------------------------------------------------------
# Descrição.....: Estudo dos métodos da biblioteca pathlib aplicados ao
#                 dataset Data/Pedidos.csv.
# Dependências..: Python 3.14
# =============================================================================

from pathlib import Path

import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)

# Path(__file__) -> caminho deste próprio arquivo .py
# .parent        -> sobe um nível e chega na pasta do projeto
# Com isso o script acha o CSV de qualquer diretório onde for executado.
BASE = Path(__file__).parent

# O operador / monta o caminho; o Python aplica o separador correto do sistema.
caminho_csv = BASE / 'Data' / 'Pedidos.csv'

# --- Inspecionando o arquivo antes de abrir ---------------------------------
print(caminho_csv.exists())    # método    -> True: confirma se o arquivo existe no disco
print(caminho_csv.name)        # atributo  -> 'Pedidos.csv': nome do arquivo com extensão
print(caminho_csv.stem)        # atributo  -> 'Pedidos': nome do arquivo sem a extensão
print(caminho_csv.suffix)      # atributo  -> '.csv': apenas a extensão
print(caminho_csv.parent)      # atributo  -> a pasta que contém o arquivo (Data)
print(caminho_csv.absolute())  # método    -> caminho completo a partir da raiz do sistema
print()

# stat().st_size devolve o tamanho em bytes: dá noção do volume antes de carregar.
print(f'Tamanho do arquivo: {caminho_csv.stat().st_size} bytes')
print()

# --- Usando o caminho para a análise ----------------------------------------
# exists() como guarda: evita o FileNotFoundError e dá uma mensagem clara.
if not caminho_csv.exists():
    raise SystemExit(f'Arquivo não encontrado: {caminho_csv}')

# O pandas aceita um objeto Path direto, sem precisar converter para string.
df_pedidos = pd.read_csv(caminho_csv)
df_pedidos['Total'] = df_pedidos['Unidades'] * df_pedidos['PrecoUnidade']

print(f'Pedidos carregados de {caminho_csv.name}: {len(df_pedidos)} linhas')
print(df_pedidos.head())
print()

# Faturamento por região, ordenado do maior para o menor.
print('Total por região:')
print(df_pedidos.groupby('Regiao')['Total'].sum().sort_values(ascending=False))
print()

# --- glob(): varrendo a pasta -----------------------------------------------
# Devolve todos os arquivos que batem com o padrão. Hoje há só um CSV, mas se
# surgirem Pedidos_2016.csv, Pedidos_2017.csv... o mesmo laço lê todos.
print('CSVs encontrados em Data/:')
for arquivo in (BASE / 'Data').glob('*.csv'):
    print(f'  {arquivo.name} -> {arquivo.stat().st_size} bytes')
print()

# Lendo e empilhando todos os CSVs da pasta de uma vez:
# df_completo = pd.concat([pd.read_csv(a) for a in (BASE / 'Data').glob('*.csv')],
#                         ignore_index=True)

# --- Montando o caminho de saída --------------------------------------------
# with_name()   -> troca o nome do arquivo, mantendo a mesma pasta
# with_suffix() -> troca apenas a extensão
print(caminho_csv.with_name('Pedidos_tratado.csv'))
print(caminho_csv.with_suffix('.xlsx'))
print()

# mkdir() cria a pasta; exist_ok=True evita erro caso ela já exista.
# Descomente as duas linhas quando for exportar o resultado da análise.
# (BASE / 'Saida').mkdir(exist_ok=True)
# df_pedidos.to_csv(BASE / 'Saida' / 'Pedidos_tratado.csv', index=False)
