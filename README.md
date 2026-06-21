# PM3 — Tratamento de Dados: Mercado de Trabalho na Região Sul (PNAD Contínua/IBGE)

Projeto de tratamento de dados (PM3) usando a **PNAD Contínua** (IBGE/SIDRA) como
fonte única. Análise **principal**: gap salarial entre homens e mulheres (rendimento,
força de trabalho e informalidade) em Paraná, Santa Catarina e Rio Grande do Sul,
2020–2025. Análise de **contexto**: nível de instrução por sexo na Região Sul, usada
para testar a hipótese de que o gap salarial seria explicado por escolaridade. O
checklist completo do trabalho original está em [`docs/plano_pm3.md`](docs/plano_pm3.md);
a mudança de foco para gap salarial + dois datasets finais está documentada em
[`docs/plano_refoco_gap_salarial.md`](docs/plano_refoco_gap_salarial.md).

## Estrutura do projeto

```
mensal_3/
├── coleta/
│   └── coletar_pnad.py        # PnadCollector — busca tabelas SIDRA 4093, 5436, 7322
├── silver/
│   └── normalizar_pnad.py     # PnadNormalizer — JSON SIDRA -> CSV limpo e tipado
├── notebooks/
│   ├── 01_coleta.ipynb        # Executa o PnadCollector -> dados/bronze/pnad_*.json
│   ├── 02_silver.ipynb        # Executa o PnadNormalizer -> dados/silver/pnad_limpo.csv
│   └── 03_tratamento_pm3.ipynb  # Diagnóstico, EDA, limpeza, tratamento e datasets finais
├── dados/
│   ├── bronze/                # JSON bruto da API SIDRA (preservado, versionado)
│   ├── silver/                # pnad_limpo.csv (normalizado)
│   └── gold/                  # pnad_treated_data.csv (principal) + pnad_context_data.csv (contexto)
├── dashboard/                  # Dashboard Streamlit single-page (extensão de BI, não obrigatória no PM3)
│   ├── app.py                  # Filtros + KPIs + 3 abas (Mercado de Trabalho/Investigação/Escolaridade)
│   └── docs/                   # storytelling.md + analise_graficos.md
├── docs/
│   ├── plano_pm3.md                    # Checklist original do PM3 (context.md 6.1-6.17)
│   ├── plano_refoco_gap_salarial.md    # Plano da mudança de foco + split em 2 gold outputs
│   ├── relatorio_final.md              # Relatório final (estrutura de 23 itens, context.md 6.8)
│   ├── catalogo_dados.md               # Catálogo de colunas do dataset principal
│   ├── catalogo_dados_contexto.md      # Catálogo de colunas do dataset de contexto
│   └── context.md                      # Enunciado/requisitos do PM3
└── config.py                  # Configuração centralizada (lê .env)
```

## Como rodar o pipeline

1. **Coleta (Bronze):** `notebooks/01_coleta.ipynb` — busca as tabelas SIDRA 4093
   (força de trabalho/informalidade), 5436 (rendimento médio) e 7322 (rendimento por
   nível de instrução) para PR/SC/RS, 2020–2025, e salva o JSON bruto em
   `dados/bronze/pnad_*.json`.
2. **Normalização (Silver):** `notebooks/02_silver.ipynb` — executa o
   `PnadNormalizer`, gerando `dados/silver/pnad_limpo.csv` (tipos corretos, códigos
   de ausência do IBGE convertidos para `NaN`).
3. **Tratamento (Gold):** `notebooks/03_tratamento_pm3.ipynb` — diagnóstico de
   qualidade, EDA, seleção, limpeza, tratamento de ausentes/outliers, transformação,
   agregação, normalização, discretização e feature engineering, gerando dois
   datasets finais: `dados/gold/pnad_treated_data.csv` (principal, gap salarial) e
   `dados/gold/pnad_context_data.csv` (contexto, escolaridade por sexo).

> No Windows, execute o notebook com a variável de ambiente `PYTHONUTF8=1` definida
> (`locale.getpreferredencoding()` neste tipo de ambiente costuma retornar `cp1252`,
> o que corrompe acentuação ao salvar o `.ipynb` via `jupyter execute`).

4. **Dashboard (opcional):** `streamlit run dashboard/app.py` — consome os dois
   datasets finais para uma investigação visual guiada do gap salarial. Ver
   [`dashboard/README.md`](dashboard/README.md) e
   [`dashboard/docs/storytelling.md`](dashboard/docs/storytelling.md).

Pré-requisitos: Python 3.12+, dependências em `requirements.txt`
(`pip install -r requirements.txt`).

## Entregáveis do PM3

- Dados brutos: `dados/bronze/pnad_*.json`
- Dataset final principal (gap salarial): `dados/gold/pnad_treated_data.csv`
- Dataset final de contexto (escolaridade): `dados/gold/pnad_context_data.csv`
- Notebook de tratamento: `notebooks/03_tratamento_pm3.ipynb`
- Relatório final: `docs/relatorio_final.md`
- Catálogo de dados: `docs/catalogo_dados.md` (principal) e
  `docs/catalogo_dados_contexto.md` (contexto)
- Checklist/plano: `docs/plano_pm3.md` e `docs/plano_refoco_gap_salarial.md`
