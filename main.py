# =============================================================================
# Autor.........: Cristian Matias de Souza
# Cargo/Nível...: Analista de Dados (N3)
# Criado em.....: 19/08/2026 22:26
# Versão........: 1.1
# -----------------------------------------------------------------------------
# Descrição.....: Orquestrador da análise de pedidos.
#                 Carrega -> agrega -> plota -> salva. É o único arquivo que
#                 decide o que fazer com as figuras (exibir ou gravar).
# Dependências..: pandas, plotly, kaleido (opcional, só para os PNG)
# =============================================================================

from pathlib import Path

import pandas as pd

from src import analise, graficos
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


def main(exibir: bool = False, gerar_png: bool = True) -> None:
    df = carregar_pedidos()
    print(f'Pedidos carregados: {len(df)} linhas\n')

    # Cada item liga uma agregação à figura correspondente e ao nome do arquivo.
    relatorios = [
        ('vendas_por_regiao',
         analise.vendas_por_regiao(df),
         graficos.grafico_vendas_por_regiao),
        ('vendas_por_vendedor',
         analise.vendas_por_vendedor(df),
         graficos.grafico_vendas_por_vendedor),
        ('vendas_por_mes',
         analise.vendas_por_mes(df),
         graficos.grafico_vendas_por_mes),
        ('top_itens',
         analise.top_itens(df),
         graficos.grafico_top_itens),
    ]

    SAIDA.mkdir(exist_ok=True)
    if gerar_png:
        SAIDA_IMG.mkdir(parents=True, exist_ok=True)

    for nome, dados, construir_figura in relatorios:
        print(f'=== {nome} ===')
        print(dados, '\n')

        fig = construir_figura(dados)

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

        if exibir:
            fig.show()


if __name__ == '__main__':
    # exibir=False  -> só grava os arquivos, sem abrir o navegador.
    # gerar_png=False -> pula a exportação estática (execução mais rápida).
    main(exibir=True, gerar_png=True)
