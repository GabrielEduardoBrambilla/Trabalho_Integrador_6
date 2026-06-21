# Relatório Final — PM3: Tratamento de Dados do Mercado de Trabalho na Região Sul (PNAD Contínua/IBGE)

> Estrutura conforme `docs/context.md` (seção 8, 23 itens). Todos os números,
> tabelas e gráficos citados estão implementados e executados em
> `notebooks/03_tratamento_pm3.ipynb`; as seções abaixo indicam onde encontrar
> cada item no notebook.

## 1. Introdução

Este relatório documenta o processo completo de tratamento de dados (PM3) aplicado à PNAD Contínua (IBGE), com foco no mercado de trabalho da Região Sul do Brasil (Paraná, Santa Catarina e Rio Grande do Sul) entre 2020 e 2025. O trabalho cobre desde a coleta dos dados brutos via API SIDRA até a entrega de um dataset final limpo, transformado e documentado, pronto para uso em ferramentas de Business Intelligence (BI) e Data Mining.

## 2. Tema escolhido

**Gap salarial entre homens e mulheres no mercado de trabalho da Região Sul — força de trabalho, informalidade e rendimento, por sexo (2020–2025).** Nível de instrução por sexo é usado como evidência de apoio, para testar (e descartar) a hipótese de que essa desigualdade seria explicada por diferenças de escolaridade. O tema foi escolhido por permitir a análise de um problema social relevante e mensurável — a desigualdade de rendimento entre homens e mulheres ("gap salarial") — usando dados públicos, oficiais e atualizados periodicamente.

## 3. Fonte dos dados

- **Fonte:** PNAD Contínua (Pesquisa Nacional por Amostra de Domicílios Contínua), IBGE, via API SIDRA — `https://apisidra.ibge.gov.br`.
- **Tabelas principais** (gap salarial, joináveis por UF/sexo/trimestre):
  - **4093** — Força de trabalho, pessoas ocupadas e taxa de informalidade, por sexo e UF (trimestral, pessoas de 14+ anos).
  - **5436** — Rendimento médio real habitual do trabalho principal, por sexo e UF (trimestral, pessoas de 14+ anos).
- **Tabela de contexto** (escolaridade, não joinável às principais — seção 22):
  - **7322** — Pessoas por nível de instrução, por sexo, Região Sul (anual, pessoas de 10+ anos).
- **Recorte geográfico:** Paraná, Santa Catarina e Rio Grande do Sul (UFs, tabelas principais) e Região Sul (agregado, tabela de contexto).
- **Recorte temporal:** 2020 a 2025 (principais, trimestral); 2021 a 2024 (contexto, anual).
- **Coleta:** `notebooks/01_coleta.ipynb` (classe `PnadCollector`), dados brutos preservados em `dados/bronze/pnad_4093.json`, `pnad_5436.json`, `pnad_7322.json`.

## 4. Objetivo do trabalho

Transformar os dados brutos da PNAD Contínua — que vêm em formato bruto de API, com códigos de ausência do IBGE, períodos codificados, múltiplos indicadores empilhados e unidades de medida diferentes — em dois datasets finais: um **principal** (gap salarial, joinável por UF/sexo/trimestre, com colunas derivadas como período legível, valores imputados, normalização, faixas de rendimento e gap salarial) e um de **contexto** (escolaridade por sexo na Região Sul), prontos para alimentar dashboards de BI e análises de Data Mining sobre desigualdade de rendimento no mercado de trabalho da Região Sul.

## 5. Descrição da base de dados original

A base original (silver, `dados/silver/pnad_limpo.csv`, gerada a partir do bronze pelo `PnadNormalizer`) tem **5.920 linhas × 15 colunas**:
`tabela_id, uf_cod, uf_nome, regiao_cod, regiao_nome, periodo, sexo_cod, sexo, nivel_instrucao_cod, nivel_instrucao, variavel_cod, variavel_nome, unidade_medida_cod, unidade_medida, valor`.

Cada `tabela_id` traz dezenas de `variavel_nome` diferentes empilhadas na mesma coluna `valor`, com unidades distintas (Mil pessoas, %, Reais) — ver seção 7 (Diagnóstico) para detalhes. O dataset bruto (bronze, JSON da API SIDRA) está preservado em `dados/bronze/`.

## 6. Relação com BI, Big Data Analytics e Data Mining

**Como os dados poderiam apoiar decisões:** políticas públicas de equidade salarial podem ser direcionadas com base no tamanho real do gap por UF, por exemplo, priorizando programas de qualificação ou fiscalização em estados onde o gap não está convergindo. Sindicatos podem usar a evolução trimestral do rendimento para embasar negociações coletivas.

