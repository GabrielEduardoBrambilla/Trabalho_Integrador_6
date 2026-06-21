# %% [markdown]

# # PM3 — Tratamento de Dados PNAD Contínua (IBGE)

# Notebook de tratamento conforme `docs/plano_pm3.md` (seções 5 a 18 do checklist,

# mapeadas para `docs/context.md` 6.4–6.17).

# **Pré-requisitos:** `01_coleta.ipynb` e `02_silver.ipynb` já executados

# (`dados/bronze/pnad_*.json` e `dados/silver/pnad_limpo.csv` existentes).

# %% [markdown]

# ## 1. Planejamento do tratamento dos dados (`context.md` 6.1)

# **Tema:** Mercado de trabalho na Região Sul do Brasil (Paraná, Santa Catarina e Rio

# Grande do Sul), com foco em rendimento, força de trabalho, informalidade e nível de

# instrução, por sexo, entre 2020 e 2025.

# **Origem dos dados:** PNAD Contínua (Pesquisa Nacional por Amostra de Domicílios

# Contínua), IBGE, via API SIDRA (`https://apisidra.ibge.gov.br`). Tabelas 4093

# (força de trabalho/informalidade), 5436 (rendimento médio) e 7322 (rendimento por

# nível de instrução), coletadas em `notebooks/01_coleta.ipynb` (dados brutos

# preservados em `dados/bronze/pnad_*.json`).

# **Problema/situação que a base ajuda a compreender:** a desigualdade de rendimento

# entre homens e mulheres no mercado de trabalho da Região Sul, sua persistência ao

# longo do tempo, e os efeitos da pandemia de COVID-19 (2020–2022) sobre a ocupação,

# a informalidade e a divulgação dos próprios dados pelo IBGE.

# **Quem poderia usar esses dados para tomar decisão:** gestores públicos estaduais

# (secretarias de planejamento e de trabalho), sindicatos e centrais sindicais,

# pesquisadores de economia do trabalho, ONGs de equidade de gênero e jornalismo de

# dados.

# **Uso em Business Intelligence:** dashboards trimestrais comparando UF × sexo para

# ocupação, taxa de informalidade e rendimento médio; monitoramento contínuo do "gap

# salarial" (`gap_salarial_pct`) como indicador-chave (KPI) de equidade.

# **Uso em Data Mining:** agrupamento (clustering) de combinações UF/trimestre por

# perfil de mercado de trabalho (ocupação, informalidade, rendimento); previsão de

# rendimento médio futuro a partir da série temporal; descoberta de padrões entre

# nível de instrução e rendimento (a base já evidencia que mulheres têm mais

# escolaridade, mas rendimento menor — um padrão não trivial).

# **Perguntas respondíveis com esses dados:**

# - Como evoluiu o rendimento médio por UF e sexo entre 2020 e 2025?

# - Qual o tamanho do gap salarial (Masc. vs. Fem.) em cada UF e como ele varia ao

# longo do tempo?

# - Como a ocupação e a informalidade se comportaram durante e após a pandemia?

# - Existe relação entre nível de instrução e rendimento que explique (ou não) o gap

# salarial?

# ---

# ## 2. Relação com Big Data Analytics, Data Mining e BI (`context.md` 6.2)

# **Como os dados poderiam apoiar decisões:** políticas públicas de equidade salarial

# podem ser direcionadas com base no tamanho real do gap por UF (seção 12/15) — por

# exemplo, priorizando programas de qualificação ou fiscalização em estados onde o

# gap não está convergindo (SC, segundo a seção 12). Sindicatos podem usar a evolução

# trimestral do rendimento (seção 6.6) para embasar negociações coletivas.

# **Padrões que poderiam ser descobertos:**

# - Correlação forte (0,86) entre pessoas ocupadas e taxa de informalidade (seção

# 6.9) — sugere que a recuperação do emprego pós-pandemia veio acompanhada de mais

# informalidade.

# - O gap salarial (30%–39%) é persistente e não explicado por escolaridade — mulheres

# têm mais "Superior completo" que homens (seção 6.11), mas rendimento menor.

# - Lacunas de divulgação do IBGE (Problema 9) coincidem temporalmente entre tabelas

# diferentes (4093 e 5436), reforçando a hipótese de undercoverage real durante a

# pandemia, não falha de coleta.

# **Tipos de análise possíveis:** séries temporais (evolução trimestral por UF/sexo),

# análise de correlação entre indicadores, agrupamento (clustering) de UF/trimestres

# por perfil de mercado de trabalho, e regressão/previsão de rendimento futuro.

# **Uso em dashboards:** sim — `df_sel` (o dataset final, seção 16) já está no

# formato "uma linha por dimensão x período x indicador", ideal para ferramentas de

# BI (Power BI, Tableau, Looker Studio) fazerem `groupby`/pivot por UF, sexo, ano e

# indicador.

# **Classificação, agrupamento, previsão ou descoberta de padrões:** todos aplicáveis.

# _Classificação_: categorizar trimestres/UFs em `faixa_rendimento` (seção 14, já

# feito via discretização). _Agrupamento_: clusterizar UF/trimestre por perfil

# multivariado (ocupação, informalidade, rendimento — usando `valor_normalizado` da

# seção 13, que já coloca os indicadores na mesma escala). _Previsão_: séries

# temporais de rendimento/ocupação por UF/sexo. _Descoberta de padrões_: a relação

# entre nível de instrução e rendimento por sexo (seções 6.11 e 12) já é um exemplo

# de padrão descoberto na EDA.

# ---

# ## 3. Modelagem inicial dos dados (`context.md` 6.3)

# A modelagem é apresentada em duas etapas: a base **silver** (ponto de partida desta

# limpeza) e o dataset **gold** final (resultado, seção 16).

# **Silver (`pnad_limpo.csv`):** 5.920 linhas × 15 colunas — granularidade de

# "um valor por (tabela, UF/região, período, sexo, variável, nível de instrução)".

# **Gold (`pnad_tratado_final.csv`, seção 16):** 448 linhas × 17 colunas, após

# filtrar para os 4 indicadores de interesse (`VARIAVEIS_FOCO`, seção 7) e adicionar

# as colunas derivadas das seções 8–15.

# - **Colunas numéricas:** `valor` (com `NaN` documentados), `valor_imputado`

# (imputado, seção 9), `valor_normalizado` (Min-Max, seção 13),

# `gap_salarial_pct` (feature derivada, seção 15).

# - **Colunas categóricas:** `tabela_id`, `indicador_tabela`, `uf_nome`,

# `regiao_nome`, `sexo`, `nivel_instrucao`, `variavel_nome`, `unidade_medida`,

