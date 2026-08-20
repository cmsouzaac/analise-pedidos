# =============================================================================
# Autor.........: Cristian Matias de Souza
# Cargo/Nível...: Analista de Dados (N3)
# Criado em.....: 19/08/2026 22:26
# Versão........: 1.0
# -----------------------------------------------------------------------------
# Descrição.....: Camada de carga. Lê o dataset bruto de pedidos e devolve um
#                 DataFrame já tipado e com as colunas derivadas.
# Dependências..: pandas
# =============================================================================

from pathlib import Path

import pandas as pd

# src/ -> raiz do projeto. Dois .parent porque este arquivo está um nível abaixo.
BASE = Path(__file__).parent.parent
CAMINHO_PEDIDOS = BASE / 'Data' / 'Pedidos.csv'


def carregar_pedidos(caminho: Path | None = None) -> pd.DataFrame:
    """Lê o CSV de pedidos e devolve o DataFrame pronto para análise.

    O parâmetro `caminho` fica opcional para permitir apontar outro arquivo
    (um recorte, um CSV de teste) sem alterar o módulo.
    """
    caminho = caminho or CAMINHO_PEDIDOS

    if not caminho.exists():
        raise FileNotFoundError(f'Arquivo não encontrado: {caminho}')

    df = pd.read_csv(caminho)

    # DataPedido vem como texto no formato 7-Jun-2016; converter aqui evita
    # que cada análise repita o parsing.
    df['DataPedido'] = pd.to_datetime(df['DataPedido'], format='%d-%b-%Y')

    # Coluna derivada: faturamento de cada linha do pedido.
    df['Total'] = df['Unidades'] * df['PrecoUnidade']

    return df