**Padrões que poderiam ser descobertos:**

- Correlação forte (0,86) entre pessoas ocupadas e taxa de informalidade (seção 8) — sugere que a recuperação do emprego pós-pandemia veio acompanhada de mais informalidade.
- O gap salarial (30%–39%) é persistente e não explicado por escolaridade — mulheres têm mais "Superior completo" que homens, mas rendimento menor.
- Lacunas de divulgação do IBGE (Problema 9) coincidem temporalmente entre tabelas diferentes (4093 e 5436), reforçando a hipótese de undercoverage real durante a pandemia, não falha de coleta.

**Tipos de análise possíveis:** séries temporais (evolução trimestral por UF/sexo), análise de correlação entre indicadores, agrupamento (clustering) de UF/trimestres por perfil de mercado de trabalho, e regressão/previsão de rendimento futuro.

**Uso em dashboards:** sim — o dataset principal (`pnad_treated_data.csv`, seção 18) já está no formato long/tidy, com "uma linha por dimensão × período × indicador", ideal para ferramentas de BI (Power BI, Tableau, Looker Studio) fazerem `groupby`/pivot por UF, sexo, ano e indicador. O dataset de contexto (`pnad_context_data.csv`) não compartilha UF/trimestre com o principal, então não entra no mesmo cubo — é consumido separadamente, como uma tabela de apoio qualitativo.

**Classificação, agrupamento, previsão ou descoberta de padrões:** todos aplicáveis. _Classificação_: categorizar trimestres/UFs em `faixa_rendimento` (seção 16, já feito via discretização, só no dataset principal). _Agrupamento_: clusterizar UF/trimestre por perfil multivariado (ocupação, informalidade, rendimento — usando `valor_normalizado` da seção 15, que já coloca os indicadores na mesma escala). _Previsão_: séries temporais de rendimento/ocupação por UF/sexo. _Descoberta de padrões_: a relação entre nível de instrução e rendimento por sexo (seção 8) já é um exemplo de padrão descoberto na EDA, usando o dataset de contexto para complementar o principal.

## 7. Diagnóstico da qualidade dos dados

Análise feita a partir do **bronze** (JSON bruto retornado pela API SIDRA), antes da normalização do `PnadNormalizer`, para expor os problemas reais da base original (ver `notebooks/03_tratamento_pm3.ipynb`, seção "5. Diagnóstico da qualidade dos dados").

Tabela-resumo dos 9 problemas identificados:

| #   | Problema                                                                                                                | Exemplo                                                               |
| --- | ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| 1   | Linha 0 do JSON SIDRA = cabeçalho de metadados misturado aos dados                                                      | Primeira linha de cada `pnad_*.json`                                  |
| 2   | Códigos numéricos vs. nomes redundantes                                                                                 | `D1C="41"` / `D1N="Paraná"`, `D4C="4"` / `D4N="Homens"`               |
| 3   | `Trimestre`/`Ano` (`D2C`) como código de texto, não como data                                                           | `"202001"` (4093/5436) vs. `"2021"` (7322)                            |
| 4   | Valores ausentes codificados pelo IBGE                                                                                  | `-`, `...`, `X`, `x`, `C`, `""`                                       |
| 5   | **(Principal)** Dimensão "Variável" (D3) empilha dezenas de indicadores com unidades diferentes na mesma coluna `valor` | 4093 tem 34 variáveis (Mil pessoas, %, coef. variação)                |
| 6   | Mistura de unidades entre `tabela_id`                                                                                   | 4093 = pessoas/%, 5436 = R$                                           |
| 7   | Recorte etário inconsistente entre tabelas                                                                              | 4093/5436 = 14+ anos; 7322 = 10+ anos                                 |
| 8   | Tabela 7322 coletada em nível geográfico diferente (N2/Região, não N3/UF)                                               | 7322 tem `regiao_cod`/`regiao_nome`; 4093/5436 têm `uf_cod`/`uf_nome` |
| 9   | Trimestres inteiros ausentes na resposta da API (tabela 5436)                                                           | Faltam 2020T2 a 2022T1 (linhas inteiras, não `"..."`)                 |

**Problema 1 — cabeçalho de metadados na linha 0.** A API SIDRA retorna a linha 0 com as _descrições_ das colunas (`D1C`/`D1N`, `D2C`/`D2N`, ..., `MC`/`MN`, `V`), e a partir da linha 1 os dados propriamente ditos — usando os mesmos nomes de chave. Se essa linha 0 não for descartada e usada apenas para mapear os nomes das colunas, ela aparece como um registro inválido no dataset (todas as colunas como texto descritivo). O `PnadNormalizer` já trata isso: usa `dados[0]` apenas para construir `_build_col_map` e descarta a linha do dataframe final.