# `faixa_rendimento` (seção 14), `is_outlier` (seção 10).

# - **Colunas de período:** `ano`, `trimestre` (Int64 nullable), `periodo_label`

# (seção 8).

# - **Dimensões para BI:** `uf_nome`/`regiao_nome`, `sexo`, `ano`/`trimestre`/

# `periodo_label`, `nivel_instrucao`, `indicador_tabela`/`variavel_nome`,

# `faixa_rendimento`.

# - **Medidas para BI:** `valor`/`valor_imputado` (rendimento, ocupação ou

# informalidade, conforme `indicador_tabela`), `valor_normalizado`,

# `gap_salarial_pct`.

# O catálogo completo de colunas do dataset final está em

# [`docs/catalogo_dados.md`](../docs/catalogo_dados.md) (seção 17).

# %%

import sys, pathlib

\_root = pathlib.Path.cwd()
if not (\_root / "config.py").exists():
\_root = \_root.parent
if str(\_root) not in sys.path:
sys.path.insert(0, str(\_root))

from config import config

print(f"Bronze dir : {config.bronze_dir}")
print(f"Silver dir : {config.silver_dir}")

# %%

import json

import pandas as pd
import plotly.express as px

pd.set_option("display.max_colwidth", 80)

# %% [markdown]

# ## 5. Diagnóstico da qualidade dos dados (`context.md` 6.4)

# Análise feita a partir do **bronze** (JSON bruto retornado pela API SIDRA), antes da

# normalização do `PnadNormalizer`, para expor os problemas reais da base original.

# %%

bronze = {}
for tabela in ["4093", "5436", "7322"]:
bronze[tabela] = json.loads(
(config.bronze*dir / f"pnad*{tabela}.json").read*text(encoding="utf-8")
)
print(f"pnad*{tabela}.json -> {len(bronze[tabela]) - 1:,} registros + 1 linha de cabeçalho")

print("\nLinha 0 (cabeçalho de metadados, tabela 4093):")
bronze["4093"][0]

# %%

print("Linha 1 (primeiro registro de dados, tabela 4093):")
bronze["4093"][1]

# %% [markdown]

# **Problema 1 — cabeçalho de metadados na linha 0.** A API SIDRA retorna a linha 0 com

# as _descrições_ das colunas (`D1C`/`D1N`, `D2C`/`D2N`, ..., `MC`/`MN`, `V`), e a partir

# da linha 1 os dados propriamente ditos — usando os mesmos nomes de chave. Se essa

# linha 0 não for descartada e usada apenas para mapear os nomes das colunas, ela

# aparece como um registro inválido no dataset (todas as colunas como texto

# descritivo). O `PnadNormalizer` já trata isso: usa `dados[0]` apenas para construir

# `_build_col_map` e descarta a linha do dataframe final.

# **Problema 2 — códigos numéricos vs. nomes redundantes.** Cada dimensão vem em pares

# `DnC` (código) / `DnN` (nome) — ex.: `D1C="41"` / `D1N="Paraná"`,

# `D4C="4"` / `D4N="Homens"`. Isso duplica a informação e precisa ser resolvido na

# seleção de colunas (seção 7).

# **Problema 3 — `Trimestre`/`Ano` (`D2C`) como código de texto, não como data.** Para

# 4093/5436, `D2C` vem no formato `AAAASS` (ex.: `"202001"` = 1º trimestre de 2020); para

# 7322, `D2C` é só o ano (`"2021"`). Precisa virar `ano`/`trimestre` (seção 8).

# %%

\_AUSENTES_IBGE = {"-", "...", "X", "x", "C", ""}

print("Códigos de ausência do IBGE na coluna 'V' (valor bruto):\n")
for tabela, dados in bronze.items():
df_raw = pd.DataFrame(dados[1:])
n_ausentes = df_raw["V"].isin(\_AUSENTES_IBGE).sum()
n_virgula = df_raw["V"].str.contains(",", regex=False).sum()
print(f" tabela {tabela}: {n_ausentes:>5,} / {len(df_raw):,} valores ausentes"
f" | {n_virgula} valores com vírgula decimal")
if n_ausentes:
print(" ", dict(df_raw.loc[df_raw['V'].isin(\_AUSENTES_IBGE), 'V'].value_counts()))

# %% [markdown]

# **Problema 4 — valores ausentes codificados pelo IBGE.** A tabela 4093 tem **1.632**

# valores `"..."` (≈33% das suas 4.896 linhas) e a tabela 7322 tem **8** valores `"-"`

# (≈3% das 256 linhas) — total de **1.640** valores ausentes na coluna `valor`. O

# `PnadNormalizer` converte todos os códigos `{-, ..., X, x, C, ""}` para `NaN` via

# `pd.to_numeric(..., errors="coerce")`. Esses ausentes são tratados na seção 9.

# > **Nota:** ao contrário do esperado inicialmente, **nenhum** valor numérico desta

# > coleta usa vírgula como separador decimal (todos já vêm com ponto, ex. `"49.1"`).

# > A normalização `valor_str.str.replace(",", ".")` no `PnadNormalizer` é defensiva

# > (não tem efeito nos dados atuais, mas protege contra outras tabelas SIDRA que usam

# > vírgula).

# %%

print("Problema 5 — dimensão 'Variável' (D3) empilhada na mesma coluna 'V':\n")
for tabela, dados in bronze.items():
df_raw = pd.DataFrame(dados[1:])
n_vars = df_raw["D3N"].nunique()
unidades = df_raw["MN"].unique()
print(f" tabela {tabela}: {n_vars} variáveis distintas | unidades de medida: {list(unidades)}")

print("\nExemplo — tabela 4093, variáveis e unidades (5 primeiras):")
df_4093_raw = pd.DataFrame(bronze["4093"][1:])
df_4093_raw[["D3N", "MN"]].drop_duplicates().head()

# %% [markdown]

# \*\*Problema 5 (principal) — múltiplos indicadores empilhados na mesma coluna `valor`,

# com unidades diferentes.** Cada tabela SIDRA traz a dimensão **"Variável" (D3)\*\* com

# dezenas de indicadores diferentes (contagens em "Mil pessoas", taxas em "%",

# rendimentos em "Reais" e "Coeficientes de variação" — uma medida de precisão

# estatística, não um indicador de negócio):

# - **4093** → 34 variáveis (ocupados, desocupados, taxa de informalidade, taxa de

# participação etc., cada uma com seu "Coeficiente de variação - ...").

# - **5436** → 8 variáveis (rendimento habitual/efetivo × trabalho principal/todos os

# trabalhos, e respectivos coeficientes de variação).

