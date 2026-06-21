"""Capítulo 5 — Conclusão: o que a investigação descartou, e o que sobrou."""

import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data import gap_geral, load_data
from theme import COLOR_SEXO, style

st.set_page_config(page_title="Conclusão", page_icon="🧭", layout="wide")

df_gap, _ = load_data()
gap_atual = gap_geral(df_gap)

st.title("🧭 Conclusão")
st.markdown("### O que foi testado, e o que não explica o gap")

hipoteses = [
    ("Diferença de ocupação (quantas pessoas trabalham)", "Não explica", "Homens e mulheres seguem a mesma tendência de ocupação ao longo do tempo; a folga entre os sexos nesse eixo é bem menor que no rendimento (capítulo Investigação)."),
    ("Diferença de informalidade", "Não explica", "Correlação fraca com rendimento (≈0,07); ocupação e informalidade se movem juntas, rendimento não."),
    ("Diferença de escolaridade", "Piora a pergunta", "Mulheres têm proporcionalmente mais Superior completo que homens — o oposto do que explicaria um rendimento menor (capítulo Escolaridade)."),
    ("Persistência ao longo do tempo / pandemia", "Confirma, não explica", "O gap oscila entre 26% e 39% em todos os trimestres com dado, nas três UFs — não é um efeito pontual da pandemia."),
]

for hipotese, status, detalhe in hipoteses:
    icon = "❌" if status == "Não explica" else ("⚠️" if status == "Piora a pergunta" else "🔁")
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        c1.markdown(f"**{hipotese}**  \n{detalhe}")
        c2.markdown(f"### {icon} {status}")

st.divider()

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown(
        f"""
### O que sobra

Depois de descartar ocupação, informalidade e escolaridade como explicações, o gap
salarial médio de **{gap_atual:.0f}%** entre homens e mulheres na Região Sul
permanece **sem explicação nos dados disponíveis** — o que é consistente com a
literatura sobre desigualdade de gênero no mercado de trabalho, que aponta fatores
não capturados nesta base, como segregação ocupacional (tipos de cargo/setor),
diferença em horas trabalhadas, descontinuidade de carreira por maternidade, e
discriminação direta ou indireta na remuneração.

**Isso não prova causalidade** — esta é uma análise exploratória sobre dados
agregados, não um estudo causal sobre indivíduos. Mas o padrão é forte, persistente
e vai na direção contrária ao que as hipóteses mais simples preveem.

### Limitações e próximos passos

Detalhados em `docs/relatorio_final.md` (seções 22–23): a lacuna de dados da
tabela 5436 durante a pandemia, a diferença de granularidade entre os dois
datasets, e a sugestão de usar microdados da PNAD Contínua para cruzar
escolaridade × UF × idade 14+ de forma realmente comparável ao dataset principal.
"""
    )

with col2:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=gap_atual,
        number={"suffix": "%", "font": {"size": 36}},
        title={"text": "Gap salarial médio<br>Região Sul, 2020–2025"},
        gauge={
            "axis": {"range": [0, 45]},
            "bar": {"color": COLOR_SEXO["Feminino"]},
            "steps": [
                {"range": [0, 15], "color": "#F1F3F5"},
                {"range": [15, 30], "color": "#FFE3EC"},
                {"range": [30, 45], "color": "#FFC2D7"},
            ],
        },
    ))
    st.plotly_chart(style(fig, height=320), width="stretch")
    st.caption("O mesmo número da capa — fechando o ciclo da investigação.")