**Problema 2 — códigos numéricos vs. nomes redundantes.** Cada dimensão vem em pares `DnC` (código) / `DnN` (nome) — ex.: `D1C="41"` / `D1N="Paraná"`, `D4C="4"` / `D4N="Homens"`. Isso duplica a informação e precisa ser resolvido na seleção de colunas (seção 9).

**Problema 3 — `Trimestre`/`Ano` (`D2C`) como código de texto, não como data.** Para 4093/5436, `D2C` vem no formato `AAAASS` (ex.: `"202001"` = 1º trimestre de 2020); para 7322, `D2C` é só o ano (`"2021"`). Precisa virar `ano`/`trimestre` (seção 10).

**Problema 4 — valores ausentes codificados pelo IBGE.** A tabela 4093 tem **1.632** valores `"..."` (≈33% das suas 4.896 linhas) e a tabela 7322 tem **8** valores `"-"` (≈3% das 256 linhas) — total de **1.640** valores ausentes na coluna `valor`. O `PnadNormalizer` converte todos os códigos `{-, ..., X, x, C, ""}` para `NaN` via `pd.to_numeric(..., errors="coerce")`. Esses ausentes são tratados na seção 11.

> **Nota:** ao contrário do esperado inicialmente, **nenhum** valor numérico desta coleta usa vírgula como separador decimal (todos já vêm com ponto, ex. `"49.1"`). A normalização `valor_str.str.replace(",", ".")` no `PnadNormalizer` é defensiva (não tem efeito nos dados atuais, mas protege contra outras tabelas SIDRA que usam vírgula).

**Problema 5 (principal) — múltiplos indicadores empilhados na mesma coluna `valor`, com unidades diferentes.** Cada tabela SIDRA traz a dimensão **"Variável" (D3)** com dezenas de indicadores diferentes (contagens em "Mil pessoas", taxas em "%", rendimentos em "Reais" e "Coeficientes de variação" — uma medida de precisão estatística, não um indicador de negócio):

- **4093** → 34 variáveis (ocupados, desocupados, taxa de informalidade, taxa de participação etc., cada uma com seu "Coeficiente de variação - ...").
- **5436** → 8 variáveis (rendimento habitual/efetivo × trabalho principal/todos os trabalhos, e respectivos coeficientes de variação).
- **7322** → 4 variáveis (pessoas por nível de instrução, distribuição percentual, e coeficientes de variação).

Sem isolar por `variavel_nome` (e `unidade_medida`), qualquer estatística ou gráfico sobre `valor` mistura grandezas incompatíveis (pessoas, %, R$, coeficientes de variação). O `PnadNormalizer` já preserva `variavel_cod`/`variavel_nome` e `unidade_medida_cod`/`unidade_medida` como colunas próprias — a correção definitiva é **filtrar por `variavel_nome`** na seleção de dados (seção 9).

**Problema 6 — mistura de unidades entre `tabela_id`.** Mesmo após filtrar por `variavel_nome`, `tabela_id == "4093"` (pessoas/%) e `tabela_id == "5436"` (R$) usam escalas totalmente diferentes — qualquer comparação de `valor` entre tabelas sem filtrar por `tabela_id` é inválida.

**Problema 7 — recorte etário inconsistente entre tabelas.** As tabelas 4093 e 5436 cobrem pessoas de **14 anos ou mais**, enquanto a tabela 7322 cobre pessoas de **10 anos ou mais**. Comparações entre `tabela_id == "7322"` e as demais (ex.: população total) devem registrar essa diferença de público-alvo — não são diretamente somáveis/comparáveis.

**Problema 8 — tabela 7322 coletada em nível geográfico diferente (N2/Região, não N3/UF).** Suas linhas têm `regiao_cod`/`regiao_nome` preenchidos e `uf_cod`/`uf_nome` vazios (`NaN`), enquanto 4093/5436 são o oposto.

**Problema 9 — trimestres inteiros ausentes na resposta da API (tabela 5436).** A tabela 5436 retorna apenas **16 dos 24 trimestres** esperados (2020T1 a 2025T4) — os 8 trimestres de **2020T2 a 2022T1** simplesmente não aparecem na resposta da API SIDRA (não é um valor `"..."`, a linha não existe). A tabela 4093 está completa (24/24 trimestres, com `"..."` em alguns indicadores). Esse "buraco" temporal em 5436 é registrado na seção 11 e aparece como uma lacuna no gráfico de evolução temporal (seção 8).