# - **7322** → 4 variáveis (pessoas por nível de instrução, distribuição percentual, e

# coeficientes de variação).

# Sem isolar por `variavel_nome` (e `unidade_medida`), qualquer estatística ou gráfico

# sobre `valor` mistura grandezas incompatíveis (pessoas, %, R$, coeficientes de

# variação). O `PnadNormalizer` já preserva `variavel_cod`/`variavel_nome` e

# `unidade_medida_cod`/`unidade_medida` como colunas próprias — a correção definitiva é

# **filtrar por `variavel_nome`** na seleção de dados (seção 7).

# **Problema 6 — mistura de unidades entre `tabela_id`.** Mesmo após filtrar por

# `variavel_nome`, `tabela_id == "4093"` (pessoas/%) e `tabela_id == "5436"` (R$) usam

# escalas totalmente diferentes — qualquer comparação de `valor` entre tabelas sem

# filtrar por `tabela_id` é inválida.

# **Problema 7 — recorte etário inconsistente entre tabelas.** As tabelas 4093 e 5436

# cobrem pessoas de **14 anos ou mais**, enquanto a tabela 7322 cobre pessoas de

# **10 anos ou mais**. Comparações entre `tabela_id == "7322"` e as demais (ex.:

# população total) devem registrar essa diferença de público-alvo — não são diretamente

# somáveis/comparáveis.

# \*\*Problema 8 — tabela 7322 coletada em nível geográfico diferente (N2/Região, não

# N3/UF).\*\* Suas linhas têm `regiao_cod`/`regiao_nome` preenchidos e

# `uf_cod`/`uf_nome` vazios (`NaN`), enquanto 4093/5436 são o oposto.

# %%

print("Problema 9 — períodos ausentes inteiros (não apenas valores '...'):\n")
for tabela in ["4093", "5436"]:
df_raw = pd.DataFrame(bronze[tabela][1:])
periodos_presentes = sorted(df_raw["D2C"].unique())
todos_periodos = [f"{ano}{tri:02d}" for ano in range(2020, 2026) for tri in range(1, 5)]
faltando = [p for p in todos_periodos if p not in periodos_presentes]
print(f" tabela {tabela}: {len(periodos_presentes)}/{len(todos_periodos)} trimestres "
f"presentes na resposta da API")
if faltando:
print(f" trimestres ausentes: {faltando}")

# %% [markdown]

# **Problema 9 — trimestres inteiros ausentes na resposta da API (tabela 5436).** A

# tabela 5436 retorna apenas **16 dos 24 trimestres** esperados (2020T1 a 2025T4) — os

# 8 trimestres de **2020T2 a 2022T1** simplesmente não aparecem na resposta da API

# SIDRA (não é um valor `"..."`, a linha não existe). A tabela 4093 está completa

# (24/24 trimestres, com `"..."` em alguns indicadores). Esse "buraco" temporal em

# 5436 deve ser registrado no relatório (seção 9) e aparecerá como uma lacuna no

# gráfico de evolução temporal (seção 6.6).

# %%

tabela_problemas = pd.DataFrame([
{
"problema": "Cabeçalho de metadados na linha 0",
"exemplo": "dados[0] = {'D1C': 'Unidade da Federação (Código)', ...}",
"tratamento": "Usado apenas para mapear nomes de colunas (\_build_col_map); descartado do dataframe final",
},
{
"problema": "Códigos vs. nomes redundantes (DnC/DnN)",
"exemplo": "uf_cod=41 / uf_nome='Paraná', sexo_cod=4 / sexo='Masculino'",
"tratamento": "Manter nomes para leitura/EDA; remover códigos redundantes na seleção (seção 7)",
},
{
"problema": "Período como código de texto (AAAASS / AAAA)",
"exemplo": "periodo=202001 (4093/5436), periodo=2021 (7322)",
"tratamento": "Derivar colunas ano (int) e trimestre (int, quando aplicável) na limpeza (seção 8)",
},
{
"problema": "Valores ausentes codificados pelo IBGE",
"exemplo": "valor_str = '...' (4093, 1.632x) ou '-' (7322, 8x)",
"tratamento": "Convertidos para NaN via pd.to_numeric(errors='coerce'); tratados na seção 9",
},
{
"problema": "Múltiplos indicadores empilhados em 'valor' (dimensão Variável)",
"exemplo": "tabela 4093 tem 34 'variavel_nome' distintos com unidades Mil pessoas/%/Reais",
"tratamento": "Filtrar por variavel_nome (4 indicadores de interesse) na seleção (seção 7) — problema principal",
},
{
"problema": "Mistura de unidades entre tabela_id",
"exemplo": "4093/7322 = Mil pessoas/%, 5436 = Reais",
"tratamento": "Sempre agrupar/comparar 'valor' por (tabela_id, variavel_nome, unidade_medida)",
},
{
"problema": "Recorte etário inconsistente entre tabelas",
"exemplo": "4093/5436 = 14+ anos, 7322 = 10+ anos",
"tratamento": "Documentar no relatório; não somar/comparar população entre 7322 e as demais",
},
{
"problema": "Nível geográfico distinto (UF vs. Região)",
"exemplo": "7322: uf_nome=NaN, regiao_nome='Sul'; 4093/5436: uf_nome preenchido, regiao_nome=NaN",
"tratamento": "Tratar uf_nome/regiao_nome como 'Não se aplica' conforme a tabela (seção 9)",
},
{
"problema": "Trimestres inteiros ausentes na resposta da API (5436)",
"exemplo": "5436 tem 16/24 trimestres (faltam 2020T2 a 2022T1)",
"tratamento": "Registrar lacuna temporal no relatório; não interpolar sem justificativa (seção 9)",
},
])
tabela_problemas

# %% [markdown]

# ## 6. Análise Exploratória de Dados (`context.md` 6.5)

# A partir daqui trabalhamos com o **silver** (`pnad_limpo.csv`, 5.920 linhas × 15

# colunas), já com `valor` numérico e `variavel_nome`/`unidade_medida` preservados.

# ### 6.1 Visão estrutural geral

# %%

df = pd.read_csv(config.silver_dir / "pnad_limpo.csv")

print(f"shape: {df.shape}")
df.info()

# %%

# Valores ausentes por coluna (visão geral, antes de qualquer tratamento)

df.isna().sum().to_frame("n_ausentes").assign(pct=lambda x: (100 \* x["n_ausentes"] / len(df)).round(1))

# %% [markdown]

# ### 6.2 Frequência das variáveis categóricas

# %%

print("tabela_id:")
print(df["tabela_id"].value_counts(), "\n")

print("sexo:")
print(df["sexo"].value_counts(), "\n")

