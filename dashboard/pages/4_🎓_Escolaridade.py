"""Capítulo 4 — Escolaridade: a revelação da história."""

import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data import NIVEIS_INSTRUCAO, educacao_sem_total, educacao_share_por_sexo, load_data
from theme import COLOR_SEXO, style

st.set_page_config(page_title="Escolaridade", page_icon="🎓", layout="wide")

_, df_contexto = load_data()

st.title("🎓 Escolaridade")
st.markdown(
    """
Este capítulo usa o dataset de **contexto** (`pnad_context_data.csv`, tabela SIDRA
7322) — nível de instrução por sexo, Região Sul, anual. **Ele não compartilha UF
nem trimestre com o dataset principal** (ver capítulo "📖 Cenário"), então os
números aqui não são cruzados linha a linha com o gap salarial — são comparados
lado a lado, como evidência independente.
"""
)

ctx = educacao_sem_total(df_contexto)

st.subheader("Quem tem qual nível de instrução, por sexo")
media = ctx.groupby(["nivel_instrucao", "sexo"])["valor_imputado"].mean().reset_index()
fig = px.bar(
    media, x="nivel_instrucao", y="valor_imputado", color="sexo", barmode="group",
    color_discrete_map=COLOR_SEXO,
    category_orders={"nivel_instrucao": NIVEIS_INSTRUCAO},
    labels={"nivel_instrucao": "Nível de instrução", "valor_imputado": "População (mil pessoas)", "sexo": "Sexo"},
)
fig.update_xaxes(tickangle=20)
st.plotly_chart(style(fig), width="stretch")

col1, col2 = st.columns(2)

with col1:
    st.subheader("A forma da distribuição educacional")
    share = educacao_share_por_sexo(df_contexto)
    fig = go.Figure()
    for sexo in ["Feminino", "Masculino"]:
        vals = share[sexo].tolist()
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=NIVEIS_INSTRUCAO + [NIVEIS_INSTRUCAO[0]],
            fill="toself", name=sexo, line_color=COLOR_SEXO[sexo], opacity=0.75,
        ))
    eixo_max = max(share["Feminino"].max(), share["Masculino"].max()) * 1.15
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, eixo_max])))
    st.plotly_chart(style(fig, height=440), width="stretch")
    st.caption(
        "% da população de cada sexo em cada nível (soma 100% por sexo) — assim, o "
        "gráfico compara a *forma* da distribuição, não o tamanho da população. O "
        "polígono feminino se estica mais no eixo 'Superior completo'; o masculino, "
        "ligeiramente mais nos níveis intermediários."
    )

with col2:
    st.subheader("Da população total a cada nível")
    fig = px.sunburst(
        media, path=["sexo", "nivel_instrucao"], values="valor_imputado",
        color="sexo", color_discrete_map=COLOR_SEXO,
    )
    st.plotly_chart(style(fig, height=440), width="stretch")
    st.caption(
        "Mesma informação do gráfico de barras, em formato hierárquico: o anel "
        "interno é o sexo, o externo é o nível de instrução, e o tamanho de cada "
        "fatia é proporcional à população (mil pessoas)."
    )

sup = ctx[ctx["nivel_instrucao"] == "Superior completo"].groupby("sexo")["valor_imputado"].mean()
share_sup = educacao_share_por_sexo(df_contexto).set_index("nivel_instrucao").loc["Superior completo"]

st.subheader("O número que não devia existir, se a educação explicasse o gap")
col1, col2, col3 = st.columns(3)
col1.metric("Mulheres com Superior completo", f"{sup['Feminino']:,.0f} mil", f"{share_sup['Feminino']:.1f}% das mulheres")
col2.metric("Homens com Superior completo", f"{sup['Masculino']:,.0f} mil", f"{share_sup['Masculino']:.1f}% dos homens")
col3.metric("Diferença a favor das mulheres", f"+{sup['Feminino'] - sup['Masculino']:,.0f} mil", f"+{share_sup['Feminino'] - share_sup['Masculino']:.1f} p.p.")

st.warning(
    "**A revelação:** mulheres da Região Sul têm, em proporção, **mais formação "
    "superior completa** que homens — exatamente o nível associado às melhores "
    "remunerações. Mesmo assim, como visto no capítulo \"💰 O Gap Salarial\", elas "
    "ganham em média ~32% menos. A educação não apenas não explica o gap: ela torna "
    "o gap mais difícil de justificar por diferenças de qualificação."
)
