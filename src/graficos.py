# =============================================================================
# Autor.........: Cristian Matias de Souza
# Cargo/Nível...: Analista de Dados (N3)
# Criado em.....: 19/08/2026 22:26
# Versão........: 1.0
# -----------------------------------------------------------------------------
# Descrição.....: Camada de visualização. Cada função recebe um DataFrame já
#                 agregado e devolve uma Figure do Plotly.
#                 Regra da camada: não lê arquivo, não agrega e não chama
#                 .show() — quem decide o destino da figura é o main.py.
# Dependências..: plotly, pandas
# =============================================================================

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

# --- Paleta -----------------------------------------------------------------
# Uma cor por papel, definida em um lugar só. Como todos os gráficos aqui têm
# série única, a identidade não depende de cor: o título já diz o que é medido,
# por isso não há legenda.
AZUL = '#2a78d6'          # cor da série
TEXTO_PRIMARIO = '#0b0b0b'
TEXTO_SECUNDARIO = '#52514e'
GRADE = '#e6e5e1'
SUPERFICIE = '#fcfcfb'

# Template compartilhado: evita repetir update_layout em cada função.
pio.templates['pedidos'] = go.layout.Template(
    layout=dict(
        font=dict(family='Inter, Segoe UI, sans-serif', size=13,
                  color=TEXTO_PRIMARIO),
        title=dict(font=dict(size=17), x=0, xanchor='left'),
        paper_bgcolor=SUPERFICIE,
        plot_bgcolor=SUPERFICIE,
        colorway=[AZUL],
        margin=dict(l=70, r=30, t=70, b=60),
        # Grade discreta: serve de apoio à leitura, não disputa com os dados.
        xaxis=dict(showgrid=False, linecolor=GRADE,
                   tickfont=dict(color=TEXTO_SECUNDARIO)),
        yaxis=dict(gridcolor=GRADE, zeroline=False, showline=False,
                   tickfont=dict(color=TEXTO_SECUNDARIO)),
        hoverlabel=dict(font_size=13),
        # Padrão brasileiro: vírgula decimal, ponto no milhar.
        separators=',.',
    )
)
pio.templates.default = 'pedidos'


# Plotly formata datas em inglês; o mapa abaixo troca os rótulos do eixo.
MESES_PT = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun',
            'jul', 'ago', 'set', 'out', 'nov', 'dez']


def _rotulos_mes(datas: pd.Series) -> list[str]:
    """Rótulos de eixo em português: 2016-06-01 -> 'jun/16'."""
    return [f'{MESES_PT[d.month - 1]}/{d:%y}' for d in datas]


def _formatar_reais(valores: pd.Series) -> list[str]:
    """Rótulos curtos em reais: 24.500 -> 'R$ 24,5 mil'; 1.712.354 -> 'R$ 1,7 mi'."""
    rotulos = []
    for v in valores:
        if v >= 1_000_000:
            rotulos.append(f'R$ {v / 1_000_000:.1f} mi'.replace('.', ','))
        else:
            rotulos.append(f'R$ {v / 1_000:.1f} mil'.replace('.', ','))
    return rotulos


def _folga_direita(fig: go.Figure, valores: pd.Series) -> None:
    """Estende o eixo x para o rótulo da maior barra não encostar na borda."""
    fig.update_xaxes(range=[0, valores.max() * 1.18])


def grafico_vendas_por_regiao(df: pd.DataFrame) -> go.Figure:
    """Barras verticais: faturamento por região, já ordenado pela análise."""
    fig = go.Figure(
        go.Bar(
            x=df['Regiao'],
            y=df['Total'],
            marker_color=AZUL,
            marker_cornerradius=4,       # topo arredondado, base na linha zero
            text=_formatar_reais(df['Total']),
            textposition='outside',
            textfont=dict(color=TEXTO_SECUNDARIO),
            hovertemplate='<b>%{x}</b><br>Faturamento: R$ %{y:,.2f}<extra></extra>',
        )
    )
    fig.update_layout(
        title='Faturamento por região',
        yaxis_title='Faturamento (R$)',
        xaxis_title=None,
        # Com poucas categorias a barra fica larga demais e vira bloco de cor.
        bargap=0.5,
    )
    # Folga no topo para o rótulo da barra mais alta não encostar no título.
    fig.update_yaxes(range=[0, df['Total'].max() * 1.12],
                     tickprefix='R$ ', tickformat='~s')
    return fig


