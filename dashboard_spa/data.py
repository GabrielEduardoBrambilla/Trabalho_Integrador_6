"""Carregamento e agregação de dados para o dashboard.

Mantém a lógica de agregação em um único lugar, separada da camada de
apresentação (`app.py`) — todas as funções aceitam o dataframe já filtrado
pela sidebar, recalculando os agregados sob os filtros ativos.
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from config import config

NIVEIS_INSTRUCAO = [
    "Sem instrução",
    "Fundamental incompleto",
    "Fundamental completo",
    "Médio incompleto",
    "Médio completo",
    "Superior incompleto",
    "Superior completo",
]

ROTULOS_INDICADOR = {
    "Pessoas de 14 anos ou mais de idade ocupadas na semana de referência": "Ocupação",
    "Taxa de informalidade das pessoas de 14 anos ou mais de idade ocupadas na semana de referência": "Informalidade",
}


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    df_gap = pd.read_csv(config.gold_dir / "pnad_treated_data.csv")
    df_contexto = pd.read_csv(config.gold_dir / "pnad_context_data.csv")
    return df_gap, df_contexto


def _rendimento_label(df_gap: pd.DataFrame) -> str:
    return next(v for v in df_gap["variavel_nome"].unique() if "Rendimento" in v)


def add_indicador_curto(df_gap: pd.DataFrame) -> pd.DataFrame:
    """Adiciona uma coluna `indicador` com rótulos curtos (Ocupação/Informalidade/Rendimento)."""
    rotulos = dict(ROTULOS_INDICADOR)
    rotulos[_rendimento_label(df_gap)] = "Rendimento"
    out = df_gap.copy()
    out["indicador"] = out["variavel_nome"].map(rotulos)
    return out


def periodo_sort_key(df: pd.DataFrame) -> list[str]:
    """Lista de `periodo_label` ordenada cronologicamente (ano, trimestre)."""
    cols = ["ano", "trimestre"] if "trimestre" in df.columns else ["ano"]
    ordered = df.drop_duplicates(subset=["periodo_label"]).sort_values(cols)
    return ordered["periodo_label"].tolist()


def rendimento_df(df_gap: pd.DataFrame) -> pd.DataFrame:
    return df_gap[df_gap["tabela_id"] == 5436].copy()


def gap_by_uf(df_gap: pd.DataFrame) -> pd.DataFrame:
    """Gap salarial médio (todo o período) por UF."""
    rend = rendimento_df(df_gap)
    dedup = rend.drop_duplicates(subset=["uf_nome", "periodo_label"])
    return (
        dedup.groupby("uf_nome")["gap_salarial_pct"]
        .mean()
        .reset_index()
        .sort_values("gap_salarial_pct", ascending=False)
    )


def gap_geral(df_gap: pd.DataFrame) -> float:
    rend = rendimento_df(df_gap)
    dedup = rend.drop_duplicates(subset=["uf_nome", "periodo_label"])
    return float(dedup["gap_salarial_pct"].mean())


def rendimento_medio_por_sexo(df_gap: pd.DataFrame) -> pd.Series:
    return rendimento_df(df_gap).groupby("sexo")["valor_imputado"].mean()


def build_indicator_wide(df_gap: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por (uf_nome, periodo_label, sexo) com uma coluna por indicador.

    Usado pelo heatmap de correlação e pelo gráfico de bolhas animado (página
    "Investigação" e "O Gap Salarial") — junta tabelas 4093 e 5436, que
    compartilham uf_nome/periodo/sexo (diferente da tabela de contexto 7322).
    """
    df = add_indicador_curto(df_gap)
    df = df.dropna(subset=["indicador"])
    wide = df.pivot_table(
        index=["uf_nome", "periodo_label", "ano", "trimestre", "sexo"],
        columns="indicador",
        values="valor_imputado",
    ).reset_index()
    return wide


def normalized_profile_by_sexo(df_gap: pd.DataFrame) -> pd.DataFrame:
    """Média de `valor_normalizado` por indicador x sexo — base do radar de perfil."""
    df = add_indicador_curto(df_gap)
    df = df.dropna(subset=["indicador"])
    return df.groupby(["indicador", "sexo"])["valor_normalizado"].mean().reset_index()


def correlacao_indicadores(df_gap: pd.DataFrame) -> pd.DataFrame:
    wide = build_indicator_wide(df_gap)
    cols = ["Ocupação", "Informalidade", "Rendimento"]
    return wide[cols].corr()


def educacao_sem_total(df_contexto: pd.DataFrame) -> pd.DataFrame:
    return df_contexto[df_contexto["nivel_instrucao"] != "Total"].copy()


def educacao_share_por_sexo(df_contexto: pd.DataFrame) -> pd.DataFrame:
    """% da população (por sexo) em cada nível de instrução — soma 100% por sexo.

    Base do radar de escolaridade: mostra a *forma* da distribuição educacional
    de cada sexo, não os valores absolutos (que têm escalas diferentes).
    """
    ctx = educacao_sem_total(df_contexto)
    media = ctx.groupby(["nivel_instrucao", "sexo"])["valor_imputado"].mean().unstack()
    media = media.reindex(NIVEIS_INSTRUCAO)
    share = media.div(media.sum(axis=0), axis=1) * 100
    return share.reset_index()
