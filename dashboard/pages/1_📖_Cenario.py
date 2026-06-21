"""Capítulo 1 — Cenário: quem, onde, quando (ver docs/storytelling.md)."""

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data import load_data, rendimento_df
from theme import COLOR_UF, style

st.set_page_config(page_title="Cenário — Gap Salarial", page_icon="📖", layout="wide")

df_gap, df_contexto = load_data()

st.title("📖 Cenário")
st.markdown(
    """
A **PNAD Contínua** (Pesquisa Nacional por Amostra de Domicílios Contínua) é a
principal pesquisa do IBGE sobre o mercado de trabalho brasileiro, divulgada
trimestralmente. Este dashboard usa três tabelas da API SIDRA, recortadas para
**Paraná, Santa Catarina e Rio Grande do Sul**, entre **2020 e 2025**:

- **Força de trabalho e informalidade** (tabela 4093) e **rendimento médio**
  (tabela 5436) — trimestrais, pessoas de 14+ anos, por UF. Formam o dataset
  **principal** (`pnad_treated_data.csv`), base dos capítulos "O Gap Salarial" e
  "Investigação".
- **Nível de instrução por sexo** (tabela 7322) — anual, pessoas de 10+ anos,
  só no nível Região Sul (não por UF). Forma o dataset de **contexto**
  (`pnad_context_data.csv`), base do capítulo "Escolaridade".

> **Por que dois datasets, e não um só?** A tabela de escolaridade não existe por UF
> no SIDRA (só agregada para a Região Sul) e é divulgada anualmente, não
> trimestralmente — ela não pode ser cruzada linha a linha com as outras duas sem
> perder precisão. Em vez de forçar essa junção, o tratamento de dados manteve os
> dois datasets separados (ver `docs/relatorio_final.md`, seção 22). Por isso, no
> resto deste dashboard, eles aparecem em capítulos distintos.
"""
)

st.subheader("Tamanho do mercado de trabalho, por UF")

rend = rendimento_df(df_gap)
ocup = df_gap[df_gap["variavel_nome"].str.contains("ocupadas na semana", case=False, na=False)
              & ~df_gap["variavel_nome"].str.contains("informalidade", case=False, na=False)]

treemap_df = (
    ocup.groupby(["uf_nome", "sexo"])["valor_imputado"]
    .mean()
    .reset_index()
    .rename(columns={"valor_imputado": "ocupados_mil"})
)
fig = px.treemap(
    treemap_df,
    path=["uf_nome", "sexo"],
    values="ocupados_mil",
    color="uf_nome",
    color_discrete_map=COLOR_UF,
    custom_data=["ocupados_mil"],
)
fig.update_traces(texttemplate="%{label}<br>%{customdata[0]:,.0f} mil pessoas")
st.plotly_chart(style(fig, height=420), width="stretch")
st.caption(
    "Tamanho do retângulo = média de pessoas ocupadas (mil), 2020–2025. Mostra a "
    "escala relativa de cada UF e a proporção homens/mulheres ocupados dentro de "
    "cada uma — útil para calibrar a leitura dos gráficos de gap salarial: "
    "diferenças percentuais nos próximos capítulos não são por causa do tamanho do "
    "mercado de cada estado."
)

col1, col2, col3 = st.columns(3)
col1.metric("Linhas — dataset principal", f"{len(df_gap):,}")
col2.metric("Linhas — dataset de contexto", f"{len(df_contexto):,}")
col3.metric("Trimestres com dado de rendimento", f"{rend['periodo_label'].nunique()} / 24")

st.caption(
    "16 dos 24 trimestres esperados (2020T1–2025T4) têm dado de rendimento — a "
    "tabela 5436 não retorna valores para 2020T2–2022T1, um buraco real na "
    "divulgação do IBGE durante a pandemia (ver capítulo seguinte e "
    "`docs/relatorio_final.md`, Problema 9)."
)
