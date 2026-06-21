"""Capítulo 2 — O Gap Salarial: a tensão central da história."""

import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data import build_indicator_wide, periodo_sort_key, rendimento_df
from data import load_data
from theme import COLOR_SEXO, COLOR_UF, style

st.set_page_config(page_title="O Gap Salarial", page_icon="💰", layout="wide")

df_gap, _ = load_data()
rend = rendimento_df(df_gap)

st.title("💰 O Gap Salarial")
st.markdown(
    "Homens recebem mais que mulheres nos três estados, em todos os trimestres "
    "disponíveis, sem exceção. Os gráficos abaixo mostram o tamanho dessa diferença "
    "e como ela evoluiu."
)

st.subheader("Rendimento médio por sexo, lado a lado")
rend_uf = rend.groupby(["uf_nome", "sexo"])["valor_imputado"].mean().reset_index()
pivot = rend_uf.pivot(index="uf_nome", columns="sexo", values="valor_imputado").sort_values("Masculino")

fig = go.Figure()
fig.add_trace(go.Bar(
    y=pivot.index, x=pivot["Masculino"], orientation="h", name="Masculino",
    marker_color=COLOR_SEXO["Masculino"],
    text=[f"R$ {v:,.0f}" for v in pivot["Masculino"]], textposition="outside",
))
fig.add_trace(go.Bar(
    y=pivot.index, x=-pivot["Feminino"], orientation="h", name="Feminino",
    marker_color=COLOR_SEXO["Feminino"],
    text=[f"R$ {v:,.0f}" for v in pivot["Feminino"]], textposition="outside",
))
max_val = max(pivot["Masculino"].max(), pivot["Feminino"].max())
step = 1000
ticks = list(range(0, int(max_val) + step, step))
tickvals = [-t for t in reversed(ticks)] + ticks[1:]
ticktext = [str(t) for t in reversed(ticks)] + [str(t) for t in ticks[1:]]
fig.update_layout(barmode="relative", xaxis_title="← Feminino     |     Masculino →")
fig.update_xaxes(tickvals=tickvals, ticktext=ticktext)
st.plotly_chart(style(fig, height=320), width="stretch")
st.caption(
    "Gráfico tipo 'borboleta': barras saindo de um eixo central em direções opostas "
    "deixam visualmente óbvio o tamanho do desnível entre os dois lados — aqui, o "
    "rendimento médio (R$) de cada sexo, por UF, média 2020–2025."
)

st.subheader("Evolução trimestral do gap salarial")
df_evol = (
    rend.dropna(subset=["gap_salarial_pct"])
    .drop_duplicates(subset=["uf_nome", "periodo_label"])
    .sort_values(["ano", "trimestre"])
)
fig = px.line(
    df_evol, x="periodo_label", y="gap_salarial_pct", color="uf_nome",
    markers=True, color_discrete_map=COLOR_UF,
    category_orders={"periodo_label": periodo_sort_key(rend)},
    labels={"periodo_label": "Trimestre", "gap_salarial_pct": "Gap salarial (%)", "uf_nome": "UF"},
)
fig.add_vrect(
    x0="2020-T2", x1="2022-T1", fillcolor="#E9ECEF", opacity=0.6, line_width=0,
    annotation_text="sem dado de rendimento<br>(lacuna de divulgação do IBGE)",
    annotation_position="top left", annotation_font_size=11,
)
fig.update_yaxes(rangemode="tozero")
st.plotly_chart(style(fig), width="stretch")
st.caption(
    "A faixa cinza marca os 8 trimestres em que a tabela 5436 simplesmente não "
    "retornou dados (Problema 9, `docs/relatorio_final.md`) — não é um erro deste "
    "dashboard. Fora dela, o gap oscila entre ~26% e ~39%, sem tendência clara de "
    "fechamento."
)

st.subheader("Rendimento × Informalidade × Ocupação, trimestre a trimestre")
wide = build_indicator_wide(df_gap).dropna(subset=["Rendimento", "Informalidade", "Ocupação"])
fig = px.scatter(
    wide, x="Rendimento", y="Informalidade", size="Ocupação", color="sexo",
    facet_col="uf_nome", animation_frame="periodo_label",
    color_discrete_map=COLOR_SEXO, size_max=40,
    category_orders={"periodo_label": periodo_sort_key(wide), "uf_nome": list(COLOR_UF.keys())},
    range_x=[wide["Rendimento"].min() * 0.9, wide["Rendimento"].max() * 1.1],
    range_y=[0, wide["Informalidade"].max() * 1.15],
    labels={"Rendimento": "Rendimento médio (R$)", "Informalidade": "Taxa de informalidade (%)"},
)
fig.update_layout(height=480)
st.plotly_chart(fig, width="stretch")
st.caption(
    "Clique em ▶ para animar a evolução trimestre a trimestre. Tamanho da bolha = "
    "pessoas ocupadas (mil). Mulheres (rosa) aparecem consistentemente mais à "
    "esquerda (rendimento menor) que homens (azul) — o gap não é um instante "
    "isolado, é uma posição relativa que se repete em praticamente todo trimestre "
    "disponível, nas três UFs."
)

st.subheader("Distribuição do rendimento — não é só a média")
df_rend_nonnull = rend.dropna(subset=["valor"])
fig = px.box(
    df_rend_nonnull, x="uf_nome", y="valor", color="sexo",
    color_discrete_map=COLOR_SEXO,
    labels={"uf_nome": "UF", "valor": "Rendimento (R$)", "sexo": "Sexo"},
)
st.plotly_chart(style(fig), width="stretch")
st.caption(
    "As caixas femininas ficam quase sempre abaixo das masculinas, com pouca "
    "sobreposição — o gap não é causado por alguns trimestres atípicos puxando a "
    "média; é uma diferença sistemática que aparece em praticamente toda a "
    "distribuição, não só no rendimento médio."
)
