# =============================================================================
# Autor.........: Cristian Matias de Souza
# Cargo/Nível...: Analista de Dados (N3)
# Criado em.....: 20/08/2026 07:40
# Versão........: 1.0
# -----------------------------------------------------------------------------
# Descrição.....: Camada de entrega. Declara o catálogo de relatórios (o que
#                 entra, em que ordem e como se lê cada gráfico) e junta as
#                 figuras em uma única página HTML autocontida — o arquivo que
#                 vai para o cliente.
#                 Regra da camada: não lê arquivo e não grava nada; devolve a
#                 string HTML e quem escreve em disco é quem chamou.
# Dependências..: plotly, pandas
# =============================================================================

from datetime import datetime
from html import escape

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from src import analise, graficos
# Reusa a paleta da camada de gráficos: uma cor definida em um lugar só.
from src.graficos import (AZUL, GRADE, SUPERFICIE, TEXTO_PRIMARIO,
                          TEXTO_SECUNDARIO)

MESES_PT = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
            'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']

# Barra de ferramentas enxuta: o cliente quer ler e, no máximo, baixar a
# imagem — os botões de seleção e lasso só confundem quem não usa Plotly.
CONFIG_PLOTLY = {
    'displaylogo': False,
    'responsive': True,
    'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'autoScale2d',
                               'zoomIn2d', 'zoomOut2d'],
}


# --- Catálogo ---------------------------------------------------------------
# Fonte única da verdade sobre o que compõe a entrega: nome do arquivo, a
# agregação, a figura e a frase que explica como ler o gráfico. O main.py (saída
# em arquivo) e o app.py (painel Dash) leem daqui, então acrescentar um gráfico
# novo é acrescentar uma linha nesta lista — e ele aparece nos dois.
RELATORIOS = [
    ('vendas_por_regiao',
     analise.vendas_por_regiao,
     graficos.grafico_vendas_por_regiao,
     'Comparação direta entre as regiões atendidas. A altura da barra é o '
     'faturamento acumulado em todo o período.'),
    ('vendas_por_vendedor',
     analise.vendas_por_vendedor,
     graficos.grafico_vendas_por_vendedor,
     'Ranking do time comercial. Passe o mouse sobre a barra para ver também '
     'quantos pedidos cada vendedor fechou — faturar mais nem sempre significa '
     'vender mais vezes.'),
    ('vendas_por_mes',
     analise.vendas_por_mes,
     graficos.grafico_vendas_por_mes,
     'Evolução mês a mês. Serve para separar tendência de sazonalidade: picos '
     'isolados costumam ser um pedido grande, não uma mudança de patamar.'),
    ('top_itens',
     analise.top_itens,
     graficos.grafico_top_itens,
     'Os produtos que mais pesam no faturamento — não necessariamente os mais '
     'vendidos em unidades, já que o preço unitário varia.'),
]


def construir(df: pd.DataFrame) -> list[tuple[str, pd.DataFrame, go.Figure, str]]:
    """Roda o catálogo inteiro sobre um DataFrame de pedidos.

    Devolve, para cada relatório, a tupla (nome, agregação, figura, nota).
    Quem chama decide o destino: gravar em disco, montar a página ou devolver
    para o navegador em um callback do Dash.
    """
    itens = []
    for nome, agregar, plotar, nota in RELATORIOS:
        dados = agregar(df)
        itens.append((nome, dados, plotar(dados), nota))
    return itens

def _moeda(valor: float) -> str:
    """Padrão brasileiro: 2913448.88 -> 'R$ 2.913.448,88'."""
    # Formata no padrão en-US e troca os separadores: evita depender de locale
    # instalado no sistema, que varia entre a máquina de quem gera e a do CI.
    corpo = f'{valor:,.2f}'.replace(',', '§').replace('.', ',').replace('§', '.')
    return f'R$ {corpo}'


def _inteiro(valor: int) -> str:
    """1234 -> '1.234'."""
    return f'{valor:,}'.replace(',', '.')


def _periodo(inicio: pd.Timestamp, fim: pd.Timestamp) -> str:
    """Intervalo por extenso: 'junho de 2016 a junho de 2017'."""
    return (f'{MESES_PT[inicio.month - 1]} de {inicio:%Y} a '
            f'{MESES_PT[fim.month - 1]} de {fim:%Y}')


def _cartao(rotulo: str, valor: str) -> str:
    """Stat tile: rótulo em caixa baixa, valor em destaque."""
    return (f'<div class="cartao"><p class="rotulo">{escape(rotulo)}</p>'
            f'<p class="valor">{escape(valor)}</p></div>')


def _secao(fig: go.Figure, nota: str, div_id: str, embutir_js: bool) -> str:
    """Um gráfico e a frase que diz como lê-lo.

    O título já está dentro da figura, então a seção não o repete — a nota
    entra abaixo, no papel de legenda editorial.

    `embutir_js` só é True na primeira seção: é o que faz o plotly.js entrar
    uma vez no documento em vez de uma vez por gráfico.
    """
    grafico = pio.to_html(fig, full_html=False, include_plotlyjs=embutir_js,
                          config=CONFIG_PLOTLY, div_id=div_id)
    return (f'<section class="secao">{grafico}'
            f'<p class="nota">{escape(nota)}</p></section>')