print("uf_nome (NaN = registros da tabela 7322, nível Região):")
print(df["uf_nome"].value_counts(dropna=False), "\n")

print("regiao_nome (NaN = registros das tabelas 4093/5436, nível UF):")
print(df["regiao_nome"].value_counts(dropna=False), "\n")

print("nivel_instrucao (NaN = tabelas 4093/5436, sem essa classificação):")
print(df["nivel_instrucao"].value_counts(dropna=False))

# %% [markdown]

# ### 6.3 Recorte para análise de `valor`

# Conforme o **Problema 5** (seção 5), `valor` só é analisável depois de filtrar por

# `variavel_nome`. Para a EDA a seguir, usamos os **4 indicadores de interesse** que

# serão formalizados na seleção de dados (seção 7) — um indicador-chave por tabela,

# cobrindo força de trabalho, informalidade, rendimento e nível de instrução.

# %%

VARIAVEIS_FOCO = [
"Pessoas de 14 anos ou mais de idade ocupadas na semana de referência",
"Taxa de informalidade das pessoas de 14 anos ou mais de idade ocupadas na semana de referência",
"Rendimento médio mensal real das pessoas de 14 anos ou mais de idade ocupadas na semana de"
" referência com rendimento de trabalho, habitualmente recebido no trabalho principal",
"Pessoas de 10 anos ou mais de idade",
]

df_eda = df[df["variavel_nome"].isin(VARIAVEIS_FOCO)].copy()
print(f"df_eda: {df_eda.shape[0]} linhas (de {df.shape[0]} no silver completo)")
df_eda.groupby(["tabela_id", "variavel_nome", "unidade_medida"]).size().to_frame("n_linhas")

# %% [markdown]

# ### 6.4 Estatísticas descritivas de `valor` por indicador

# %%

(
df_eda.groupby(["tabela_id", "unidade_medida"])["valor"]
.describe()
.round(2)
)

# %% [markdown]

# ### 6.5 Gráfico de barras — rendimento médio por UF e sexo

# Rendimento médio mensal real (R$, tabela 5436), médio ao longo de todo o período

# 2020–2025, por UF e sexo.

# %%

df_rendimento = df_eda[df_eda["tabela_id"] == 5436]

rendimento_uf_sexo = (
df_rendimento.groupby(["uf_nome", "sexo"])["valor"].mean().reset_index()
)

fig = px.bar(
rendimento_uf_sexo,
x="uf_nome",
y="valor",
color="sexo",
barmode="group",
text_auto=".0f",
title="Rendimento médio mensal real (R$) por UF e sexo — média 2020-2025",
    labels={"uf_nome": "UF", "valor": "Rendimento médio (R$)", "sexo": "Sexo"},
)
fig.show()

# %% [markdown]

# **Interpretação:** em todos os três estados, o rendimento médio dos homens é

# nitidamente superior ao das mulheres — Paraná (R$ 3.997 vs. R$ 2.984, gap de ≈34%),

# Rio Grande do Sul (R$ 4.018 vs. R$ 3.058, gap de ≈31%) e Santa Catarina (R$ 4.182 vs.

# R$ 3.198, gap de ≈31%). Santa Catarina tem o maior rendimento médio para ambos os

# sexos, mas o gap percentual é semelhante entre os três estados — indicando que a

# desigualdade de rendimento por sexo é um padrão regional, não específico de uma UF.

# Esse "gap salarial" será formalizado como `gap_salarial_pct` na seção 15 (feature

# engineering).

# %% [markdown]

# ### 6.6 Gráfico de linha — evolução temporal do rendimento

# Evolução trimestral do rendimento médio mensal real (R$, tabela 5436), por sexo,

# agregando as três UFs.

# %%

# periodo no formato AAAASS -> rótulo "AAAA-Tn" para o eixo temporal

df_rendimento = df_rendimento.copy()
df_rendimento["ano"] = df_rendimento["periodo"] // 100
df_rendimento["trimestre"] = df_rendimento["periodo"] % 100
df_rendimento["periodo_label"] = (
df_rendimento["ano"].astype(str) + "-T" + df_rendimento["trimestre"].astype(str)
)

evolucao = (
df_rendimento.groupby(["periodo", "periodo_label", "sexo"])["valor"]
.mean()
.reset_index()
.sort_values("periodo")
)

fig = px.line(
evolucao,
x="periodo_label",
y="valor",
color="sexo",
markers=True,
title="Evolução trimestral do rendimento médio mensal real (R$) por sexo — PR/SC/RS",
    labels={"periodo_label": "Trimestre", "valor": "Rendimento médio (R$)", "sexo": "Sexo"},
)
fig.show()

# %% [markdown]

# **Interpretação:** observa-se uma lacuna entre 2020T1 e 2022T2 — reflexo do

# **Problema 9** (a tabela 5436 não retorna dados para 2020T2–2022T1). A partir de

# 2022T2, ambas as séries (homens e mulheres) mostram tendência de leve crescimento

# real do rendimento até 2025T4, com a linha dos homens consistentemente acima da das

# mulheres em todo o período observado — o gap salarial é persistente ao longo do

# tempo, oscilando entre ≈30% e ≈35% (calculado a partir do `groupby` por período/sexo),

# sem sinal de fechamento estrutural no horizonte analisado.

# %% [markdown]

# ### 6.7 Boxplot — distribuição do rendimento por sexo e por UF

# %%

fig = px.box(
df_rendimento,
x="uf_nome",
y="valor",
color="sexo",
title="Distribuição do rendimento médio mensal real (R$) por UF e sexo",
    labels={"uf_nome": "UF", "valor": "Rendimento médio (R$)", "sexo": "Sexo"},
)
fig.show()

# %% [markdown]

# **Interpretação:** os boxplots de homens ficam visivelmente acima dos de mulheres em

# todas as UFs, com pouca sobreposição entre as caixas — reforçando que o gap salarial

# não é causado por alguns trimestres atípicos, mas é uma diferença sistemática ao

# longo de toda a série. As caixas de Santa Catarina estão deslocadas para cima em

# relação a Paraná e Rio Grande do Sul (rendimentos mais altos), mas a amplitude

# (variabilidade) é semelhante entre as três UFs, sem outliers extremos visíveis — algo

# que será confirmado de forma mais rigorosa via IQR na seção 10.

# %% [markdown]

# ### 6.8 Histograma — distribuição do rendimento

# %%

fig = px.histogram(
df_rendimento,
x="valor",
color="sexo",
nbins=20,
barmode="overlay",
opacity=0.7,
title="Distribuição do rendimento médio mensal real (R$) — Mas. vs. Fem.",
    labels={"valor": "Rendimento médio (R$)", "sexo": "Sexo"},
)
fig.show()

