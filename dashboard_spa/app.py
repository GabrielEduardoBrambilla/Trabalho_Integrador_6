"""Dashboard PM3 — Gap salarial no mercado de trabalho da Região Sul (PNAD Contínua/IBGE).

Single-page app. Lógica de agregação em `data.py`, identidade visual em
`theme.py`. Racional de cada gráfico e do design em `dashboard/docs/`.
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from data import (
    build_indicator_wide,
    correlacao_indicadores,
    educacao_sem_total,
    educacao_share_por_sexo,
    gap_by_uf,
    gap_geral,
    load_data,
    NIVEIS_INSTRUCAO,
    normalized_profile_by_sexo,
    periodo_sort_key,
    rendimento_df,
    rendimento_medio_por_sexo,
)
from theme import COLOR_SEXO, COLOR_UF, style

st.set_page_config(page_title="Gap Salarial — Região Sul", page_icon="📊", layout="wide")

df_gap_raw, df_contexto_raw = load_data()

# --------------------------------------------------------------------------- #
# Sidebar — filtros globais
# --------------------------------------------------------------------------- #
st.sidebar.header("Filtros")
ufs = sorted(df_gap_raw["uf_nome"].unique())
uf_sel = st.sidebar.multiselect("UF", ufs, default=ufs)

anos = sorted(df_gap_raw["ano"].unique())
ano_sel = st.sidebar.select_slider("Período (ano)", options=anos, value=(anos[0], anos[-1]))

st.sidebar.divider()
st.sidebar.caption(
    "**Fonte:** PNAD Contínua/IBGE via API SIDRA.  \n"
    "**Principal:** `pnad_treated_data.csv` (4093+5436, UF×trimestre).  \n"
    "**Contexto:** `pnad_context_data.csv` (7322, Região×ano, não joinável).  \n"
    "Detalhes: `docs/relatorio_final.md` · `dashboard/docs/`."
)

if not uf_sel:
    st.warning("Selecione ao menos uma UF na barra lateral.")
    st.stop()

df_gap = df_gap_raw[df_gap_raw["uf_nome"].isin(uf_sel) & df_gap_raw["ano"].between(*ano_sel)]
df_contexto = df_contexto_raw[df_contexto_raw["ano"].between(*ano_sel)]
rend = rendimento_df(df_gap)

# --------------------------------------------------------------------------- #
# Header + KPIs
# --------------------------------------------------------------------------- #
st.title("📊 Gap Salarial — Mercado de Trabalho da Região Sul")
st.caption("PNAD Contínua/IBGE · Paraná, Santa Catarina, Rio Grande do Sul · 2020–2025")

gap_atual = gap_geral(df_gap)
rend_sexo = rendimento_medio_por_sexo(df_gap)
profile = normalized_profile_by_sexo(df_gap)

share_full = educacao_share_por_sexo(df_contexto)
if {"Feminino", "Masculino"}.issubset(share_full.columns) and not share_full.empty:
    share_sup = share_full.set_index("nivel_instrucao").loc["Superior completo"]
else:
    share_sup = pd.Series({"Feminino": float("nan"), "Masculino": float("nan")})

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Gap salarial médio", f"{gap_atual:.1f}%")
k2.metric("Rendimento — Masc.", f"R$ {rend_sexo.get('Masculino', float('nan')):,.0f}")
k3.metric("Rendimento — Fem.", f"R$ {rend_sexo.get('Feminino', float('nan')):,.0f}")
k4.metric("Correlação Ocup.×Informalidade", f"{correlacao_indicadores(df_gap).loc['Ocupação', 'Informalidade']:.2f}")
k5.metric("Superior completo, Fem. vs Masc.", f"+{share_sup['Feminino'] - share_sup['Masculino']:.1f} p.p.")

st.divider()

tab_mercado, tab_investigacao, tab_escolaridade = st.tabs(
    ["💰 Mercado de Trabalho", "🔍 Investigação", "🎓 Escolaridade"]
)

# --------------------------------------------------------------------------- #
# Tab 1 — Mercado de trabalho
# --------------------------------------------------------------------------- #
with tab_mercado:
    col1, col2 = st.columns([3, 2])

    with col1:
        rend_uf = rend.groupby(["uf_nome", "sexo"])["valor_imputado"].mean().reset_index()
        pivot = rend_uf.pivot(index="uf_nome", columns="sexo", values="valor_imputado").sort_values("Masculino")
        fig = go.Figure()
        if "Masculino" in pivot:
            fig.add_trace(go.Bar(
                y=pivot.index, x=pivot["Masculino"], orientation="h", name="Masculino",
                marker_color=COLOR_SEXO["Masculino"],
                text=[f"R$ {v:,.0f}" for v in pivot["Masculino"]], textposition="outside",
            ))
        if "Feminino" in pivot:
            fig.add_trace(go.Bar(
                y=pivot.index, x=-pivot["Feminino"], orientation="h", name="Feminino",
                marker_color=COLOR_SEXO["Feminino"],
                text=[f"R$ {v:,.0f}" for v in pivot["Feminino"]], textposition="outside",
            ))
        fig.update_layout(barmode="relative", title="Rendimento médio por sexo e UF", xaxis_title=None, xaxis_showticklabels=False)
        st.plotly_chart(style(fig, height=300), width="stretch")

    with col2:
        gap_uf = gap_by_uf(df_gap)
        fig = go.Figure(go.Bar(
            x=gap_uf["gap_salarial_pct"], y=gap_uf["uf_nome"], orientation="h",
            marker_color=[COLOR_UF.get(u, "#868E96") for u in gap_uf["uf_nome"]],
            text=[f"{v:.1f}%" for v in gap_uf["gap_salarial_pct"]], textposition="outside",
        ))
        fig.update_layout(title="Gap salarial médio por UF", xaxis_title="%")
        st.plotly_chart(style(fig, height=300), width="stretch")

    df_evol = (
        rend.dropna(subset=["gap_salarial_pct"])
        .drop_duplicates(subset=["uf_nome", "periodo_label"])
        .sort_values(["ano", "trimestre"])
    )
    fig = px.line(
        df_evol, x="periodo_label", y="gap_salarial_pct", color="uf_nome", markers=True,
        color_discrete_map=COLOR_UF, category_orders={"periodo_label": periodo_sort_key(rend)},
        title="Evolução trimestral do gap salarial",
        labels={"periodo_label": "Trimestre", "gap_salarial_pct": "Gap (%)", "uf_nome": "UF"},
    )
    fig.add_vrect(x0="2020-T2", x1="2022-T1", fillcolor="#E9ECEF", opacity=0.6, line_width=0,
                  annotation_text="sem dado (lacuna IBGE)", annotation_position="top left", annotation_font_size=10)
    fig.update_yaxes(rangemode="tozero")
    st.plotly_chart(style(fig, height=340), width="stretch")
    st.caption("Faixa cinza = trimestres sem dado de rendimento na tabela 5436 (lacuna real de divulgação do IBGE, 2020T2–2022T1).")

    df_box = rend.dropna(subset=["valor"])
    fig = px.box(
        df_box, x="uf_nome", y="valor", color="sexo", color_discrete_map=COLOR_SEXO,
        title="Distribuição do rendimento por UF e sexo",
        labels={"uf_nome": "UF", "valor": "Rendimento (R$)", "sexo": "Sexo"},
    )
    fig.add_hline(
        y=df_box["valor"].median(), line_dash="dash", line_color="red",
        annotation_text="Mediana geral", annotation_position="top left",
    )
    st.plotly_chart(style(fig, height=340), width="stretch")
    st.caption(
        "A tabela 5436 do SIDRA/IBGE já é o rendimento médio mensal real calculado "
        "pelo IBGE por sexo/UF/trimestre, e não os rendimentos individuais dos "
        "respondentes da PNAD Contínua — cada ponto do boxplot é uma média sobre "
        "milhares de pessoas entrevistadas naquele trimestre/UF/sexo, por isso não "
        "há outliers individuais."
    )

# --------------------------------------------------------------------------- #
# Tab 2 — Investigação
# --------------------------------------------------------------------------- #
with tab_investigacao:
    col1, col2 = st.columns([2, 3])

    with col1:
        corr = correlacao_indicadores(df_gap)
        fig = px.imshow(
            corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
            title="Correlação entre indicadores", labels={"color": "ρ"},
        )
        st.plotly_chart(style(fig, height=380), width="stretch")

    with col2:
        categorias = ["Ocupação", "Informalidade", "Rendimento"]
        fig = go.Figure()
        for sexo in ["Feminino", "Masculino"]:
            sub = profile[profile["sexo"] == sexo].set_index("indicador")
            if not set(categorias).issubset(sub.index):
                continue
            vals = sub.loc[categorias, "valor_normalizado"]
            fig.add_trace(go.Scatterpolar(
                r=list(vals) + [vals.iloc[0]], theta=categorias + [categorias[0]],
                fill="toself", name=sexo, line_color=COLOR_SEXO[sexo], opacity=0.75,
            ))
        fig.update_layout(title="Perfil normalizado por sexo", polar=dict(radialaxis=dict(range=[0, 1])))
        st.plotly_chart(style(fig, height=380), width="stretch")

    st.caption(
        "Ocupação e informalidade têm correlação forte entre si; o rendimento é o indicador mais "
        "independente dos dois — e é justamente onde o afastamento entre os polígonos do radar é maior."
    )

    wide = build_indicator_wide(df_gap).dropna(subset=["Rendimento", "Informalidade", "Ocupação"])
    fig = px.scatter(
        wide, x="Rendimento", y="Informalidade", size="Ocupação", color="sexo",
        facet_col="uf_nome", animation_frame="periodo_label",
        color_discrete_map=COLOR_SEXO, size_max=35,
        category_orders={"periodo_label": periodo_sort_key(wide), "uf_nome": [u for u in COLOR_UF if u in uf_sel]},
        range_x=[wide["Rendimento"].min() * 0.9, wide["Rendimento"].max() * 1.1],
        range_y=[0, wide["Informalidade"].max() * 1.15],
        title="Rendimento × Informalidade × Ocupação, por trimestre",
        labels={"Rendimento": "Rendimento médio (R$)", "Informalidade": "Informalidade (%)"},
    )
    fig.update_layout(height=440)
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "Os quadros saltam de 2020-T1 para 2022-T2 porque a tabela 5436 (rendimento) não "
        "retornou dados para 2020T2–2022T1 — sem rendimento, a linha some do gráfico nesses "
        "8 trimestres (lacuna real de divulgação do IBGE, não um erro deste dashboard)."
    )

# --------------------------------------------------------------------------- #
# Tab 3 — Escolaridade (dataset de contexto — não joinável ao principal)
# --------------------------------------------------------------------------- #
with tab_escolaridade:
    st.caption(
        "Dataset de contexto (`pnad_context_data.csv`, tabela 7322) — Região Sul, anual, "
        "não cruzado por UF/trimestre com o dataset principal."
    )

    sup = educacao_sem_total(df_contexto)
    if sup.empty:
        st.info("Sem dados de escolaridade no período selecionado.")
    else:
        sup_media = sup[sup["nivel_instrucao"] == "Superior completo"].groupby("sexo")["valor_imputado"].mean()
        c1, c2, c3 = st.columns(3)
        c1.metric("Superior completo — Fem.", f"{sup_media.get('Feminino', 0):,.0f} mil", f"{share_sup['Feminino']:.1f}% das mulheres")
        c2.metric("Superior completo — Masc.", f"{sup_media.get('Masculino', 0):,.0f} mil", f"{share_sup['Masculino']:.1f}% dos homens")
        c3.metric("Diferença a favor das mulheres", f"+{share_sup['Feminino'] - share_sup['Masculino']:.1f} p.p.")

        col1, col2 = st.columns(2)
        with col1:
            share = educacao_share_por_sexo(df_contexto)
            fig = go.Figure()
            for sexo in ["Feminino", "Masculino"]:
                if sexo not in share.columns:
                    continue
                vals = share[sexo].tolist()
                fig.add_trace(go.Scatterpolar(
                    r=vals + [vals[0]], theta=NIVEIS_INSTRUCAO + [NIVEIS_INSTRUCAO[0]],
                    fill="toself", name=sexo, line_color=COLOR_SEXO[sexo], opacity=0.75,
                ))
            fig.update_layout(title="Distribuição educacional por sexo (% do total)")
            st.plotly_chart(style(fig, height=420), width="stretch")

        with col2:
            media = sup.groupby(["nivel_instrucao", "sexo"])["valor_imputado"].mean().reset_index()
            fig = px.bar(
                media, x="nivel_instrucao", y="valor_imputado", color="sexo", barmode="group",
                color_discrete_map=COLOR_SEXO, category_orders={"nivel_instrucao": NIVEIS_INSTRUCAO},
                title="População por nível de instrução (mil pessoas)",
                labels={"nivel_instrucao": "Nível", "valor_imputado": "Mil pessoas", "sexo": "Sexo"},
            )
            fig.update_xaxes(tickangle=20)
            st.plotly_chart(style(fig, height=420), width="stretch")

        st.caption(
            "Mulheres concentram vantagem proporcional em 'Superior completo' — o nível mais "
            "associado a maior rendimento — mesmo ganhando, em média, menos que os homens."
        )
