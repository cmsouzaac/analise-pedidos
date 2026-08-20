# =============================================================================
# Autor.........: Cristian Matias de Souza
# Cargo/Nível...: Analista de Dados (N3)
# Criado em.....: 20/08/2026 07:55
# Versão........: 1.0
# -----------------------------------------------------------------------------
# Descrição.....: Painel interativo (Dash) da análise de pedidos.
#                 É um orquestrador irmão do main.py: onde o main.py grava
#                 arquivos, este serve os mesmos gráficos em um servidor web
#                 com filtros de período, região e vendedor — e exporta o
#                 relatório HTML já com o recorte aplicado.
#                 Reusa src/carga.py, src/analise.py, src/graficos.py e
#                 src/relatorio.py sem alterar nenhum deles.
# Dependências..: dash, pandas, plotly
# =============================================================================

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, callback, dcc, html

from src import analise, relatorio
from src.carga import carregar_pedidos
from src.graficos import SUPERFICIE, TEXTO_SECUNDARIO

# O CSV é pequeno e não muda durante a execução: carregar uma vez na subida
# evita reler o arquivo a cada interação do usuário.
PEDIDOS = carregar_pedidos()

DATA_MIN = PEDIDOS['DataPedido'].min()
DATA_MAX = PEDIDOS['DataPedido'].max()
REGIOES = sorted(PEDIDOS['Regiao'].unique())
VENDEDORES = sorted(PEDIDOS['Vendedor'].unique())

app = Dash(__name__, title='Análise de Pedidos')
server = app.server          # ponto de entrada para WSGI (gunicorn), se hospedar


def filtrar(inicio, fim, regioes, vendedores) -> pd.DataFrame:
    """Aplica os filtros da barra superior e devolve o recorte dos pedidos.

    Filtro vazio (None ou lista vazia) significa "todos" — é o comportamento
    que o usuário espera ao limpar um dropdown.
    """
    df = PEDIDOS
    if inicio:
        df = df[df['DataPedido'] >= pd.to_datetime(inicio)]
    if fim:
        df = df[df['DataPedido'] <= pd.to_datetime(fim)]
    if regioes:
        df = df[df['Regiao'].isin(regioes)]
    if vendedores:
        df = df[df['Vendedor'].isin(vendedores)]
    return df


def figura_vazia() -> go.Figure:
    """Placeholder para quando o filtro não devolve nenhum pedido.

    Sem isso as agregações chegariam vazias na camada de gráficos, que
    calcularia max() de série vazia e produziria um eixo com NaN.
    """
    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor=SUPERFICIE, plot_bgcolor=SUPERFICIE, height=280,
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        margin=dict(l=20, r=20, t=20, b=20),
        annotations=[dict(
            text='Nenhum pedido no recorte selecionado.',
            showarrow=False, font=dict(size=15, color=TEXTO_SECUNDARIO),
            xref='paper', yref='paper', x=0.5, y=0.5,
        )],
    )
    return fig


def cartoes(df: pd.DataFrame) -> list:
    """Número principal + os quatro cartões de apoio, já formatados."""
    if df.empty:
        return [html.P('Nenhum pedido no recorte selecionado.',
                       className='nota')]

    r = analise.resumo(df)
    apoio = [
        ('Pedidos no período', relatorio._inteiro(r['pedidos'])),
        ('Ticket médio', relatorio._moeda(r['ticket_medio'])),
        ('Unidades vendidas', relatorio._inteiro(r['unidades'])),
        ('Região líder', r['regiao_lider']),
    ]
    return [
        html.Div(className='destaque', children=[
            html.P('Faturamento total no período', className='rotulo'),
            html.P(relatorio._moeda(r['faturamento']), className='valor'),
        ]),
        html.Div(className='cartoes', children=[
            html.Div(className='cartao', children=[
                html.P(rotulo, className='rotulo'),
                html.P(valor, className='valor'),
            ]) for rotulo, valor in apoio
        ]),
    ]