# %% [markdown]

# **Interpretação:** as duas distribuições são unimodais e relativamente concentradas

# (feminino entre R$ 2.654–3.621, masculino entre R$ 3.582–4.676), com a distribuição

# masculina deslocada para a direita em relação à feminina e \*\*praticamente sem

# sobreposição\*\* — visualização que complementa o boxplot, evidenciando que o gap

# salarial se manifesta como um deslocamento de toda a distribuição, não apenas da

# média.

# %% [markdown]

# ### 6.9 Heatmap de correlação entre indicadores

# Para correlacionar indicadores de tabelas/unidades diferentes, primeiro pivotamos

# `df_eda` (tabelas 4093 e 5436, que compartilham `uf_nome`/`periodo`/`sexo`) para uma

# linha por (UF, período, sexo) com uma coluna por indicador.

# %%

ROTULOS_INDICADOR = {
"Pessoas de 14 anos ou mais de idade ocupadas na semana de referência": "ocupados_mil",
"Taxa de informalidade das pessoas de 14 anos ou mais de idade ocupadas na semana de referência": "taxa_informalidade_pct",
"Rendimento médio mensal real das pessoas de 14 anos ou mais de idade ocupadas na semana de"
" referência com rendimento de trabalho, habitualmente recebido no trabalho principal": "rendimento_medio_r$",
}

df_4093_5436 = df_eda[df_eda["tabela_id"].isin([4093, 5436])].copy()
df_4093_5436["indicador"] = df_4093_5436["variavel_nome"].map(ROTULOS_INDICADOR)

df_pivot = df_4093_5436.pivot_table(
index=["uf_nome", "periodo", "sexo"], columns="indicador", values="valor"
).reset_index()

corr = df_pivot[list(ROTULOS_INDICADOR.values())].corr().round(2)
corr

# %%

fig = px.imshow(
corr,
text_auto=True,
color_continuous_scale="RdBu_r",
zmin=-1,
zmax=1,
title="Correlação entre indicadores (ocupados, taxa de informalidade, rendimento)",
)
fig.show()

# %% [markdown]

# **Interpretação:** `ocupados_mil` e `taxa_informalidade_pct` têm correlação forte

# (0.86) — ambos crescem ao longo da série, possivelmente refletindo a recuperação do

# mercado de trabalho pós-pandemia acompanhada de aumento da informalidade (mais

# correlação temporal conjunta do que causalidade direta). `rendimento_medio_r$` tem

# correlação moderada com `ocupados_mil` (0.49) e correlação muito fraca com

# `taxa_informalidade_pct` (0.07) — sugerindo que o nível de rendimento médio não está

# diretamente associado ao grau de informalidade nesta amostra (PR/SC/RS,

# 2020–2025).

# %% [markdown]

# ### 6.10 Análise temporal — taxa de informalidade (tabela 4093)

# Diferente de 5436, a tabela 4093 está completa nos 24 trimestres (2020T1–2025T4),

# mas com valores `...`/`NaN` em alguns trimestres (Problema 4).

# %%

df_informalidade = df_eda[
df_eda["variavel_nome"]
== "Taxa de informalidade das pessoas de 14 anos ou mais de idade ocupadas na semana de referência"
].copy()
df_informalidade["ano"] = df_informalidade["periodo"] // 100
df_informalidade["trimestre"] = df_informalidade["periodo"] % 100
df_informalidade["periodo_label"] = (
df_informalidade["ano"].astype(str) + "-T" + df_informalidade["trimestre"].astype(str)
)

evolucao_informalidade = (
df_informalidade.groupby(["periodo", "periodo_label", "sexo"])["valor"]
.mean()
.reset_index()
.sort_values("periodo")
)

fig = px.line(
evolucao_informalidade,
x="periodo_label",
y="valor",
color="sexo",
markers=True,
title="Evolução trimestral da taxa de informalidade (%) por sexo — PR/SC/RS",
labels={"periodo_label": "Trimestre", "valor": "Taxa de informalidade (%)", "sexo": "Sexo"},
)
fig.show()

print(f"\nTrimestres com valor ausente (NaN): "
f"{df_informalidade['valor'].isna().sum()} de {len(df_informalidade)}")

# %% [markdown]

# **Interpretação:** 48 das 144 linhas (33%) têm `valor` ausente (`NaN`), todas

# concentradas em **2020T2–2022T1** — exatamente o mesmo intervalo em que a tabela 5436

# não retorna dados (Problema 9). Isso reforça a hipótese de que esse período reflete

# uma limitação real de divulgação do IBGE para PR/SC/RS durante a fase mais aguda da

# pandemia (provável undercoverage da coleta por telefone), e não um problema do

# pipeline de coleta. Nos trimestres com dado disponível, a taxa de informalidade

# feminina e masculina seguem padrões semelhantes, sem um gap tão marcante quanto o

# observado no rendimento.

# %% [markdown]

# ### 6.11 População da Região Sul por nível de instrução e sexo (tabela 7322)

# %%

df_instrucao = df_eda[
(df_eda["tabela_id"] == 7322) & (df_eda["nivel_instrucao"] != "Total")
].copy()

instrucao_media = (
df_instrucao.groupby(["nivel_instrucao", "sexo"])["valor"].mean().reset_index()
)

ordem_instrucao = [
"Sem instrução", "Fundamental incompleto", "Fundamental completo",
"Médio incompleto", "Médio completo", "Superior incompleto", "Superior completo",
]

fig = px.bar(
instrucao_media,
x="nivel_instrucao",
y="valor",
color="sexo",
barmode="group",
category_orders={"nivel_instrucao": ordem_instrucao},
title="População (Mil pessoas, 10+ anos) da Região Sul por nível de instrução e sexo — média 2021-2024",
labels={"nivel_instrucao": "Nível de instrução", "valor": "População (Mil pessoas)", "sexo": "Sexo"},
)
fig.update_xaxes(tickangle=30)
fig.show()

# %% [markdown]

# **Interpretação:** o "Fundamental incompleto" é o nível de instrução mais numeroso

# para ambos os sexos (≈1.027 mil mulheres, ≈1.048 mil homens), seguido de "Médio

# completo". O contraste mais notável aparece no "Superior completo": \*\*mulheres

# superam homens\*\* (≈650 mil vs. ≈483 mil) — um padrão consistente com dados

# educacionais nacionais (maior conclusão do ensino superior por mulheres). Combinado

# com o gráfico de rendimento (seção 6.5), isso sugere que o gap salarial \*\*não é

# explicado por escolaridade\*\* — mulheres têm, em média, mais anos de estudo, mas

