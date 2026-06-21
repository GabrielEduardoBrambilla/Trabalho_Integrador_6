"""Capa do dashboard — o "gancho" da história (ver dashboard/docs/storytelling.md)."""

import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from data import gap_by_uf, gap_geral, load_data, rendimento_medio_por_sexo
from theme import COLOR_SEXO, style

st.set_page_config(
    page_title="Gap Salarial — Região Sul (PNAD Contínua)",
    page_icon="📊",
    layout="wide",
)

df_gap, df_contexto = load_data()

st.title("📊 Elas estudam mais. Elas ganham menos.")
st.markdown(
    "##### O gap salarial entre homens e mulheres no mercado de trabalho da Região Sul "
    "(PNAD Contínua/IBGE, 2020–2025)"
)

gap_atual = gap_geral(df_gap)
rend = rendimento_medio_por_sexo(df_gap)
gap_uf = gap_by_uf(df_gap)

st.markdown(
    f"""
Em **Paraná, Santa Catarina e Rio Grande do Sul**, mulheres recebem, em média,
**{gap_atual:.0f}% menos** que homens pelo mesmo tipo de trabalho — uma diferença que
se mantém estável desde 2020, em todos os três estados. E o mais intrigante: como você
verá no capítulo "🎓 Escolaridade", isso acontece **mesmo onde as mulheres têm, em
proporção, mais formação superior do que os homens**.

Este dashboard usa os dois datasets tratados no PM3 — `pnad_treated_data.csv`
(força de trabalho, informalidade e rendimento) e `pnad_context_data.csv`
(escolaridade) — para investigar essa desigualdade passo a passo. Use o menu à
esquerda para seguir os capítulos da investigação.
"""
)

st.divider()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Gap salarial médio", f"{gap_atual:.1f}%", help="(Rendimento Masc. − Fem.) / Fem. × 100, média 2020–2025")
col2.metric("Rendimento médio — Masculino", f"R$ {rend['Masculino']:,.0f}")
col3.metric("Rendimento médio — Feminino", f"R$ {rend['Feminino']:,.0f}")
col4.metric("UFs analisadas", "3", help="Paraná, Santa Catarina, Rio Grande do Sul")

st.subheader("O tamanho do gap, hoje, em cada estado")

fig = go.Figure()
for _, row in gap_uf.iterrows():
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=row["gap_salarial_pct"],
            title={"text": row["uf_nome"], "font": {"size": 16}},
            number={"suffix": "%", "font": {"size": 28}},
            gauge={
                "axis": {"range": [0, 45]},
                "bar": {"color": COLOR_SEXO["Feminino"]},
                "steps": [
                    {"range": [0, 15], "color": "#F1F3F5"},
                    {"range": [15, 30], "color": "#FFE3EC"},
                    {"range": [30, 45], "color": "#FFC2D7"},
                ],
            },
            domain={"row": 0, "column": list(gap_uf["uf_nome"]).index(row["uf_nome"])},
        )
    )
fig.update_layout(grid={"rows": 1, "columns": 3, "pattern": "independent"})
st.plotly_chart(style(fig, height=260), width="stretch")

st.caption(
    "Gap salarial percentual médio de todo o período disponível (2020–2025), por UF. "
    "Quanto mais à direita o ponteiro, maior a diferença entre o rendimento médio "
    "masculino e feminino. Continue para **📖 Cenário** para entender a base de dados, "
    "ou vá direto para **💰 O Gap Salarial** para a investigação."
)