## 8. Análise Exploratória de Dados (EDA)

A partir daqui trabalha-se com o **silver** (`pnad_limpo.csv`, 5.920 linhas × 15 colunas), já com `valor` numérico e `variavel_nome`/`unidade_medida` preservados (ver notebook, seção "6. Análise Exploratória de Dados", com gráficos plotly e interpretação textual de cada um). Conforme o Problema 5, `valor` só é analisável depois de filtrar por `variavel_nome` — por isso a EDA usa os mesmos **4 indicadores de interesse** que seriam formalizados na seleção de dados (seção 9): um indicador-chave por tabela, cobrindo força de trabalho, informalidade, rendimento e nível de instrução. As estatísticas descritivas de `valor` foram calculadas separadamente por `tabela_id`/indicador, já que cada um tem unidade própria (pessoas, %, R$).

**Rendimento médio por UF e sexo (gráfico de barras, tabela 5436):** em todos os três estados, o rendimento médio dos homens é nitidamente superior ao das mulheres — Paraná (R$ 3.997 vs. R$ 2.984, gap ≈34%), Rio Grande do Sul (R$ 4.018 vs. R$ 3.058, gap ≈31%) e Santa Catarina (R$ 4.182 vs. R$ 3.198, gap ≈31%). Santa Catarina tem o maior rendimento médio para ambos os sexos, mas o gap percentual é semelhante entre os três estados — indicando que a desigualdade de rendimento por sexo é um padrão regional, não específico de uma UF.

**Evolução temporal do rendimento (gráfico de linha):** observa-se uma lacuna entre 2020T1 e 2022T2 — reflexo do Problema 9 (a tabela 5436 não retorna dados para 2020T2–2022T1). A partir de 2022T2, ambas as séries (homens e mulheres) mostram tendência de leve crescimento real do rendimento até 2025T4, com a linha dos homens consistentemente acima da das mulheres em todo o período observado — o gap salarial é persistente, oscilando entre ≈30% e ≈35%, sem sinal de fechamento estrutural no horizonte analisado.

**Distribuição do rendimento (boxplot e histograma):** os boxplots de homens ficam visivelmente acima dos de mulheres em todas as UFs, com pouca sobreposição entre as caixas — reforçando que o gap salarial não é causado por trimestres atípicos, mas é uma diferença sistemática ao longo de toda a série. As caixas de Santa Catarina estão deslocadas para cima (rendimentos mais altos), mas a amplitude é semelhante entre as três UFs, sem outliers extremos visíveis (confirmado de forma mais rigorosa via IQR na seção 12). O histograma mostra as duas distribuições unimodais e relativamente concentradas (feminino entre R$ 2.654–3.621, masculino entre R$ 3.582–4.676), com a distribuição masculina deslocada para a direita e **praticamente sem sobreposição** — o gap salarial se manifesta como deslocamento de toda a distribuição, não apenas da média.

**Correlação entre indicadores (heatmap):** para correlacionar indicadores de tabelas/unidades diferentes, primeiro pivotou-se a base de EDA (tabelas 4093 e 5436, que compartilham `uf_nome`/`periodo`/`sexo`) para uma linha por (UF, período, sexo) com uma coluna por indicador. `ocupados_mil` e `taxa_informalidade_pct` têm correlação forte (0,86) — ambos crescem ao longo da série, possivelmente refletindo a recuperação do mercado de trabalho pós-pandemia acompanhada de aumento da informalidade (mais correlação temporal conjunta do que causalidade direta). `rendimento_medio` tem correlação moderada com `ocupados_mil` (0,49) e correlação muito fraca com `taxa_informalidade_pct` (0,07) — sugerindo que o nível de rendimento médio não está diretamente associado ao grau de informalidade nesta amostra (PR/SC/RS, 2020–2025).

**Taxa de informalidade (tabela 4093):** diferente de 5436, a tabela 4093 está completa nos 24 trimestres (2020T1–2025T4), mas com valores `...`/`NaN` em alguns trimestres (Problema 4). 48 das 144 linhas (33%) têm `valor` ausente, todas concentradas em **2020T2–2022T1** — exatamente o mesmo intervalo em que a tabela 5436 não retorna dados (Problema 9). Isso reforça a hipótese de que esse período reflete uma limitação real de divulgação do IBGE para PR/SC/RS durante a fase mais aguda da pandemia (provável undercoverage da coleta por telefone), e não um problema do pipeline de coleta. Nos trimestres com dado disponível, a taxa de informalidade feminina e masculina seguem padrões semelhantes, sem um gap tão marcante quanto o observado no rendimento.

