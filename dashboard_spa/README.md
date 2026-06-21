# Dashboard — Gap Salarial na Região Sul

Dashboard Streamlit, single-page, consumindo diretamente os dois datasets
finais do PM3 (`dados/gold/pnad_treated_data.csv` e
`dados/gold/pnad_context_data.csv`), gerados por
`notebooks/03_tratamento_pm3.ipynb`. Não obrigatório pelo PM3
(`docs/gold_context.md`, seção 1) — implementado como extensão de BI sobre o
dataset tratado.

O racional de design e a análise de cada gráfico (dados usados, números reais,
por que aquele tipo de gráfico foi escolhido) estão em
[`docs/storytelling.md`](docs/storytelling.md) e
[`docs/analise_graficos.md`](docs/analise_graficos.md).

## Como rodar

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```

Pré-requisito: os dois CSVs em `dados/gold/` precisam existir — execute
`notebooks/03_tratamento_pm3.ipynb` antes, se ainda não tiver feito (no Windows,
com `PYTHONUTF8=1` definido — ver `README.md` da raiz).

## Estrutura

```
dashboard/
├── app.py          # App único — sidebar de filtros + KPIs + 3 abas internas
├── data.py         # Carregamento e agregações (recalculadas sob os filtros ativos)
├── theme.py        # Paleta de cores e template Plotly compartilhados
├── docs/
│   ├── storytelling.md      # Racional de design (por que single-page, por que cada decisão)
│   └── analise_graficos.md  # Análise gráfico a gráfico
└── README.md
```

Filtros (UF, período) ficam na sidebar e recalculam todos os KPIs e gráficos —
nenhum número é estático. As três abas (`st.tabs`) organizam os gráficos por
tema sem sair da página nem recarregar dados.

## Testes

```bash
python -c "
from streamlit.testing.v1 import AppTest
at = AppTest.from_file('dashboard/app.py', default_timeout=60)
at.run()
assert not at.exception, at.exception
print('OK')
"
```