# recebem rendimentos menores.

# %% [markdown]

# ---

# ## 7. Seleção dos dados (`context.md` 6.6)

# ### 7.1 Filtro de linhas — `variavel_nome`

# Mantemos apenas os 4 indicadores de interesse já usados na EDA (`VARIAVEIS_FOCO`),

# descartando todas as linhas de "Coeficiente de variação - ..." e "Distribuição

# percentual - ..." (não são indicadores de negócio, são medidas de precisão

# estatística do IBGE — ver Problema 5, seção 5).

# ### 7.2 Seleção de colunas

# - **Mantidas:** `tabela_id`, `uf_nome`, `regiao_nome`, `periodo`, `sexo`,

# `nivel_instrucao`, `variavel_nome`, `unidade_medida`, `valor`.

# - **Removidas (redundantes com a versão em texto):** `uf_cod`, `sexo_cod`,

# `regiao_cod`, `variavel_cod`, `nivel_instrucao_cod`, `unidade_medida_cod`.

# - `periodo` é mantido nesta etapa e será decomposto em `ano`/`trimestre` na

# limpeza (seção 8).

# %%

COLUNAS_SELECIONADAS = [
"tabela_id", "uf_nome", "regiao_nome", "periodo", "sexo",
"nivel_instrucao", "variavel_nome", "unidade_medida", "valor",
]

df_sel = df[df["variavel_nome"].isin(VARIAVEIS_FOCO)][COLUNAS_SELECIONADAS].copy()

print(f"df_sel: {df_sel.shape[0]} linhas x {df_sel.shape[1]} colunas")
print(f"(de {df.shape[0]} linhas x {df.shape[1]} colunas no silver completo)")
df_sel.head()

# %% [markdown]

# ### 7.3 Filtro de linhas — registros com `valor` ausente

# Por ora **mantemos** as linhas com `valor` ausente em `df_sel` (não removemos),

# porque a ausência em si é informação relevante (Problemas 4 e 9 — undercoverage da

# PNAD durante a pandemia). A estratégia de tratamento (manter como `NaN` documentado

# vs. imputar) é decidida e justificada na seção 9.

# %% [markdown]

# ---

# ## 8. Limpeza e pré-processamento (`context.md` 6.7)

# ### 8.1 `periodo` (AAAASS / AAAA) → `ano` + `trimestre`

# - Tabelas 4093/5436: `periodo` no formato `AAAASS` (ex.: `202001` = 2020, T1).

# - Tabela 7322: `periodo` é só o ano (`2021`..`2024`) — não tem trimestre

# (indicador anual).

# %%