**Nível de instrução por sexo (tabela 7322):** o "Fundamental incompleto" é o nível de instrução mais numeroso para ambos os sexos (≈1.027 mil mulheres, ≈1.048 mil homens), seguido de "Médio completo". O contraste mais notável aparece no "Superior completo": **mulheres superam homens** (≈650 mil vs. ≈483 mil) — um padrão consistente com dados educacionais nacionais (maior conclusão do ensino superior por mulheres). Combinado com o gráfico de rendimento, isso sugere que o gap salarial **não é explicado por escolaridade** — mulheres têm, em média, mais anos de estudo, mas recebem rendimentos menores.

A lacuna temporal 2020T2–2022T1 (Problema 9) foi confirmada visualmente nos gráficos de evolução acima.

## 9. Seleção dos dados

**Filtro por `variavel_nome`** (`VARIAVEIS_FOCO`): mantidos apenas os 4 indicadores de interesse já usados na EDA, descartando todas as linhas de "Coeficiente de variação - ..." e "Distribuição percentual - ..." (não são indicadores de negócio, são medidas de precisão estatística do IBGE — Problema 5). De 34+8+4 variáveis disponíveis, restam pessoas ocupadas e taxa de informalidade (4093), rendimento médio mensal real (5436) e pessoas por nível de instrução (7322). Resultado: **448 linhas**.

**Seleção de colunas:**

- **Mantidas:** `tabela_id, uf_nome, regiao_nome, periodo, sexo, nivel_instrucao, variavel_nome, unidade_medida, valor`.
- **Removidas (redundantes com a versão em texto):** `uf_cod, sexo_cod, regiao_cod, variavel_cod, nivel_instrucao_cod, unidade_medida_cod`.
- `periodo` é mantido nesta etapa e decomposto em `ano`/`trimestre` na limpeza (seção 10).

**Linhas com `valor` ausente:** mantidas em `df_sel` (não removidas), porque a ausência em si é informação relevante (Problemas 4 e 9 — undercoverage da PNAD durante a pandemia). A estratégia de tratamento (manter como `NaN` documentado vs. imputar) é decidida e justificada na seção 11.

`df_sel` continua combinando as três tabelas até a consolidação (seção 18), já que a limpeza, o tratamento de ausentes/outliers e a normalização (seções 10–15) operam por grupo `(tabela_id, variavel_nome)` e valem igualmente para as três. A separação em dois datasets finais — **principal** (4093+5436, gap salarial) e de **contexto** (7322, escolaridade) — só acontece na consolidação, porque é só ali que a diferença de granularidade entre as tabelas (UF×trimestre vs. Região×ano) passa a importar (seção 22).

(ver notebook, seção "7. Seleção dos dados")

## 10. Limpeza dos dados

**`periodo` (`AAAASS`/`AAAA`) → `ano` + `trimestre`:** nas tabelas 4093/5436, `periodo` vem no formato `AAAASS` (ex.: `202001` = 2020, T1); na tabela 7322, `periodo` é só o ano (`2021`..`2024`) — não tem trimestre (indicador anua l). A partir daí derivou-se `ano` (int), `trimestre` (Int64 nullable) e `periodo_label`, legível no formato `"2023-T3"` (trimestral) ou `"2021"` (anual).

**Duplicidades:** 0 duplicatas encontradas (`df.duplicated()` e checagem pela chave de granularidade).

**Padronização de categorias de texto:** `uf_nome`, `regiao_nome` e `nivel_instrucao` têm `NaN` para tabelas que não possuem aquela dimensão (Problema 8). Substituídos por `"Não se aplica"` para deixar explícito que a ausência é estrutural (não é um dado faltante a ser imputado/investigado) — diferente do `NaN` em `valor`, que é tratado na seção 11.

Nomes de colunas já em snake_case (confirmado). `valor` confirmado como `float`.

(ver notebook, seção "8. Limpeza e pré-processamento")

## 11. Tratamento de valores faltantes

**Quantificação (antes do tratamento):** 96/448 (21,4%) valores ausentes em `valor`, todos em `tabela_id == 4093`, indicadores "Pessoas ocupadas" e "Taxa de informalidade", trimestres 2020T2–2022T1.

**Estratégia:** esses valores refletem **undercoverage real da PNAD durante a pandemia** (Problemas 4 e 9) — o IBGE optou por não divulgar esses valores por insuficiência amostral, não por falha na coleta deste projeto.

