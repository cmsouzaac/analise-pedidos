# =============================================================================
# Autor.........: Cristian Matias de Souza
# Cargo/Nível...: Analista de Dados (N3)
# Criado em.....: 19/08/2026 22:26
# Alterado em...: 20/08/2026 08:30
# Versão........: 1.3
# -----------------------------------------------------------------------------
# Descrição.....: Orquestrador da análise de pedidos em modo arquivo.
#                 Carrega -> agrega -> plota -> grava. É o único arquivo que
#                 decide o destino das figuras; o que entra na entrega e em
#                 que ordem é declarado no catálogo de src/relatorio.py.
#                 Gera três coisas em Saida/: um HTML por gráfico, um PNG por
#                 gráfico (para o README) e o relatorio.html consolidado — o
#                 arquivo único que vai para o cliente, e o que é aberto no
#                 navegador quando exibir=True.
#                 Para a versão interativa com filtros, veja app.py.
# Histórico.....: 1.0 - versão inicial (agrega e exibe no navegador).
#                 1.1 - exportação de PNG via kaleido.
#                 1.2 - relatório consolidado e catálogo em src/relatorio.py.
#                 1.3 - exibir=True abre o consolidado (antes: uma aba por
#                       gráfico).
# Dependências..: pandas, plotly, kaleido (opcional, só para os PNG)
# =============================================================================

import webbrowser
from pathlib import Path

import pandas as pd

from src import analise, relatorio
from src.carga import carregar_pedidos

BASE = Path(__file__).parent
SAIDA = BASE / 'Saida'
SAIDA_IMG = SAIDA / 'img'

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)


def salvar_png(fig, destino: Path) -> bool:
    """Grava a figura como PNG. Devolve False se o kaleido não estiver pronto.

    O PNG é um extra para a documentação (README): se a exportação falhar por
    falta do kaleido ou do Chrome headless, o pipeline segue e os HTML — que
    são o resultado principal — continuam sendo gerados normalmente.
    """
    try:
        # Respeita a altura definida na figura (os gráficos horizontais crescem
        # com a quantidade de barras); 560 é o padrão para quem não define.
        altura = fig.layout.height or 560
        fig.write_image(destino, width=1000, height=altura, scale=2)
        return True
    except Exception as erro:
        print(f'PNG não gerado ({type(erro).__name__}): {erro}')
        return False


def main(exibir: bool = False,
         gerar_png: bool = True,
         cliente: str | None = None) -> None:
    """Roda o pipeline inteiro e grava os artefatos em Saida/.

    `exibir` abre o relatório consolidado no navegador ao final — uma aba com
    o projeto todo, e não uma aba por gráfico como nas versões anteriores.
    """
    df = carregar_pedidos()
    print(f'Pedidos carregados: {len(df)} linhas\n')

    # O que entra na entrega é declarado uma vez em src/relatorio.py — aqui só
    # se decide o destino de cada peça.
    itens = relatorio.construir(df)

    SAIDA.mkdir(exist_ok=True)
    if gerar_png:
        SAIDA_IMG.mkdir(parents=True, exist_ok=True)

    for nome, dados, fig, _nota in itens:
        print(f'=== {nome} ===')
        print(dados, '\n')

        # HTML interativo, com o plotly.js embutido: abre offline, sem servidor.
        destino_html = SAIDA / f'{nome}.html'
        fig.write_html(destino_html, include_plotlyjs=True)
        print(f'gráfico salvo em {destino_html.relative_to(BASE)}')

        # PNG estático: leve o bastante para ser versionado e exibido no README.
        if gerar_png:
            destino_png = SAIDA_IMG / f'{nome}.png'
            if salvar_png(fig, destino_png):
                print(f'imagem salva em {destino_png.relative_to(BASE)}')

        print()

    # Entregável para o cliente: um arquivo só, com os quatro gráficos, os
    # números de cabeçalho e o plotly.js embutido uma única vez.
    secoes = [(nome, fig, nota) for nome, _dados, fig, nota in itens]
    destino_relatorio = SAIDA / 'relatorio.html'
    destino_relatorio.write_text(
        relatorio.montar_relatorio(secoes, analise.resumo(df), cliente=cliente),
        encoding='utf-8',
    )
    print(f'relatório consolidado em {destino_relatorio.relative_to(BASE)}')

    # Uma aba só, com o projeto inteiro: é o mesmo arquivo que vai para o
    # cliente, então conferir aqui é conferir o que ele vai receber.
    if exibir:
        webbrowser.open(destino_relatorio.as_uri())
        print('abrindo no navegador')


if __name__ == '__main__':
    # exibir=False    -> só grava os arquivos, sem abrir o navegador.
    # gerar_png=False -> pula a exportação estática (execução mais rápida).
    # cliente='...'   -> escreve "Preparado para X" no cabeçalho do relatório.
    main(exibir=True, gerar_png=True, cliente=None)
