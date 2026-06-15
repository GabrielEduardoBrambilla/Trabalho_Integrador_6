# Relatório Final — PM3: Tratamento de Dados do Mercado de Trabalho na Região Sul (PNAD Contínua/IBGE)

> Estrutura conforme `docs/context.md` (seção 8, 23 itens). Todos os números,
> tabelas e gráficos citados estão implementados e executados em
> `notebooks/03_tratamento_pm3.ipynb`; as seções abaixo indicam onde encontrar
> cada item no notebook.

## 1. Introdução

Este relatório documenta o processo completo de tratamento de dados (PM3) aplicado
à PNAD Contínua (IBGE), com foco no mercado de trabalho da Região Sul do Brasil
(Paraná, Santa Catarina e Rio Grande do Sul) entre 2020 e 2025. O trabalho cobre
desde a coleta dos dados brutos via API SIDRA até a entrega de um dataset final
limpo, transformado e documentado, pronto para uso em ferramentas de Business
Intelligence (BI) e Data Mining.

## 2. Tema escolhido

**Mercado de trabalho na Região Sul: rendimento, força de trabalho, informalidade
e nível de instrução, por sexo (2020–2025).** O tema foi escolhido por permitir a
análise de um problema social relevante e mensurável — a desigualdade de
rendimento entre homens e mulheres ("gap salarial") — usando dados públicos,
oficiais e atualizados periodicamente.

## 3. Fonte dos dados

- **Fonte:** PNAD Contínua (Pesquisa Nacional por Amostra de Domicílios Contínua),
  IBGE, via API SIDRA — `https://apisidra.ibge.gov.br`.
- **Tabelas utilizadas:**
  - **4093** — Força de trabalho, pessoas ocupadas e taxa de informalidade, por
    sexo e UF (trimestral, pessoas de 14+ anos).
  - **5436** — Rendimento médio real habitual do trabalho principal, por sexo e UF
    (trimestral, pessoas de 14+ anos).
  - **7322** — Pessoas por nível de instrução, por sexo, Região Sul (anual,
    pessoas de 10+ anos).
- **Recorte geográfico:** Paraná, Santa Catarina e Rio Grande do Sul (UFs) e Região
  Sul (agregado, tabela 7322).
- **Recorte temporal:** 2020 a 2025.
- **Coleta:** `notebooks/01_coleta.ipynb` (classe `PnadCollector`), dados brutos
  preservados em `dados/bronze/pnad_4093.json`, `pnad_5436.json`, `pnad_7322.json`.

## 4. Objetivo do trabalho

Transformar os dados brutos da PNAD Contínua — que vêm em formato bruto de API,
com códigos de ausência do IBGE, períodos codificados, múltiplos indicadores
empilhados e unidades de medida diferentes — em um dataset único, limpo,
documentado e enriquecido com colunas derivadas (período legível, valores
imputados, normalização, faixas de rendimento e gap salarial), pronto para
alimentar dashboards de BI e análises de Data Mining sobre desigualdade de
rendimento no mercado de trabalho da Região Sul.

## 5. Descrição da base de dados original

A base original (silver, `dados/silver/pnad_limpo.csv`, gerada a partir do bronze
pelo `PnadNormalizer`) tem **5.920 linhas × 15 colunas**:
`tabela_id, uf_cod, uf_nome, regiao_cod, regiao_nome, periodo, sexo_cod, sexo,
nivel_instrucao_cod, nivel_instrucao, variavel_cod, variavel_nome,
unidade_medida_cod, unidade_medida, valor`.

Cada `tabela_id` traz dezenas de `variavel_nome` diferentes empilhadas na mesma
coluna `valor`, com unidades distintas (Mil pessoas, %, Reais) — ver seção 7
(Diagnóstico) para detalhes. O dataset bruto (bronze, JSON da API SIDRA) está
preservado em `dados/bronze/`.

## 6. Relação com BI, Big Data Analytics e Data Mining

> Texto completo implementado em `notebooks/03_tratamento_pm3.ipynb`, seções "1.
> Planejamento do tratamento dos dados" e "2. Relação com Big Data Analytics, Data
> Mining e BI".

**Resumo:**
- **BI:** o dataset final (`df_sel`, formato long — uma linha por
  dimensão×período×indicador) alimenta diretamente dashboards de evolução do
  rendimento, ocupação, informalidade e gap salarial por UF, sexo e trimestre.
