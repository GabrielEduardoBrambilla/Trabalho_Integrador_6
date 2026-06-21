"""Capítulo 3 — Investigação: será que dá pra explicar o gap por outro motivo?"""

import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data import build_indicator_wide, correlacao_indicadores, linear_trend, load_data, normalized_profile_by_sexo
from theme import COLOR_SEXO, style

st.set_page_config(page_title="Investigação", page_icon="🔍", layout="wide")

df_gap, _ = load_data()

st.title("🔍 Investigação")
st.markdown(
    """
Antes de concluir que o gap salarial é estrutural, vale eliminar explicações mais
simples: será que homens e mulheres simplesmente **trabalham em proporções
diferentes**, ou estão **diferentemente expostos à informalidade** — e isso, não
o sexo em si, explicaria o rendimento menor?
"""
)

st.subheader("Como os três indicadores se relacionam entre si")
corr = correlacao_indicadores(df_gap)
fig = px.imshow(
    corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
    labels={"color": "Correlação"},
)
st.plotly_chart(style(fig, height=380), width="stretch")
st.caption(
    "Correlação de Pearson entre os três indicadores do dataset principal, por "
    "UF/trimestre/sexo. `Ocupação` e `Informalidade` têm correlação forte "
    f"({corr.loc['Ocupação','Informalidade']:.2f}) — quando mais gente está "
    "ocupada, a taxa de informalidade tende a subir também (provável reflexo da "
    "recuperação pós-pandemia). Já `Rendimento` tem correlação fraca com os outros "
    "dois — o nível de rendimento não parece se mover junto com ocupação ou "
    "informalidade, o que já é um indício de que o gap salarial não se explica por "
    "essas duas variáveis."
)

st.subheader("O perfil de homens e mulheres, em uma única imagem")
profile = normalized_profile_by_sexo(df_gap)
categorias = ["Ocupação", "Informalidade", "Rendimento"]

fig = go.Figure()
for sexo in ["Feminino", "Masculino"]:
    vals = profile[profile["sexo"] == sexo].set_index("indicador").loc[categorias, "valor_normalizado"]
    fig.add_trace(go.Scatterpolar(
        r=list(vals) + [vals.iloc[0]],
        theta=categorias + [categorias[0]],
        fill="toself",
        name=sexo,
        line_color=COLOR_SEXO[sexo],
        opacity=0.75,
    ))
fig.update_layout(polar=dict(radialaxis=dict(range=[0, 1], showticklabels=True)))
st.plotly_chart(style(fig, height=460), width="stretch")
st.caption(
    "**Como ler:** cada eixo é um indicador normalizado entre 0 e 1 (para poder "
    "comparar mil pessoas, % e R$ na mesma escala). O polígono masculino (azul) é "
    "maior nos três eixos — homens têm mais pessoas ocupadas em números absolutos "
    "e informalidade ligeiramente maior — **mas o eixo onde a diferença mais se "
    "abre é justamente `Rendimento`**, desproporcional às diferenças nos outros "
    "dois eixos. Se ocupação e informalidade explicassem o gap salarial, o "
    "afastamento entre os dois polígonos seria parecido nos três eixos — não é o "
    "que se vê aqui."
)

st.subheader("Ocupação x Informalidade: a correlação, em detalhe")
wide = build_indicator_wide(df_gap).dropna(subset=["Ocupação", "Informalidade"])
fig = px.scatter(
    wide, x="Ocupação", y="Informalidade", color="sexo", color_discrete_map=COLOR_SEXO,
    labels={"Ocupação": "Pessoas ocupadas (mil)", "Informalidade": "Taxa de informalidade (%)"},
    opacity=0.7,
)
x_line, y_line = linear_trend(wide["Ocupação"], wide["Informalidade"])
fig.add_trace(go.Scatter(x=x_line, y=y_line, mode="lines", name="tendência", line=dict(color="#495057", dash="dash")))
st.plotly_chart(style(fig), width="stretch")
st.caption(
    "Cada ponto é uma combinação UF/trimestre/sexo. A linha de tendência confirma a "
    "correlação positiva do heatmap acima — mas note que os pontos femininos (rosa) "
    "e masculinos (azul) seguem a *mesma* tendência geral, só deslocados pela "
    "diferença de escala populacional. Isso reforça que ocupação/informalidade não "
    "diferenciam estruturalmente os sexos do jeito que o rendimento diferencia."
)

st.info(
    "**Conclusão deste capítulo:** ocupação e informalidade não parecem explicar o "
    "gap salarial. Resta testar a hipótese mais citada no senso comum — "
    "escolaridade. Siga para o capítulo **🎓 Escolaridade**."
)