def \_split_periodo(row):
periodo = row["periodo"]
if row["tabela_id"] == 7322:
return pd.Series({"ano": periodo, "trimestre": pd.NA})
return pd.Series({"ano": periodo // 100, "trimestre": periodo % 100})

df_sel[["ano", "trimestre"]] = df_sel.apply(\_split_periodo, axis=1)
df_sel["ano"] = df_sel["ano"].astype(int)
df_sel["trimestre"] = df_sel["trimestre"].astype("Int64") # nullable int (NA p/ tabela 7322)

df_sel = df_sel.drop(columns=["periodo"])

print(df_sel[["tabela_id", "ano", "trimestre"]].drop_duplicates().groupby("tabela_id").agg(
{"ano": ["min", "max"], "trimestre": lambda x: sorted(x.dropna().unique().tolist())}
))
df_sel.head()

# %% [markdown]

# ### 8.2 `periodo_label` legível

# %%

df_sel["periodo_label"] = df_sel.apply(
lambda r: f"{r['ano']}-T{r['trimestre']}" if pd.notna(r["trimestre"]) else str(r["ano"]),
axis=1,
)
df_sel[["tabela_id", "ano", "trimestre", "periodo_label"]].drop_duplicates().head(8)

# %% [markdown]

# ### 8.3 Duplicidades

# %%

n_dup = df_sel.duplicated().sum()
print(f"Linhas duplicadas em df_sel: {n_dup}")

# Cada combinação (tabela_id, uf_nome/regiao_nome, periodo, sexo, nivel_instrucao,

# variavel_nome) deveria ser única — checagem da chave de granularidade

chave = ["tabela_id", "uf_nome", "regiao_nome", "ano", "trimestre", "sexo", "nivel_instrucao", "variavel_nome"]
n_dup_chave = df_sel.duplicated(subset=chave).sum()
print(f"Linhas duplicadas pela chave de granularidade: {n_dup_chave}")

# %% [markdown]

# ### 8.4 Padronização de categorias de texto

# `uf_nome`, `regiao_nome` e `nivel_instrucao` têm `NaN` para tabelas que não possuem

# aquela dimensão (Problema 8). Substituímos por `"Não se aplica"` para deixar

# explícito que a ausência é estrutural (não é um dado faltante a ser

# imputado/investigado) — diferente do `NaN` em `valor`, que é tratado na seção 9.

# %%

for col in ["uf_nome", "regiao_nome", "nivel_instrucao"]:
df_sel[col] = df_sel[col].fillna("Não se aplica")

# checagem de consistência de texto (sem variações de acentuação/caixa)

for col in ["uf_nome", "regiao_nome", "sexo", "nivel_instrucao", "tabela_id", "unidade_medida"]:
print(f"{col}: {sorted(df_sel[col].astype(str).unique())}")

# %% [markdown]

# ---

# ## 9. Tratamento de valores faltantes (`context.md` 6.8)

# ### 9.1 Quantificação (antes do tratamento)

# %%

print(f"Total de NaN em 'valor': {df_sel['valor'].isna().sum()} / {len(df_sel)}\n")

print("NaN por tabela_id / variavel_nome:")
print(
df_sel[df_sel["valor"].isna()]
.groupby(["tabela_id", "variavel_nome"])
.size()
.to_frame("n_nan")
)

print("\nPeríodos afetados (todos em 4093):")
print(sorted(df_sel.loc[df_sel["valor"].isna(), "periodo_label"].unique()))

# %% [markdown]

# ### 9.2 Estratégia de tratamento

# Os 96 valores ausentes (todos em `tabela_id == 4093`, indicadores "Pessoas ocupadas"

# e "Taxa de informalidade", trimestres 2020T2–2022T1) refletem \*\*undercoverage real

# da PNAD durante a pandemia\*\* (Problemas 4 e 9, seção 5) — o IBGE optou por não

# divulgar esses valores por insuficiência amostral, não por falha na coleta deste

# projeto.

# **Decisão:** manter `valor` como `NaN` (preserva a informação de que o dado \*não

# existe na fonte\*, essencial para um relatório honesto sobre a pandemia). Para

# demonstrar a técnica de imputação (exigência do PM3), criamos uma coluna adicional

# `valor_imputado`, preenchida pela **média do grupo** (`uf_nome`, `sexo`,

# `variavel_nome`) — ou seja, assume-se que o indicador naquele trimestre seguiu o

# padrão médio da série da mesma UF/sexo/indicador. Ambas as colunas seguem para o

# dataset final (seção 16), permitindo ao analista escolher qual usar conforme a

# análise.

# %%

grupo = ["uf_nome", "sexo", "variavel_nome"]
df_sel["valor_imputado"] = df_sel["valor"].fillna(
df_sel.groupby(grupo)["valor"].transform("mean")
)

print(f"NaN em 'valor': {df_sel['valor'].isna().sum()}")
print(f"NaN em 'valor_imputado': {df_sel['valor_imputado'].isna().sum()}")

# Exemplo: trimestre 2020-T2, ocupados em PR/Masculino

df_sel[
(df_sel["periodo_label"] == "2020-T2")
& (df_sel["uf_nome"] == "Paraná")
& (df_sel["sexo"] == "Masculino")
][["periodo_label", "uf_nome", "sexo", "variavel_nome", "valor", "valor_imputado"]]

# %% [markdown]

# ---

# ## 10. Tratamento de outliers (`context.md` 6.9)

# Análise via **IQR** (1.5×) de `valor_imputado`, separada por `tabela_id` +

# `variavel_nome` (cada combinação tem sua própria escala/unidade — Problema 6).

# %%

def \_flag_outliers(grupo_df):
q1, q3 = grupo_df["valor_imputado"].quantile([0.25, 0.75])
iqr = q3 - q1
limite_inf, limite_sup = q1 - 1.5 _ iqr, q3 + 1.5 _ iqr
return (grupo_df["valor_imputado"] < limite_inf) | (grupo_df["valor_imputado"] > limite_sup)

df_sel["is_outlier"] = (
df_sel.groupby(["tabela_id", "variavel_nome"], group_keys=False)
.apply(\_flag_outliers, include_groups=False)
)

print(f"Outliers detectados (IQR 1.5x): {df_sel['is_outlier'].sum()} / {len(df_sel)}\n")
print(df_sel[df_sel["is_outlier"]].groupby(["tabela_id", "variavel_nome"]).size())
df_sel[df_sel["is_outlier"]][
["tabela_id", "uf_nome", "regiao_nome", "periodo_label", "sexo", "nivel_instrucao", "variavel_nome", "valor_imputado"]
]

# %% [markdown]

# **Interpretação e decisão:** os 8 "outliers" detectados pelo IQR são todos da

# combinação `tabela_id == 7322` / `nivel_instrucao == "Total"` — ou seja, são a

# **soma de todos os outros níveis de instrução** para aquele ano/sexo (≈13 mil, vs.

# ≈300–1.000 mil de cada nível individual). Não é um erro de digitação nem um valor

# estatisticamente anômalo: é uma agregação legítima embutida na própria classificação

# do IBGE (categoria "Total" dentro de "Nível de instrução"). **Decisão:** manter os

# valores (não remover/transformar), mas a coluna `is_outlier` permanece no dataset

# final para que análises que exijam apenas os subníveis (excluindo "Total") possam

# filtrar com `is_outlier == False` ou, de forma mais explícita,

# `nivel_instrucao != "Total"`. Para os indicadores das tabelas 4093/5436, **nenhum**

# outlier foi detectado pelo IQR — a queda de rendimento/ocupação observada em

# 2020–2022 (seção 6) está dentro da variação normal da série.

# %% [markdown]

# ---

# ## 11. Transformação dos dados (`context.md` 6.10)

# A separação de `periodo` em `ano` + `trimestre` + `periodo_label` já foi feita nas

# seções 8.1/8.2 durante a limpeza (era pré-requisito dos gráficos temporais da seção

# 6). O que falta para completar a transformação é \*\*agrupar `tabela_id` em rótulos

# descritivos\*\*, facilitando a leitura do dataset final por quem não conhece os

# códigos do SIDRA.

# %%

TABELA_LABELS = {
4093: "Força de trabalho e informalidade",
5436: "Rendimento médio",
7322: "Rendimento por nível de instrução",
}

df_sel["indicador_tabela"] = df_sel["tabela_id"].map(TABELA_LABELS)
df_sel[["tabela_id", "indicador_tabela"]].drop_duplicates()

# %% [markdown]

# ---

# ## 12. Agregação de dados (`context.md` 6.11)

# Tabela agregada: rendimento médio anual (R$, `valor_imputado`, tabela 5436) por UF e

# sexo — uma visão "anualizada" que resume os 4 trimestres de cada ano em um único

# número, útil para um dashboard de BI que compare a evolução ano a ano sem o ruído da

# sazonalidade trimestral.

# %%

rendimento_anual = (
df_sel[df_sel["tabela_id"] == 5436]
.groupby(["uf_nome", "sexo", "ano"])["valor_imputado"]
.mean()
.round(2)
.reset_index()
.rename(columns={"valor_imputado": "rendimento_medio_anual_r$"})
)
rendimento_anual

# %% [markdown]

# **Interpretação:** o ano de **2021 não aparece** na tabela — reflexo direto do

# "buraco" temporal da tabela 5436 (Problema 9, 2020T2–2022T1): 2020 tem só o dado de

# T1 e 2022 tem só T2–T4, então a média anual de 2021 ficaria baseada em 0 trimestres

# reais (mesmo usando `valor_imputado`, não há nenhum trimestre de 2021 na base — a

# imputação preenche valores ausentes _dentro_ de uma linha existente, não cria linhas

# para períodos inexistentes). Olhando a evolução de 2020 a 2025: o rendimento

# masculino cresce de forma consistente nas três UFs (PR: R$ 3.918 → R$ 4.378, +11,7%;

# RS: R$ 3.863 → R$ 4.274, +10,6%; SC: R$ 3.901 → R$ 4.636, +18,8%), enquanto o

# feminino cresce a um ritmo semelhante ou maior em termos relativos (PR: +15,3%; RS:

# +15,7%; SC: +19,4%). Como resultado, o gap percentual (Masc. vs. Fem.) recua

# ligeiramente em PR (37,3% → 33,1%) e RS (37,6% → 31,6%), e fica praticamente estável

# em SC (31,7% → 31,1%) — um sinal de leve convergência, mas o gap permanece acima de

# 30% em todos os casos até 2025.

# %% [markdown]

# ---

# ## 13. Normalização e padronização (`context.md` 6.12)

# Aplicamos **Min-Max scaling** (`sklearn.preprocessing.MinMaxScaler`) sobre

# `valor_imputado`, gerando `valor_normalizado` no intervalo `[0, 1]`. A escala é

# ajustada **separadamente para cada combinação `(tabela_id, variavel_nome)`**, pois

# cada indicador tem sua própria unidade/grandeza (Mil pessoas, %, R$ — Problema 6) —

# normalizar todos juntos faria, por exemplo, percentuais (0-100) dominarem reais

# (centenas/milhares) de forma artificial. Min-Max foi escolhido em vez de

# `StandardScaler` (z-score) porque o objetivo é colocar todos os indicadores na

# mesma escala `[0, 1]` para visualizações comparativas (ex.: um único gráfico com

# ocupados, informalidade e rendimento na mesma escala), o que é mais intuitivo de

# interpretar do que desvios-padrão.

# %%

from sklearn.preprocessing import MinMaxScaler

def \_normalizar_grupo(grupo_df):
valores = grupo_df[["valor_imputado"]]
return pd.Series(
MinMaxScaler().fit_transform(valores).ravel(), index=grupo_df.index
)

df_sel["valor_normalizado"] = (
df_sel.groupby(["tabela_id", "variavel_nome"], group_keys=False)
.apply(\_normalizar_grupo, include_groups=False)
)

# Antes vs. depois, para um indicador (rendimento médio, tabela 5436)

df_sel[df_sel["tabela_id"] == 5436][
["periodo_label", "uf_nome", "sexo", "valor_imputado", "valor_normalizado"]
].sort_values("valor_imputado").iloc[[0, -1]]

# %% [markdown]

# ---

# ## 14. Discretização dos dados (`context.md` 6.13)

# Discretizamos o **rendimento médio** (`valor_imputado`, tabela 5436) em três faixas

# — `baixo` / `médio` / `alto` — usando `pd.qcut` (tercis: cada faixa concentra ~1/3

# das observações). Essa coluna `faixa_rendimento` é útil para BI (ex.: segmentar

# UF/trimestres por faixa de rendimento sem precisar olhar o valor exato) e para

# análises categóricas (ex.: contar quantos trimestres cada UF/sexo passou em cada

# faixa). Para as demais tabelas (4093/7322), `faixa_rendimento` fica `"Não se

# aplica"`.

# %%

df_sel["faixa_rendimento"] = "Não se aplica"

mask_5436 = df_sel["tabela_id"] == 5436
df_sel.loc[mask_5436, "faixa_rendimento"] = pd.qcut(
df_sel.loc[mask_5436, "valor_imputado"],
q=3,
labels=["baixo", "médio", "alto"],
)

print(df_sel.loc[mask_5436, "faixa_rendimento"].value_counts())
df_sel.loc[mask_5436, ["periodo_label", "uf_nome", "sexo", "valor_imputado", "faixa_rendimento"]].sample(
5, random_state=42
).sort_values("valor_imputado")

# %% [markdown]

# ---

# ## 15. Feature Engineering (`context.md` 6.14)

# A principal feature derivada é o **gap salarial percentual** por UF e período —

# formalizando a desigualdade observada nas seções 6.5/6.6/6.7:

# ```

# gap_salarial_pct = (rendimento_masculino - rendimento_feminino) / rendimento_feminino \* 100

# ```

# Calculado via `pivot_table` de `sexo` (uma coluna para "Masculino" e outra para

# "Feminino" do `valor_imputado`, indexado por `uf_nome` + `periodo_label`) e depois

# reanexado a `df_sel` — ambas as linhas (Masculino e Feminino) de um mesmo

# UF/período recebem o mesmo `gap_salarial_pct`, pois é uma medida do par, não de um

# sexo isoladamente. As demais features de transformação/discretização (`ano`,

# `trimestre`, `periodo_label`, `faixa_rendimento`, `is_outlier`,

# `valor_normalizado`, `indicador_tabela`) já foram criadas nas seções 8, 11, 13 e

# 14 — `df_sel` consolida todas elas.

# %%

df_5436 = df_sel[df_sel["tabela_id"] == 5436]

pivot_sexo = df_5436.pivot_table(
index=["uf_nome", "periodo_label"], columns="sexo", values="valor_imputado"
)
pivot_sexo["gap_salarial_pct"] = (
(pivot_sexo["Masculino"] - pivot_sexo["Feminino"]) / pivot_sexo["Feminino"] \* 100
).round(2)

df_sel = df_sel.merge(
pivot_sexo["gap_salarial_pct"].reset_index(),
on=["uf_nome", "periodo_label"],
how="left",
)

df_sel.loc[df_sel["tabela_id"] == 5436, ["periodo_label", "uf_nome", "sexo", "valor_imputado", "gap_salarial_pct"]].head(6)

# %% [markdown]

# ---

# ## 16. Consolidação do dataset final (`context.md` 6.15)

# `df_sel` reúne todas as colunas originais selecionadas (seção 7) mais as colunas

# criadas nas seções 8–15: `ano`, `trimestre`, `periodo_label`, `indicador_tabela`,

# `valor_imputado`, `is_outlier`, `valor_normalizado`, `faixa_rendimento`,

# `gap_salarial_pct`. É claramente diferente do bronze (JSON bruto por tabela) e do

# silver (`pnad_limpo.csv`, 5.920×15, sem essas colunas derivadas) — o resultado é

# salvo em `dados/gold/pnad_tratado_final.csv`.

# %%

config.gold_dir.mkdir(parents=True, exist_ok=True)

out_path = config.gold_dir / "pnad_tratado_final.csv"
df_sel.to_csv(out_path, index=False, encoding="utf-8")

print(f"shape final: {df_sel.shape[0]} linhas x {df_sel.shape[1]} colunas")
print(f"colunas: {list(df_sel.columns)}")
print(f"\nsalvo em: {out_path}")

# %% [markdown]

# ---

# ## 17. Catálogo de dados (`context.md` 6.16)

# Catálogo completo das 17 colunas de `pnad_tratado_final.csv` — descrição, tipo,

# exemplo, origem (original/derivada), tratamento aplicado e uso esperado — está em

# [`docs/catalogo_dados.md`](../docs/catalogo_dados.md).

# ---

# ## 18. DataOps e organização do projeto (`context.md` 6.17)

# - Estrutura de pastas, pipeline de execução (`01_coleta` → `02_silver` →

# `03_tratamento_pm3`) e convenções estão documentadas no `README.md` da raiz do

# projeto.

# - `dados/bronze/` (JSON original do SIDRA) e `dados/gold/pnad_tratado_final.csv`

# (dataset final) são versionados no repositório como evidência/entregável do PM3

# (ver `.gitignore`).