def grafico_vendas_por_vendedor(df: pd.DataFrame) -> go.Figure:
    """Barras horizontais: nome de vendedor é texto longo, lê melhor deitado."""
    dados = df.sort_values('Total')   # menor embaixo -> maior no topo
    fig = go.Figure(
        go.Bar(
            x=dados['Total'],
            y=dados['Vendedor'],
            orientation='h',
            marker_color=AZUL,
            marker_cornerradius=4,
            text=_formatar_reais(dados['Total']),
            textposition='outside',
            textfont=dict(color=TEXTO_SECUNDARIO),
            customdata=dados['Pedidos'],
            hovertemplate=('<b>%{y}</b><br>Faturamento: R$ %{x:,.2f}'
                           '<br>Pedidos: %{customdata}<extra></extra>'),
        )
    )
    fig.update_layout(
        title='Faturamento por vendedor',
        xaxis_title='Faturamento (R$)',
        yaxis_title=None,
        height=max(320, 46 * len(dados)),   # cresce junto com a quantidade
        bargap=0.35,
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRADE, tickprefix='R$ ',
                     tickformat='~s')
    fig.update_yaxes(showgrid=False)
    _folga_direita(fig, dados['Total'])
    return fig


def grafico_vendas_por_mes(df: pd.DataFrame) -> go.Figure:
    """Linha: evolução no tempo. Eixo x é data, então ordena sozinho."""
    fig = go.Figure(
        go.Scatter(
            x=df['DataPedido'],
            y=df['Total'],
            mode='lines+markers',
            line=dict(color=AZUL, width=2),
            marker=dict(size=8, color=AZUL,
                        line=dict(width=2, color=SUPERFICIE)),
            customdata=_rotulos_mes(df['DataPedido']),
            hovertemplate=('<b>%{customdata}</b><br>'
                           'Faturamento: R$ %{y:,.2f}<extra></extra>'),
        )
    )
    fig.update_layout(
        title='Evolução do faturamento por mês',
        yaxis_title='Faturamento (R$)',
        xaxis_title=None,
        # Crosshair: em série temporal o valor é lido na vertical.
        hovermode='x unified',
    )
    fig.update_xaxes(tickmode='array', tickvals=df['DataPedido'],
                     ticktext=_rotulos_mes(df['DataPedido']))
    fig.update_yaxes(rangemode='tozero', tickprefix='R$ ', tickformat='~s')
    return fig


def grafico_top_itens(df: pd.DataFrame) -> go.Figure:
    """Barras horizontais com o ranking de itens."""
    dados = df.sort_values('Total')
    fig = go.Figure(
        go.Bar(
            x=dados['Total'],
            y=dados['Item'],
            orientation='h',
            marker_color=AZUL,
            marker_cornerradius=4,
            text=_formatar_reais(dados['Total']),
            textposition='outside',
            textfont=dict(color=TEXTO_SECUNDARIO),
            hovertemplate='<b>%{y}</b><br>Faturamento: R$ %{x:,.2f}<extra></extra>',
        )
    )
    fig.update_layout(
        title=f'Top {len(dados)} itens por faturamento',
        xaxis_title='Faturamento (R$)',
        yaxis_title=None,
        height=max(320, 46 * len(dados)),
        bargap=0.35,
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRADE, tickprefix='R$ ',
                     tickformat='~s')
    fig.update_yaxes(showgrid=False)
    _folga_direita(fig, dados['Total'])
    return fig