def montar_relatorio(secoes: list[tuple[str, go.Figure, str]],
                     resumo: dict,
                     cliente: str | None = None,
                     gerado_em: datetime | None = None) -> str:
    """Monta a página completa e devolve o HTML como string.

    `secoes` é uma lista de (id_do_div, figura, nota). O `plotly.js` entra uma
    única vez no documento — é o que faz um relatório com quatro gráficos pesar
    o mesmo que um gráfico solto (~4,8 MB) em vez de quatro vezes isso.
    """
    gerado_em = gerado_em or datetime.now()
    periodo = _periodo(resumo['inicio'], resumo['fim'])

    cartoes = ''.join([
        _cartao('Pedidos no período', _inteiro(resumo['pedidos'])),
        _cartao('Ticket médio', _moeda(resumo['ticket_medio'])),
        _cartao('Unidades vendidas', _inteiro(resumo['unidades'])),
        _cartao('Região líder', resumo['regiao_lider']),
    ])
    corpo = ''.join(_secao(fig, nota, div_id, embutir_js=(i == 0))
                    for i, (div_id, fig, nota) in enumerate(secoes))

    destinatario = (f'<p class="destinatario">Preparado para '
                    f'<strong>{escape(cliente)}</strong></p>') if cliente else ''

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Análise de Pedidos — {escape(periodo)}</title>
<style>
  :root {{
    --azul: {AZUL};
    --texto: {TEXTO_PRIMARIO};
    --texto-2: {TEXTO_SECUNDARIO};
    --grade: {GRADE};
    --superficie: {SUPERFICIE};
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--superficie);
    color: var(--texto);
    font-family: Inter, 'Segoe UI', system-ui, sans-serif;
    font-size: 15px;
    line-height: 1.55;
  }}
  .pagina {{ max-width: 960px; margin: 0 auto; padding: 48px 24px 64px; }}

  /* --- Cabeçalho --- */
  header {{ border-bottom: 1px solid var(--grade); padding-bottom: 28px; }}
  h1 {{ font-size: 28px; margin: 0 0 4px; letter-spacing: -0.01em; }}
  .periodo {{ margin: 0; color: var(--texto-2); }}
  .destinatario {{ margin: 12px 0 0; color: var(--texto-2); }}

  /* --- Número principal: um por página, como manda o bom senso --- */
  .destaque {{ margin: 32px 0 8px; }}
  .destaque .rotulo {{ margin: 0; color: var(--texto-2); font-size: 14px; }}
  .destaque .valor {{
    margin: 2px 0 0;
    font-size: 52px;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: var(--azul);
  }}

  /* --- Cartões de apoio --- */
  .cartoes {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1px;
    background: var(--grade);
    border: 1px solid var(--grade);
    border-radius: 8px;
    overflow: hidden;
    margin: 28px 0 8px;
  }}
  .cartao {{ background: var(--superficie); padding: 16px 18px; }}
  .cartao .rotulo {{ margin: 0; color: var(--texto-2); font-size: 13px; }}
  .cartao .valor {{ margin: 2px 0 0; font-size: 22px; font-weight: 600; }}

  /* --- Gráficos --- */
  .secao {{ margin-top: 40px; padding-top: 28px; border-top: 1px solid var(--grade); }}
  .secao .plotly-graph-div {{ width: 100% !important; }}
  .nota {{ margin: 8px 2px 0; color: var(--texto-2); font-size: 14px; max-width: 68ch; }}

  footer {{
    margin-top: 48px; padding-top: 20px;
    border-top: 1px solid var(--grade);
    color: var(--texto-2); font-size: 13px;
  }}
  footer p {{ margin: 2px 0; }}

  /* --- Impressão / exportação em PDF --- */
  @media print {{
    .pagina {{ max-width: none; padding: 0; }}
    .secao {{ page-break-inside: avoid; break-inside: avoid; }}
    .modebar {{ display: none !important; }}
  }}
</style>
</head>
<body>
<div class="pagina">
  <header>
    <h1>Análise de Pedidos</h1>
    <p class="periodo">Faturamento de {escape(periodo)}</p>
    {destinatario}
  </header>

  <div class="destaque">
    <p class="rotulo">Faturamento total no período</p>
    <p class="valor">{escape(_moeda(resumo['faturamento']))}</p>
  </div>

  <div class="cartoes">{cartoes}</div>

  {corpo}

  <footer>
    <p>Relatório gerado em {gerado_em:%d/%m/%Y às %H:%M}.</p>
    <p>Fonte: base de pedidos — {_inteiro(resumo['pedidos'])} registros.
       Os gráficos são interativos: passe o mouse para ver os valores exatos.</p>
    <p>Cristian Matias de Souza — Analista de Dados</p>
  </footer>
</div>
</body>
</html>
"""