- **Data Mining:** o dataset suporta (a) **classificação** de
  trimestres/UFs por `faixa_rendimento` (baixo/médio/alto, seção 14), (b)
  **agrupamento (clustering)** de UF/trimestre por perfil multivariado usando
  `valor_normalizado` (seção 13), (c) **previsão** de rendimento futuro via séries
  temporais por UF/sexo, e (d) **descoberta de padrões**, como a correlação de
  0,86 entre pessoas ocupadas e taxa de informalidade, e a persistência do gap
  salarial (30%–39%) mesmo com maior escolaridade feminina.
- **Quem usaria:** gestores públicos estaduais, sindicatos, pesquisadores de
  economia do trabalho, ONGs de equidade de gênero e jornalismo de dados.

## 7. Diagnóstico da qualidade dos dados

> Implementado em `notebooks/03_tratamento_pm3.ipynb`, seção "5. Diagnóstico da
> qualidade dos dados" (`tabela_problemas`, 9 problemas).

Principais problemas encontrados na base bruta/silver:

| # | Problema | Exemplo |
|---|---|---|
| 1 | Linha 0 do JSON SIDRA = cabeçalho de metadados misturado aos dados | Primeira linha de cada `pnad_*.json` |
| 2 | Códigos de ausência do IBGE não numéricos | `-`, `...`, `X`, `x`, `C`, `""` |
| 3 | Valores numéricos com vírgula decimal (defensivo, não ocorreu nesta coleta) | `"4.529,00"` |
| 4 | `periodo` como código `AAAASS`/`AAAA` (texto), não data | `"202301"` |
| 5 | **(Principal)** Dimensão "Variável" (D3) empilha dezenas de indicadores com unidades diferentes na mesma coluna `valor` | 4093 tem 34 variáveis (Mil pessoas, %, coef. variação) |
| 6 | Mistura de unidades entre `tabela_id` | 4093/7322 = pessoas/%, 5436 = R$ |
| 7 | Recorte etário inconsistente entre tabelas | 4093/5436 = 14+ anos; 7322 = 10+ anos |
| 8 | Códigos vs. nomes redundantes | `uf_cod`/`uf_nome`, `sexo_cod`/`sexo`, `regiao_cod`/`regiao_nome` |
| 9 | Lacuna temporal — tabela 5436 retorna apenas 16/24 trimestres | Faltam 2020T2 a 2022T1 (linhas inteiras ausentes) |

## 8. Análise Exploratória de Dados (EDA)

> Implementado em `notebooks/03_tratamento_pm3.ipynb`, seção "6. Análise
> Exploratória de Dados", com gráficos plotly e interpretação textual de cada um.

Principais achados:
- Estatísticas descritivas de `valor` calculadas separadamente por `tabela_id`
  (unidades distintas).
- Gráfico de barras: rendimento médio por UF e sexo (5436) e população por nível de
  instrução e sexo (7322) — mulheres têm mais "Superior completo" que homens em
  todas as UFs.
- Gráfico de linha: evolução trimestral do rendimento e da taxa de informalidade —
  ambos voltam a crescer após 2021.
- Boxplot e histograma: distribuição de `valor` (rendimento) por sexo/UF — Feminino
  consistentemente mais baixo e com menor dispersão.
- Heatmap de correlação: pessoas ocupadas × taxa de informalidade = 0,86.
- Análise temporal: lacuna 2020T2–2022T1 confirmada visualmente (Problema 9).

## 9. Seleção dos dados

> Implementado em `notebooks/03_tratamento_pm3.ipynb`, seção "7. Seleção dos
> dados".

- **Filtro por `variavel_nome`** (`VARIAVEIS_FOCO`): de 34+8+4 variáveis
  disponíveis, mantidos apenas 4 indicadores de interesse — pessoas ocupadas e
  taxa de informalidade (4093), rendimento médio mensal real (5436), pessoas por
  nível de instrução (7322). Resultado: **448 linhas**.
- **Colunas mantidas:** `tabela_id, uf_nome, regiao_nome, periodo, sexo,
  nivel_instrucao, variavel_nome, unidade_medida, valor`.
- **Colunas removidas:** `uf_cod, sexo_cod, regiao_cod, variavel_cod,
  nivel_instrucao_cod, unidade_medida_cod` (redundantes com as versões em texto).
- **Linhas com `valor` ausente mantidas** — a ausência é informação relevante
  (Problemas 4 e 9), tratada na seção 11.

## 10. Limpeza dos dados