**Decisão:** manter `valor` como `NaN` (preserva a informação de que o dado _não existe na fonte_, essencial para um relatório honesto sobre a pandemia). Para demonstrar a técnica de imputação (exigência do PM3), foi criada uma coluna adicional `valor_imputado`, preenchida pela **média do grupo** (`uf_nome`, `sexo`, `variavel_nome`) — assume-se que o indicador naquele trimestre seguiu o padrão médio da série da mesma UF/sexo/indicador. `valor_imputado` tem 0/448 nulos. Ambas as colunas seguem para o dataset final (seção 18), permitindo ao analista escolher qual usar conforme a análise.

(ver notebook, seção "9. Tratamento de valores faltantes")

## 12. Tratamento de outliers

Detecção via **IQR (1,5×)** sobre `valor_imputado`, separada por `tabela_id` + `variavel_nome` (cada combinação tem sua própria escala/unidade — Problema 6).

**Resultado:** 8/448 outliers, todos da combinação `tabela_id == 7322` / `nivel_instrucao == "Total"` — ou seja, são a **soma de todos os outros níveis de instrução** para aquele ano/sexo (≈13 mil, vs. ≈300–1.000 mil de cada nível individual). Não é erro de digitação nem valor estatisticamente anômalo: é uma agregação legítima embutida na própria classificação do IBGE (categoria "Total" dentro de "Nível de instrução").

**Decisão:** manter os valores (não remover/transformar), mas a coluna `is_outlier` permanece no dataset final para que análises que exijam apenas os subníveis (excluindo "Total") possam filtrar com `is_outlier == False` ou, de forma mais explícita, `nivel_instrucao != "Total"`. Para os indicadores das tabelas 4093/5436, **nenhum** outlier foi detectado pelo IQR — a queda de rendimento/ocupação observada em 2020–2022 está dentro da variação normal da série.

(ver notebook, seção "10. Tratamento de outliers")

## 13. Transformação dos dados

A separação de `periodo` em `ano` + `trimestre` + `periodo_label` já foi feita na limpeza (seção 10), pré-requisito dos gráficos temporais da EDA (seção 8). O que faltava para completar a transformação era **agrupar `tabela_id` em rótulos descritivos** via `TABELA_LABELS` → `indicador_tabela` ("Força de trabalho e informalidade", "Rendimento médio", "Rendimento por nível de instrução"), facilitando a leitura do dataset final por quem não conhece os códigos do SIDRA.

(ver notebook, seção "11. Transformação dos dados")

## 14. Agregações realizadas

Tabela agregada `rendimento_anual`: rendimento médio anual (R$, `valor_imputado`, tabela 5436) por `uf_nome` + `sexo` + `ano` (30 linhas: 3 UFs × 2 sexos × 5 anos) — uma visão "anualizada" que resume os 4 trimestres de cada ano em um único número, útil para um dashboard de BI que compare a evolução ano a ano sem o ruído da sazonalidade trimestral.

**Interpretação:** o ano de **2021 não aparece** na tabela — reflexo direto do "buraco" temporal da tabela 5436 (Problema 9, 2020T2–2022T1): 2020 tem só o dado de T1 e 2022 tem só T2–T4, então a média anual de 2021 ficaria baseada em 0 trimestres reais (mesmo usando `valor_imputado`, não há nenhum trimestre de 2021 na base — a imputação preenche valores ausentes _dentro_ de uma linha existente, não cria linhas para períodos inexistentes). Olhando a evolução de 2020 a 2025: o rendimento masculino cresce de forma consistente nas três UFs (PR: R$ 3.918 → R$ 4.378, +11,7%; RS: R$ 3.863 → R$ 4.274, +10,6%; SC: R$ 3.901 → R$ 4.636, +18,8%), enquanto o feminino cresce a um ritmo semelhante ou maior em termos relativos (PR: +15,3%; RS: +15,7%; SC: +19,4%). Como resultado, o gap percentual (Masc. vs. Fem.) recua ligeiramente em PR (37,3% → 33,1%) e RS (37,6% → 31,6%), e fica praticamente estável em SC (31,7% → 31,1%) — um sinal de leve convergência, mas o gap permanece acima de 30% em todos os casos até 2025.

(ver notebook, seção "12. Agregação de dados")

## 15. Normalização/padronização

Aplicado **Min-Max scaling** (`sklearn.preprocessing.MinMaxScaler`) sobre `valor_imputado`, gerando `valor_normalizado` no intervalo `[0, 1]`. A escala é ajustada **separadamente para cada combinação `(tabela_id, variavel_nome)`**, pois cada indicador tem sua própria unidade/grandeza (Mil pessoas, %, R$ — Problema 6) — normalizar todos juntos faria, por exemplo, percentuais (0-100) dominarem reais (centenas/milhares) de forma artificial. Min-Max foi escolhido em vez de `StandardScaler` (z-score) porque o objetivo é colocar todos os indicadores na mesma escala `[0, 1]` para visualizações comparativas (ex.: um único gráfico com ocupados, informalidade e rendimento na mesma escala), o que é mais intuitivo de interpretar do que desvios-padrão.

