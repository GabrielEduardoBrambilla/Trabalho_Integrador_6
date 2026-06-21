"""Identidade visual compartilhada por todas as páginas do dashboard.

Centralizar cores aqui garante que o mesmo conceito (ex.: "Feminino") tenha
sempre a mesma cor em qualquer gráfico do dashboard — um dos princípios
básicos de storytelling com dados (codificação visual consistente).
Ver dashboard/docs/storytelling.md, seção "Identidade visual".
"""

import plotly.graph_objects as go
import plotly.io as pio

COLOR_SEXO = {
    "Feminino": "#D6336C",
    "Masculino": "#2C6E9B",
}

COLOR_UF = {
    "Paraná": "#2A9D8F",
    "Santa Catarina": "#E76F51",
    "Rio Grande do Sul": "#8338EC",
}

COLOR_FAIXA = {
    "baixo": "#F4A261",
    "médio": "#E9C46A",
    "alto": "#2A9D8F",
}

TEXT_COLOR = "#343A40"
GRID_COLOR = "#E9ECEF"
ACCENT = "#D6336C"

_template = go.layout.Template()
_template.layout = go.Layout(
    font=dict(family="Source Sans Pro, Segoe UI, Arial", color=TEXT_COLOR, size=13),
    title_font=dict(size=18, color=TEXT_COLOR),
    paper_bgcolor="white",
    plot_bgcolor="white",
    xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
    yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    margin=dict(t=60, l=10, r=10, b=10),
    colorway=[COLOR_SEXO["Feminino"], COLOR_SEXO["Masculino"], *COLOR_UF.values()],
)
pio.templates["pm3_gap"] = _template
pio.templates.default = "pm3_gap"


def style(fig: go.Figure, height: int = 420) -> go.Figure:
    """Aplica altura padrão e remove espaços desnecessários."""
    fig.update_layout(height=height)
    return fig