# --- Layout -----------------------------------------------------------------
# Os gráficos são criados a partir do catálogo em src/relatorio.py: acrescentar
# um relatório lá o faz aparecer aqui e no main.py, sem mexer neste arquivo.
app.layout = html.Div(className='pagina', children=[
    html.Div(className='cabecalho', children=[
        html.H1('Análise de Pedidos'),
        html.P('Painel interativo — filtre o recorte e exporte o relatório '
               'para enviar ao cliente.'),
    ]),

    html.Div(className='filtros', children=[
        html.Div(className='filtro', children=[
            html.Label('Período'),
            dcc.DatePickerRange(
                id='periodo',
                min_date_allowed=DATA_MIN, max_date_allowed=DATA_MAX,
                start_date=DATA_MIN, end_date=DATA_MAX,
                display_format='DD/MM/YYYY',
                start_date_placeholder_text='Início',
                end_date_placeholder_text='Fim',
            ),
        ]),
        html.Div(className='filtro', children=[
            html.Label('Região'),
            dcc.Dropdown(id='regiao', options=REGIOES, multi=True,
                         placeholder='Todas'),
        ]),
        html.Div(className='filtro', children=[
            html.Label('Vendedor'),
            dcc.Dropdown(id='vendedor', options=VENDEDORES, multi=True,
                         placeholder='Todos'),
        ]),
        html.Div(className='acao', children=[
            html.Button('Baixar relatório', id='exportar', className='botao'),
            dcc.Download(id='download'),
        ]),
    ]),

    html.Div(id='kpis'),

    *[html.Div(className='secao', children=[
        dcc.Graph(id=f'grafico-{nome}', config=relatorio.CONFIG_PLOTLY),
        html.P(nota, className='nota'),
    ]) for nome, _agregar, _plotar, nota in relatorio.RELATORIOS],

    html.Div(className='rodape', children=[
        html.P('Fonte: Data/Pedidos.csv. Os filtros valem para todos os '
               'gráficos e para o relatório exportado.'),
        html.P('Cristian Matias de Souza — Analista de Dados'),
    ]),
])

FILTROS = [Input('periodo', 'start_date'), Input('periodo', 'end_date'),
           Input('regiao', 'value'), Input('vendedor', 'value')]


@callback(
    [Output('kpis', 'children')] +
    [Output(f'grafico-{nome}', 'figure') for nome, *_ in relatorio.RELATORIOS],
    FILTROS,
)
def atualizar(inicio, fim, regioes, vendedores):
    """Refaz KPIs e gráficos a cada mudança de filtro."""
    df = filtrar(inicio, fim, regioes, vendedores)

    if df.empty:
        return [cartoes(df)] + [figura_vazia() for _ in relatorio.RELATORIOS]

    figuras = [fig for _nome, _dados, fig, _nota in relatorio.construir(df)]
    return [cartoes(df)] + figuras


@callback(
    Output('download', 'data'),
    Input('exportar', 'n_clicks'),
    [State(c.component_id, c.component_property) for c in FILTROS],
    prevent_initial_call=True,
)
def exportar(_n_clicks, inicio, fim, regioes, vendedores):
    """Gera o relatório HTML do recorte atual e entrega ao navegador.

    É o mesmo arquivo que o main.py grava em Saida/ — a diferença é que aqui
    ele sai já filtrado, sem precisar editar código para recortar os dados.
    """
    df = filtrar(inicio, fim, regioes, vendedores)
    if df.empty:
        return None

    secoes = [(nome, fig, nota)
              for nome, _dados, fig, nota in relatorio.construir(df)]
    html_relatorio = relatorio.montar_relatorio(secoes, analise.resumo(df))
    return dcc.send_string(html_relatorio, 'relatorio.html')


if __name__ == '__main__':
    # debug=True recarrega o servidor a cada alteração no código.
    app.run(debug=True, port=8050)