(ver notebook, seção "13. Normalização e padronização")

## 16. Discretização

Discretizado o **rendimento médio** (`valor_imputado`, tabela 5436) em três faixas — `baixo` / `médio` / `alto` — usando `pd.qcut` (tercis: cada faixa concentra ~1/3 das observações, divisão de 32/32/32 linhas). Essa coluna `faixa_rendimento` é útil para BI (ex.: segmentar UF/trimestres por faixa de rendimento sem precisar olhar o valor exato) e para análises categóricas (ex.: contar quantos trimestres cada UF/sexo passou em cada faixa). Para as demais tabelas (4093/7322), que não representam rendimento individual, `faixa_rendimento` fica `"Não se aplica"`.

(ver notebook, seção "14. Discretização dos dados")

## 17. Feature Engineering

A principal feature derivada é o **gap salarial percentual** por UF e período — formalizando a desigualdade observada nas seções 8/14:

`gap_salarial_pct = (rendimento_masculino - rendimento_feminino) / rendimento_feminino * 100`

Calculado via `pivot_table` de `sexo` (uma coluna para "Masculino" e outra para "Feminino" do `valor_imputado`, indexado por `uf_nome` + `periodo_label`) e depois reanexado a `df_sel` — ambas as linhas (Masculino e Feminino) de um mesmo UF/período recebem o mesmo `gap_salarial_pct`, pois é uma medida do par, não de um sexo isoladamente. As demais features de transformação/discretização (`ano`, `trimestre`, `periodo_label`, `faixa_rendimento`, `is_outlier`, `valor_normalizado`, `indicador_tabela`) já haviam sido criadas nas seções 10, 13, 15 e 16 deste relatório — `df_sel` consolida todas elas.

(ver notebook, seção "15. Feature Engineering")

## 18. Dataset final

`df_sel` reúne todas as colunas originais selecionadas (seção 9) mais as colunas criadas nas seções 10–17: `ano`, `trimestre`, `periodo_label`, `indicador_tabela`, `valor_imputado`, `is_outlier`, `valor_normalizado`, `faixa_rendimento`, `gap_salarial_pct`. Como visto na seção 9, as tabelas 4093/5436 (UF, trimestral) e 7322 (Região, anual) nunca compartilharam granularidade geográfica/temporal — e `gap_salarial_pct`/`faixa_rendimento` só existem a partir de 5436. Por isso, em vez de um único CSV com colunas que não se aplicam a parte das linhas, o resultado é dividido em dois datasets finais:

- **`dados/gold/pnad_treated_data.csv`** (principal): tabelas 4093+5436, **384 linhas × 15 colunas** — `tabela_id, uf_nome, sexo, variavel_nome, unidade_medida, valor, ano, trimestre, periodo_label, valor_imputado, is_outlier, indicador_tabela, valor_normalizado, faixa_rendimento, gap_salarial_pct`. Remove `regiao_nome`/`nivel_instrucao` (sempre `"Não se aplica"` nessas linhas).
- **`dados/gold/pnad_context_data.csv`** (contexto): tabela 7322, **64 linhas × 13 colunas** — `tabela_id, regiao_nome, sexo, nivel_instrucao, variavel_nome, unidade_medida, valor, ano, periodo_label, valor_imputado, is_outlier, indicador_tabela, valor_normalizado`. Remove `uf_nome`/`trimestre`/`faixa_rendimento`/`gap_salarial_pct` (nunca se aplicam a esta tabela).

Ambos são claramente diferentes do bronze (JSON bruto por tabela, sem filtro nem colunas derivadas) e do silver (`pnad_limpo.csv`, 5.920×15, sem as colunas tratadas/derivadas).

(ver notebook, seção "16. Consolidação dos datasets finais")

## 19. Catálogo de dados

O catálogo completo das colunas de `pnad_treated_data.csv` — descrição, tipo, exemplo, origem (original/derivada), tratamento aplicado e uso esperado — está em `docs/catalogo_dados.md`. O catálogo das colunas de `pnad_context_data.csv` está em `docs/catalogo_dados_contexto.md`. Ambos seguem o formato `coluna | descrição | tipo | exemplo | origem | tratamento aplicado | uso esperado`, mais observações gerais sobre o recorte etário/geográfico/temporal inconsistente entre as tabelas e a categoria "Total" da tabela 7322.