> Implementado em `notebooks/03_tratamento_pm3.ipynb`, seção "8. Limpeza e
> pré-processamento".

- Nomes de colunas já em snake_case (confirmado).
- `periodo` (`AAAASS`/`AAAA`, texto) → `ano` (int) + `trimestre` (Int64 nullable) +
  `periodo_label` (`"2023-T3"` ou `"2021"`).
- `valor` confirmado como `float`.
- 0 duplicatas encontradas (`df.duplicated()` e checagem pela chave de
  granularidade).
- `uf_nome`/`regiao_nome`/`nivel_instrucao` com `NaN` estrutural preenchidos como
  `"Não se aplica"`.

## 11. Tratamento de valores faltantes

> Implementado em `notebooks/03_tratamento_pm3.ipynb`, seção "9. Tratamento de
> valores faltantes".

- **Antes:** 96/448 (21,4%) valores ausentes em `valor`, todos em `tabela_id ==
  4093`, trimestres 2020T2–2022T1 — undercoverage real da PNAD durante a pandemia.
- **Decisão:** manter `valor` com `NaN` (preserva a informação de que o dado não
  foi divulgado) **e** criar `valor_imputado` (imputação pela média do grupo
  `uf_nome`+`sexo`+`variavel_nome`). `valor_imputado` tem 0/448 nulos.

## 12. Tratamento de outliers

> Implementado em `notebooks/03_tratamento_pm3.ipynb`, seção "10. Tratamento de
> outliers".

- Detecção via **IQR (1,5×)** sobre `valor_imputado`, separado por
  `(tabela_id, variavel_nome)`.
- Resultado: **8/448 outliers**, todos em `tabela_id == 7322` /
  `nivel_instrucao == "Total"` — categoria estrutural (soma dos demais níveis de
  instrução), não erro de dado.
- **Decisão:** manter os valores e a coluna `is_outlier` para que análises possam
  filtrar `nivel_instrucao != "Total"` quando necessário.

## 13. Transformação dos dados

> Implementado em `notebooks/03_tratamento_pm3.ipynb`, seção "11. Transformação
> dos dados".

- `ano`, `trimestre`, `periodo_label` derivados de `periodo` (seção 10 deste
  relatório / seção 8 do notebook).
- `tabela_id` mapeado para rótulos descritivos via `TABELA_LABELS` →
  `indicador_tabela` ("Força de trabalho e informalidade", "Rendimento médio",
  "Rendimento por nível de instrução").

## 14. Agregações realizadas

> Implementado em `notebooks/03_tratamento_pm3.ipynb`, seção "12. Agregação de
> dados".

- Tabela `rendimento_anual`: rendimento médio anual (`valor_imputado`, tabela
  5436) por `uf_nome` + `sexo` + `ano` (30 linhas: 3 UFs × 2 sexos × 5 anos —
  2021 ausente pela lacuna da tabela 5436).
- **Interpretação:** entre 2020 e 2025, o rendimento cresce em todas as
  UFs/sexos (PR Fem. +15,3%/Masc. +11,7%; RS Fem. +15,7%/Masc. +10,6%; SC Fem.
  +19,4%/Masc. +18,8%). O gap salarial converge levemente em PR (37,3%→33,1%) e RS
  (37,6%→31,6%), mas permanece praticamente estável em SC (~31%).

## 15. Normalização/padronização

> Implementado em `notebooks/03_tratamento_pm3.ipynb`, seção "13. Normalização e
> padronização".

- `MinMaxScaler` (scikit-learn) aplicado a `valor_imputado`, separado por
  `(tabela_id, variavel_nome)`, gerando `valor_normalizado` em `[0, 1]`.
- Min-Max escolhido em vez de `StandardScaler` por colocar todos os indicadores na
  mesma escala `[0,1]`, facilitando comparações visuais entre indicadores de
  unidades diferentes (pessoas, %, R$).

## 16. Discretização

> Implementado em `notebooks/03_tratamento_pm3.ipynb`, seção "14. Discretização
> dos dados".

- `faixa_rendimento` (baixo/médio/alto) criada via `pd.qcut` (tercis) sobre
  `valor_imputado` da tabela 5436 — divisão de 32/32/32 linhas.
- `"Não se aplica"` para as demais tabelas (4093, 7322), que não representam
  rendimento individual.

## 17. Feature Engineering

> Implementado em `notebooks/03_tratamento_pm3.ipynb`, seção "15. Feature
> Engineering".

