# Análise de Pedidos

Pipeline de análise de vendas em Python: lê um CSV de pedidos, calcula as
agregações de negócio e gera quatro gráficos interativos em HTML.

O projeto é organizado em **camadas independentes** — carga, análise e
visualização — com um orquestrador (`main.py`) que as conecta. Cada camada tem
uma responsabilidade única e não conhece as outras:

```
Data/Pedidos.csv
       │
       ▼
 src/carga.py      → lê o CSV, tipa as colunas e cria a coluna Total
       │
       ▼
 src/analise.py    → agrega (DataFrame → DataFrame), sem ler arquivo nem plotar
       │
       ▼
 src/graficos.py   → monta as Figures do Plotly, sem agregar nem salvar
       │
       ▼
 main.py           → orquestra e decide o destino: Saida/*.html e/ou navegador
```

---

## Estrutura do projeto

```
Pedidos/
├── Data/
│   └── Pedidos.csv
├── src/
│   ├── __init__.py
│   ├── carga.py
│   ├── analise.py
│   └── graficos.py
├── Saida/                  (gerado ao executar)
│   ├── *.html              (interativos — fora do versionamento)
│   └── img/
│       ├── vendas_por_regiao.png
│       ├── vendas_por_vendedor.png
│       ├── vendas_por_mes.png
│       └── top_itens.png
├── main.py
├── MetodosPathlib.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Diretórios

| Diretório | O que guarda |
|---|---|
| `Data/` | Dados de entrada (dataset bruto). Nada aqui é modificado pelo pipeline — a leitura é sempre somente leitura. |
| `src/` | Pacote Python com a lógica do projeto, dividida em camadas. Nenhum módulo aqui é executado diretamente. |
| `Saida/` | Artefatos gerados pela execução. Criado automaticamente pelo `main.py`. Os HTML interativos são **ignorados pelo Git** (~4,8 MB cada, com o `plotly.js` embutido) — o repositório guarda o código que gera o resultado, não o resultado. |
| `Saida/img/` | Exceção à regra acima: os PNG estáticos (~500 KB no total) **ficam versionados**, para que os gráficos apareçam neste README sem que ninguém precise executar o projeto. |

### Arquivos

| Arquivo | Papel |
|---|---|
| `main.py` | **Ponto de entrada.** Orquestra o fluxo: carrega → agrega → plota → salva. É o único arquivo que decide o destino das figuras (HTML em `Saida/`, PNG em `Saida/img/` e/ou abrir no navegador). Também é onde a lista de relatórios é declarada — adicionar um gráfico novo é acrescentar uma linha nessa lista. |
| `src/__init__.py` | Marca `src/` como pacote Python, permitindo `from src import analise, graficos`. |
| `src/carga.py` | **Camada de carga.** Função `carregar_pedidos()`: valida a existência do arquivo, lê o CSV, converte `DataPedido` para `datetime` e cria a coluna derivada `Total` (`Unidades × PrecoUnidade`). Aceita um caminho opcional, o que permite apontar para outro CSV (recorte, arquivo de teste) sem alterar o módulo. |
| `src/analise.py` | **Camada de análise.** Quatro funções puras que recebem o DataFrame e devolvem uma agregação: `vendas_por_regiao()`, `vendas_por_vendedor()`, `vendas_por_mes()` e `top_itens(n=5)`. Nenhuma delas lê arquivo nem desenha gráfico. |
| `src/graficos.py` | **Camada de visualização.** Uma função por gráfico, cada uma recebendo um DataFrame já agregado e devolvendo uma `Figure` do Plotly. Define o template visual compartilhado (`pedidos`): paleta, tipografia, grade discreta e separadores no padrão brasileiro (vírgula decimal). Helpers internos cuidam de rótulos de mês em português (`jun/16`) e valores curtos em reais (`R$ 24,5 mil`). |
| `MetodosPathlib.py` | **Script de estudo, independente do pipeline.** Explora os métodos de `pathlib` (`exists`, `stem`, `suffix`, `stat`, `glob`, `with_name`, `with_suffix`, `mkdir`) aplicados ao dataset. Serve como material de referência e não é importado por nenhum outro módulo. |
| `requirements.txt` | Dependências do projeto: `pandas`, `plotly`, `kaleido`. |
| `.gitignore` | Mantém fora do repositório o ambiente virtual (`.venv/`), configurações da IDE (`.idea/`), caches (`__pycache__/`) e os HTML gerados (`Saida/*`), abrindo exceção para os PNG do README (`!Saida/img/`). |

---

## Dados

`Data/Pedidos.csv` — 43 pedidos de eletrodomésticos entre **jun/2016 e jun/2017**.

| Coluna | Tipo | Descrição |
|---|---|---|
| `DataPedido` | texto → `datetime` | Data do pedido, no formato `7-Jun-2016`. Convertida na carga. |
| `Regiao` | texto | Nordeste, Sudeste ou Sul. |
| `Estado` | texto | Unidade federativa do pedido (13 estados). |
| `Vendedor` | texto | Responsável pela venda (11 vendedores). |
| `Item` | texto | Fogão, Geladeira, Lavadora ou Microondas. |
| `Unidades` | inteiro | Quantidade vendida. |
| `PrecoUnidade` | decimal | Preço unitário em reais. |
| `Total` | decimal | **Coluna derivada** (`Unidades × PrecoUnidade`), criada em `src/carga.py`. |

---

## Relatórios gerados

| Arquivo em `Saida/` | Gráfico | Leitura |
|---|---|---|
| `vendas_por_regiao.html` | Barras verticais | Faturamento por região, do maior para o menor. |
| `vendas_por_vendedor.html` | Barras horizontais | Faturamento por vendedor; o hover mostra também a quantidade de pedidos. Nomes longos leem melhor deitados. |
| `vendas_por_mes.html` | Linha com marcadores | Evolução mensal do faturamento, com crosshair unificado no eixo x. |
| `top_itens.html` | Barras horizontais | Ranking dos itens que mais faturaram. |

Os HTML são autocontidos — o `plotly.js` fica embutido no arquivo, então
basta abrir no navegador: sem servidor e sem internet. Cada execução grava
também uma versão estática em `Saida/img/`, usada abaixo.

### Faturamento por região

![Faturamento por região](Saida/img/vendas_por_regiao.png)

### Faturamento por vendedor

![Faturamento por vendedor](Saida/img/vendas_por_vendedor.png)

### Evolução do faturamento por mês

![Evolução do faturamento por mês](Saida/img/vendas_por_mes.png)

### Top itens por faturamento

![Top itens por faturamento](Saida/img/top_itens.png)

---

## Como executar

```bash
# 1. Ambiente virtual
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Dependências
pip install -r requirements.txt

# 3. Pipeline completo
python main.py
```

A execução imprime cada agregação no terminal, grava os quatro HTML em
`Saida/` e os quatro PNG em `Saida/img/` (~7 s no total). Dois interruptores
no final do `main.py` controlam o comportamento:

| Parâmetro | Padrão | Efeito |
|---|---|---|
| `exibir` | `True` | Abre cada gráfico no navegador. Use `False` para apenas gravar os arquivos. |
| `gerar_png` | `True` | Exporta os PNG via `kaleido`. Use `False` para uma execução mais rápida, só com os HTML. |

A exportação de PNG depende do `kaleido`, que usa um Chrome headless. Se ele
não estiver disponível na máquina, o `main.py` avisa no terminal e segue — os
HTML, que são o resultado principal, são gerados do mesmo jeito.

Para rodar o script de estudo de `pathlib`:

```bash
python MetodosPathlib.py
```

**Requisitos:** Python 3.10+ (o código usa a sintaxe `Path | None`).
Desenvolvido em Python 3.14.

---

## Decisões de projeto

- **Separação por camadas.** Análise não sabe de onde vêm os dados; gráficos
  não sabem como os números foram calculados. Trocar a fonte (CSV → banco)
  mexe em um arquivo só.
- **Funções que devolvem, não que imprimem.** As camadas retornam DataFrames e
  Figures; só o `main.py` decide o que fazer com eles. Isso torna cada função
  testável e reutilizável.
- **Caminhos com `pathlib`.** Todos os caminhos partem de `Path(__file__).parent`,
  então o projeto roda de qualquer diretório e em qualquer sistema operacional.
- **Formatação brasileira.** Vírgula decimal, meses em português e valores
  abreviados em reais — o gráfico é lido por quem fala português.
- **PNG versionado, HTML não.** O interativo é o entregável, mas pesa 4,8 MB
  por arquivo e pode ser regerado a qualquer momento; o estático é leve e
  documenta o resultado direto neste README.
- **Sem legenda nos gráficos.** Todas as séries são únicas: o título já diz o
  que está sendo medido, e a legenda seria ruído.

---

## Autor

**Cristian Matias de Souza** — Analista de Dados