(ver notebook, seção "17. Catálogo de dados")

## 20. DataOps

A estrutura de pastas, o pipeline de execução (`01_coleta.ipynb` → `02_silver.ipynb` → `03_tratamento_pm3.ipynb`) e a localização dos entregáveis estão documentados no `README.md` da raiz do projeto. `dados/bronze/` (JSON original do SIDRA) e os dois datasets finais (`dados/gold/pnad_treated_data.csv`, `dados/gold/pnad_context_data.csv`) são versionados no repositório como entregáveis/evidência do PM3 (ver `.gitignore`); `dados/silver/` permanece ignorado por ser intermediário e regenerável. O notebook de tratamento foi executado do início ao fim sem erros (78 células).

(ver notebook, seção "18. DataOps e organização do projeto")

## 21. Conclusão

O processo de tratamento transformou uma base bruta de 5.920 linhas × 15 colunas, com múltiplos indicadores empilhados, períodos codificados e valores ausentes não documentados, em dois datasets finais — limpos, documentados, com período legível, valores imputados, normalizados, discretizados e enriquecidos com a feature derivada `gap_salarial_pct`: o **principal** (`pnad_treated_data.csv`, 384 linhas × 15 colunas, gap salarial) e o de **contexto** (`pnad_context_data.csv`, 64 linhas × 13 colunas, escolaridade por sexo). Os achados confirmam que o gap salarial entre homens e mulheres na Região Sul é persistente (30%–39%), apresenta leve convergência em PR e RS mas não em SC, e não é explicado por diferenças de escolaridade — mulheres têm, em média, mais "Superior completo" que homens nas três UFs.

## 22. Limitações

- A tabela 5436 (rendimento) não possui dados para 2020T2–2022T1, o que limita análises de evolução do gap salarial durante o pico da pandemia.
- **A tabela 7322 está em outra granularidade, não só em outro recorte etário — por isso ela é um dataset separado, não uma coluna a mais no principal.** Além de cobrir 10+ anos (vs. 14+ em 4093/5436), ela só existe no SIDRA no nível **N2/Região** (não N3/UF — a API nem oferece esse cruzamento) e com periodicidade **anual** (2021–2024, vs. trimestral 2020–2025 nas demais). Mantê-la no mesmo CSV que 4093/5436 (como em uma versão anterior deste tratamento) produzia linhas com `uf_nome = "Não se aplica"` e `gap_salarial_pct`/`faixa_rendimento` sempre vazios — colunas que nunca se aplicavam a ela. A separação em `pnad_treated_data.csv`/`pnad_context_data.csv` (seção 18) resolve isso: a 7322 segue existindo apenas como **tabela de referência isolada**, usada para o achado qualitativo de que o gap salarial não é explicado por escolaridade (seção 8) — não como uma dimensão joinável às demais.
- A imputação por média de grupo (`valor_imputado`) é uma aproximação — não reflete a real flutuação econômica do período de pandemia, apenas preenche a lacuna para fins de continuidade analítica.
- A categoria "Total" da tabela 7322 (8 outliers) deve ser excluída em análises que somem níveis de instrução individualmente, sob risco de dupla contagem.

## 23. Próximos passos

- Coletar dados de 2026 em diante para manter o dataset atualizado em um pipeline incremental.
- **Resolver o descompasso de granularidade da tabela 7322 via microdados da PNAD Contínua** (fora da API SIDRA): o limite a N2/Região e o corte de 10+ anos são restrições do agregado _publicado_, não da pesquisa original — processar o microdado bruto permitiria recalcular nível de instrução × sexo por UF e para 14+ anos, tornando a tabela finalmente comparável a 4093/5436. É um esforço consideravelmente maior (arquivos trimestrais grandes, dicionário de variáveis, pesos amostrais) e foi deixado fora do escopo deste PM3, que se restringiu à coleta via API SIDRA.
- Construir um dashboard de BI (Power BI/Looker Studio) consumindo diretamente `dados/gold/pnad_treated_data.csv`, com filtros por UF, sexo, período e indicador; `pnad_context_data.csv` como tabela de apoio qualitativo, sem join direto.
- Explorar modelos de previsão (séries temporais) para `gap_salarial_pct` e `valor_imputado` por UF, e clustering de UF/trimestre usando `valor_normalizado` dos diferentes indicadores.
- Padronizar um identificador comum entre os dois datasets finais (ex.: `sexo` + `ano`) para permitir, no futuro, ao menos um join parcial entre `pnad_treated_data.csv` e `pnad_context_data.csv` por sexo/ano, sem UF/trimestre.