- `gap_salarial_pct`: `(rendimento_Masculino - rendimento_Feminino) /
  rendimento_Feminino * 100`, calculado por UF/período via `pivot_table` de
  `sexo` e reanexado a `df_sel` (mesmo valor para Masc./Fem. de cada UF/período).
- Demais features derivadas consolidadas: `ano`, `trimestre`, `periodo_label`
  (seção 13 deste relatório), `indicador_tabela` (seção 13), `valor_normalizado`
  (seção 15), `faixa_rendimento` (seção 16), `is_outlier` (seção 12).

## 18. Dataset final

> Implementado em `notebooks/03_tratamento_pm3.ipynb`, seção "16. Consolidação do
> dataset final".

- `dados/gold/pnad_tratado_final.csv`: **448 linhas × 17 colunas**:
  `tabela_id, uf_nome, regiao_nome, sexo, nivel_instrucao, variavel_nome,
  unidade_medida, valor, ano, trimestre, periodo_label, valor_imputado,
  is_outlier, indicador_tabela, valor_normalizado, faixa_rendimento,
  gap_salarial_pct`.
- Diferente do bronze (JSON por tabela, sem filtro nem colunas derivadas) e do
  silver (`pnad_limpo.csv`, 5.920×15, sem as colunas tratadas/derivadas).

## 19. Catálogo de dados

> Catálogo completo em `docs/catalogo_dados.md` — tabela com
> `coluna | descrição | tipo | exemplo | origem | tratamento aplicado | uso esperado`
> para todas as 17 colunas do dataset final, mais observações gerais sobre o
> recorte etário inconsistente, a lacuna temporal da tabela 5436 e a categoria
> "Total" da tabela 7322.

## 20. DataOps

> Implementado em `README.md`, `.gitignore` e
> `notebooks/03_tratamento_pm3.ipynb` (seção "18. DataOps e organização do
> projeto").

- `README.md`: estrutura de pastas, ordem de execução do pipeline (`01_coleta.ipynb`
  → `02_silver.ipynb` → `03_tratamento_pm3.ipynb`) e localização dos entregáveis.
- `.gitignore`: `dados/bronze/` e `dados/gold/` versionados como
  entregáveis/evidência do PM3; `dados/silver/` permanece ignorado (intermediário,
  regenerável).
- Notebook de tratamento executado do início ao fim sem erros (78 células).

## 21. Conclusão

O processo de tratamento transformou uma base bruta de 5.920 linhas × 15 colunas,
com múltiplos indicadores empilhados, períodos codificados e valores ausentes não
documentados, em um dataset final de 448 linhas × 17 colunas — limpo, documentado,
com período legível, valores imputados, normalizados, discretizados e enriquecido
com a feature derivada `gap_salarial_pct`. Os achados confirmam que o gap salarial
entre homens e mulheres na Região Sul é persistente (30%–39%), apresenta leve
convergência em PR e RS mas não em SC, e não é explicado por diferenças de
escolaridade — mulheres têm, em média, mais "Superior completo" que homens nas três
UFs.

## 22. Limitações

- A tabela 5436 (rendimento) não possui dados para 2020T2–2022T1, o que limita
  análises de evolução do gap salarial durante o pico da pandemia.
- O recorte etário difere entre tabelas (14+ anos em 4093/5436 vs. 10+ anos em
  7322), impedindo comparações diretas de totais populacionais entre essas
  tabelas.
- A imputação por média de grupo (`valor_imputado`) é uma aproximação — não
  reflete a real flutuação econômica do período de pandemia, apenas preenche a
  lacuna para fins de continuidade analítica.
- A categoria "Total" da tabela 7322 (8 outliers) deve ser excluída em análises que
  somem níveis de instrução individualmente, sob risco de dupla contagem.

## 23. Próximos passos

- Coletar dados de 2026 em diante para manter o dataset atualizado em um pipeline
  incremental.
- Adicionar a dimensão faixa etária (classificação C58 do SIDRA) à tabela 7322 para
  permitir cruzamentos com idade.
- Construir um dashboard de BI (Power BI/Looker Studio) consumindo diretamente
  `dados/gold/pnad_tratado_final.csv`, com filtros por UF, sexo, período e
  indicador.
- Explorar modelos de previsão (séries temporais) para `gap_salarial_pct` e
  `valor_imputado` por UF, e clustering de UF/trimestre usando `valor_normalizado`
  dos diferentes indicadores.
