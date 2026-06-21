# Dashboard — "Elas estudam mais. Elas ganham menos."

Dashboard Streamlit em formato de investigação narrativa sobre o gap salarial de
gênero no mercado de trabalho da Região Sul, consumindo diretamente os dois
datasets finais do PM3 (`dados/gold/pnad_treated_data.csv` e
`dados/gold/pnad_context_data.csv`), gerados por
`notebooks/03_tratamento_pm3.ipynb`. Não obrigatório pelo PM3
(`docs/gold_context.md`, seção 1) — implementado como extensão de BI sobre o
dataset tratado.

A lógica da narrativa, capítulo a capítulo, e a análise de cada gráfico (o que
mostra, os números reais, por que esse tipo de gráfico foi escolhido) estão em
[`dashboard/docs/storytelling.md`](docs/storytelling.md) e
[`dashboard/docs/analise_graficos.md`](docs/analise_graficos.md).

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
├── app.py                          # Capa — o "gancho" da história
├── pages/
│   ├── 1_📖_Cenario.py             # Capítulo 1 — contexto dos dados
│   ├── 2_💰_O_Gap_Salarial.py      # Capítulo 2 — o tamanho do problema
│   ├── 3_🔍_Investigacao.py        # Capítulo 3 — descartando explicações simples
│   ├── 4_🎓_Escolaridade.py        # Capítulo 4 — a reviravolta
│   └── 5_🧭_Conclusao.py           # Capítulo 5 — síntese e limitações
├── data.py                         # Carregamento e agregações compartilhadas
├── theme.py                        # Paleta de cores e template Plotly compartilhados
├── docs/
│   ├── storytelling.md             # Arco narrativo e decisões de design
│   └── analise_graficos.md         # Análise de cada gráfico, gráfico a gráfico
└── README.md
```

O Streamlit gera a navegação por capítulos automaticamente a partir de
`dashboard/pages/` (a numeração no nome do arquivo controla a ordem).

## Testes

Cada página é validada sem precisar de navegador, via
`streamlit.testing.v1.AppTest`:

```bash
python -c "
from streamlit.testing.v1 import AppTest
import glob
for s in ['dashboard/app.py'] + sorted(glob.glob('dashboard/pages/*.py')):
    at = AppTest.from_file(s, default_timeout=60)
    at.run()
    assert not at.exception, (s, at.exception)
    print(s, 'OK')
"
```
