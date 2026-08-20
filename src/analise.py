# =============================================================================
# Autor.........: Cristian Matias de Souza
# Cargo/Nível...: Analista de Dados (N3)
# Criado em.....: 19/08/2026 22:26
# Alterado em...: 20/08/2026 08:05
# Versão........: 1.1
# -----------------------------------------------------------------------------
# Descrição.....: Camada de análise. Recebe o DataFrame de pedidos e devolve as
#                 agregações. Nenhuma função aqui lê arquivo nem plota nada.
# Histórico.....: 1.0 - as quatro agregações dos gráficos.
#                 1.1 - resumo(): KPIs de cabeçalho do relatório e do painel.
# Dependências..: pandas
# =============================================================================

import pandas as pd


def vendas_por_regiao(df: pd.DataFrame) -> pd.DataFrame:
    """Faturamento total por região, do maior para o menor."""
    return (df.groupby('Regiao')['Total']
              .sum()
              .sort_values(ascending=False)
              .reset_index())


def vendas_por_vendedor(df: pd.DataFrame) -> pd.DataFrame:
    """Faturamento e quantidade de pedidos por vendedor."""
    return (df.groupby('Vendedor')
              .agg(Total=('Total', 'sum'), Pedidos=('Total', 'size'))
              .sort_values('Total', ascending=False)
              .reset_index())


def vendas_por_mes(df: pd.DataFrame) -> pd.DataFrame:
    """Faturamento por mês, em ordem cronológica.

    Usa o primeiro dia do mês como rótulo para o eixo continuar sendo data —
    assim o gráfico ordena sozinho, sem depender de string.
    """
    mensal = (df.groupby(df['DataPedido'].dt.to_period('M'))['Total']
                .sum()
                .reset_index())
    mensal['DataPedido'] = mensal['DataPedido'].dt.to_timestamp()
    return mensal.sort_values('DataPedido')


def top_itens(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Os `n` itens que mais faturaram."""
    return (df.groupby('Item')['Total']
              .sum()
              .sort_values(ascending=False)
              .head(n)
              .reset_index())


def resumo(df: pd.DataFrame) -> dict:
    """Números de cabeçalho do relatório: os KPIs que abrem a leitura.

    Devolve um dicionário simples (não um DataFrame) porque o destino é texto
    em um cartão, não uma tabela nem um gráfico.
    """
    return {
        'faturamento': df['Total'].sum(),
        'pedidos': len(df),
        'ticket_medio': df['Total'].mean() if len(df) else 0.0,
        'unidades': int(df['Unidades'].sum()),
        'inicio': df['DataPedido'].min(),
        'fim': df['DataPedido'].max(),
        # Região que mais faturou — o destaque qualitativo do período.
        'regiao_lider': (df.groupby('Regiao')['Total'].sum().idxmax()
                         if len(df) else '—'),
    }
