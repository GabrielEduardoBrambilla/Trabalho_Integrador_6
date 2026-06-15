# PM3 — Tratamento de Dados: Mercado de Trabalho na Região Sul (PNAD Contínua/IBGE)

Projeto de tratamento de dados (PM3) usando a **PNAD Contínua** (IBGE/SIDRA) como
fonte única, focado em rendimento, força de trabalho, informalidade e nível de
instrução para Paraná, Santa Catarina e Rio Grande do Sul, 2020–2025. O checklist
completo do trabalho está em [`docs/plano_pm3.md`](docs/plano_pm3.md).

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
│   └── 03_tratamento_pm3.ipynb  # Diagnóstico, EDA, limpeza, tratamento e dataset final
├── dados/
│   ├── bronze/                # JSON bruto da API SIDRA (preservado, versionado)
│   ├── silver/                # pnad_limpo.csv (normalizado)
│   └── gold/                  # pnad_tratado_final.csv (dataset final, versionado)
├── docs/
│   ├── plano_pm3.md           # Checklist do PM3 (mapeado para context.md 6.1-6.17)
│   ├── relatorio_final.md     # Relatório final (estrutura de 23 itens, context.md 6.8)
│   ├── catalogo_dados.md       # Catálogo de colunas do dataset final
│   └── context.md             # Enunciado/requisitos do PM3
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
   agregação, normalização, discretização e feature engineering, gerando
   `dados/gold/pnad_tratado_final.csv`.

Pré-requisitos: Python 3.12+, dependências em `requirements.txt`
(`pip install -r requirements.txt`).

## Entregáveis do PM3

- Dados brutos: `dados/bronze/pnad_*.json`
- Dataset final tratado: `dados/gold/pnad_tratado_final.csv`
- Notebook de tratamento: `notebooks/03_tratamento_pm3.ipynb`
- Relatório final: `docs/relatorio_final.md`
- Catálogo de dados: `docs/catalogo_dados.md`
- Checklist/plano: `docs/plano_pm3.md`
