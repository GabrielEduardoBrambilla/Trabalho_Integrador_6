# Plano PM3 — Tratamento de Dados PNAD Contínua (IBGE)

Checklist de execução do PM3 baseado em `docs/context.md`, usando a base **PNAD Contínua
(IBGE)** como única fonte de dados (tabelas SIDRA 4093, 5436 e 7322 — PR/SC/RS,
2020–2025).

## 0. Visão geral

- **Tema:** Mercado de trabalho — rendimento, força de trabalho e participação por sexo,
  UF (PR/SC/RS) e período (2020–2025).
- **Fonte:** SIDRA/IBGE — `apisidra.ibge.gov.br`. Tabelas:
  - **4093** — Força de trabalho, ocupados, desocupados, informalidade por sexo (trimestral). (dados apartir de 14 anos de idade)
  - **5436** — Rendimento médio real por sexo (trimestral). (dados apartir de 14 anos de idade)
  - **7322** — Rendimento por sexo e nível de instrução, Região Sul (anual, N2). (dados apartir de 10 anos de idade)
- **Pipeline atual:**
  - Bronze (`coleta/coletar_pnad.py`, classe `PnadCollector`) ✅ executado —
    `dados/bronze/pnad_4093.json` (4.896 registros), `pnad_5436.json` (768),
    `pnad_7322.json` (256).
  - Silver (`silver/normalizar_pnad.py`, classe `PnadNormalizer`) ✅ executado —
    gera `dados/silver/pnad_limpo.csv`, 5.920 linhas × 15 colunas:
    `tabela_id, uf_cod, uf_nome, regiao_cod, regiao_nome, periodo, sexo_cod, sexo, nivel_instrucao_cod, nivel_instrucao, variavel_cod, variavel_nome, unidade_medida_cod, unidade_medida, valor`.
  - Gold / tratamento final 🔲 a fazer (este plano).

> ⚠️ **Achado crítico:** cada tabela SIDRA traz a dimensão **"Variável" (D3)** com
> múltiplos indicadores diferentes empilhados na mesma coluna `valor`, com unidades
> distintas (`unidade_medida`: "Mil pessoas", "%", "Reais"):
>
> - **4093** → 34 variáveis (ocupados, desocupados, taxa de informalidade, taxa de
>   participação, e um "Coeficiente de variação - ..." para cada uma).
> - **5436** → 8 variáveis (rendimento habitual/efetivo × trabalho principal/todos os
>   trabalhos, e respectivos coeficientes de variação).
> - **7322** → 4 variáveis (pessoas por nível de instrução, distribuição percentual, e
>   coeficientes de variação).
>
> Sem filtrar por `variavel_nome`, qualquer estatística/gráfico sobre `valor` mistura
> grandezas incompatíveis (pessoas, %, R$, coeficientes de variação). Isso já está
> capturado no silver atual (colunas `variavel_cod`, `variavel_nome`,
> `unidade_medida_cod`, `unidade_medida`) e **precisa ser tratado na seleção de dados
> (seção 7)** — é o principal "problema de qualidade" da base para o relatório (6.4).
> Os ~1.640 valores ausentes em `valor` (≈28%) concentram-se principalmente nas linhas
> "Coeficiente de variação - ..." (≈33% de nulos cada).

---

## 1. Planejamento do tratamento (context.md 6.1) ✅

- [x] Texto escrito cobrindo: tema, origem dos dados (SIDRA/IBGE, link e tabelas
      4093/5436/7322), problema que a base ajuda a entender (desigualdade de
      rendimento por sexo na Região Sul e efeitos da pandemia), quem usaria
      (gestores públicos, sindicatos, pesquisadores, ONGs, jornalismo de dados),
      uso em BI (dashboards de gap salarial), uso em Data Mining (clustering,
      previsão de rendimento, descoberta de padrões) e perguntas respondíveis.

> Implementado em `notebooks/03_tratamento_pm3.ipynb` (seção "1. Planejamento do
> tratamento dos dados") e em `docs/relatorio_final.md`.

---

## 2. Relação com Big Data Analytics, Data Mining e BI (context.md 6.2) ✅

- [x] Texto aplicando os conceitos ao tema PNAD: como os dados apoiam decisões
      (políticas de equidade salarial direcionadas por UF), padrões descobertos
      (correlação ocupados×informalidade = 0,86; gap salarial persistente apesar
      de mulheres terem mais escolaridade), tipos de análise (séries temporais,
      correlação, clustering), uso em dashboards (sim, formato long do `df_sel`),
      e aplicações de classificação/agrupamento/previsão/descoberta de padrões.

> Implementado em `notebooks/03_tratamento_pm3.ipynb` (seção "2. Relação com Big
> Data Analytics, Data Mining e BI") e em `docs/relatorio_final.md`.

---

## 3. Modelagem inicial dos dados (context.md 6.3) ✅

- [x] Apresentada a estrutura da base silver (5.920 linhas × 15 colunas) e da base
      gold final (448 linhas × 17 colunas, seção 16).
- [x] Colunas numéricas: `valor`, `valor_imputado`, `valor_normalizado`,
      `gap_salarial_pct`.
- [x] Colunas categóricas: `tabela_id`, `indicador_tabela`, `uf_nome`,
      `regiao_nome`, `sexo`, `nivel_instrucao`, `variavel_nome`, `unidade_medida`,
      `faixa_rendimento`, `is_outlier`.
- [x] Colunas de período: `ano`, `trimestre` (Int64 nullable), `periodo_label`.
- [x] Dimensões (UF/região, sexo, período, nível de instrução, indicador,
      `faixa_rendimento`) vs. medidas (`valor`/`valor_imputado`,
      `valor_normalizado`, `gap_salarial_pct`) mapeadas.

> Implementado em `notebooks/03_tratamento_pm3.ipynb` (seção "3. Modelagem inicial
> dos dados") e em `docs/relatorio_final.md`.

---

## 4. Extensão do normalizador PNAD (pré-requisito técnico) ✅

- [x] Estender `silver/normalizar_pnad.py` (`_build_col_map` / `_normalize_file`) para
      capturar a dimensão adicional do SIDRA presente na tabela 7322:
  - Nível de instrução (classificação **C1568**) → novas colunas `nivel_instrucao_cod`
    e `nivel_instrucao`.
- [x] Para tabelas sem essa classificação (4093, 5436), a coluna fica ausente/`NaN`
      automaticamente (via `keep = [c for c in [...] if c in df.columns]`).
- [ ] Reexecutar `notebooks/02_silver.ipynb` (após coletar o bronze — seção "Pré-requisito
      de dados" abaixo) e validar o novo `pnad_limpo.csv` (conferir contagem de
      linhas/colunas, amostra de `nivel_instrucao` para `tabela_id == "7322"`).

> Nota: a tabela 7322 é coletada no nível **N2 (Região Sul)**, não N3 (UF) — portanto
> suas linhas terão `regiao_cod`/`regiao_nome` preenchidos e `uf_cod`/`uf_nome` vazios.
> Isso deve ser considerado nas seções de seleção (6.6) e agregação (6.11).

---

## 5. Diagnóstico da qualidade dos dados (context.md 6.4) ✅

Trabalhar a partir do **bronze** (JSON SIDRA bruto, antes da limpeza do
`PnadNormalizer`) para expor os problemas reais da base original:

- [x] Linha 0 do JSON = cabeçalho de metadados/descrições misturado com os dados.
- [x] Códigos de ausência do IBGE: `-`, `...`, `X`, `x`, `C`, `""`.
- [x] Valores numéricos com vírgula decimal (ex.: `"4.529,00"`) — checado: nesta
      coleta nenhum valor usa vírgula (todos já vêm com ponto); a normalização
      `.str.replace(",", ".")` é defensiva.
- [x] `periodo` armazenado como código `AAAASS` (texto), não como data.
- [x] **(Principal)** Dimensão "Variável" (D3) traz dezenas de indicadores com
      unidades distintas (`Mil pessoas`, `%`, `Reais`, coeficientes de variação) na mesma
      coluna `valor` — ver achado crítico na seção 0. Sem isolar por `variavel_nome`,
      estatísticas/gráficos sobre `valor` são inválidos.
- [x] Mistura de unidades entre `tabela_id` (4093/7322 = pessoas/%, 5436 = R$/%) —
      risco de comparação inválida sem filtrar por `tabela_id` **e** `variavel_nome`.
- [x] **Recorte etário inconsistente entre tabelas**: 4093 e 5436 cobrem pessoas de
      14+ anos, enquanto 7322 cobre pessoas de 10+ anos — qualquer comparação entre
      `tabela_id == "7322"` e as demais (ex.: população total) deve registrar essa
      diferença de público-alvo no relatório (não são diretamente somáveis/comparáveis).
- [x] Códigos vs. nomes redundantes (`uf_cod`/`uf_nome`, `sexo_cod`/`sexo`,
      `regiao_cod`/`regiao_nome`).
- [x] **Novo achado**: tabela 5436 retorna apenas 16/24 trimestres (faltam 2020T2 a
      2022T1 — linhas inteiras ausentes na resposta da API, não apenas `valor`
      ausente). Coincide com o período de `"..."` na tabela 4093 (48/144 linhas dos
      indicadores de foco), reforçando a hipótese de undercoverage da PNAD durante a
      pandemia.
- [x] Montar tabela "problema | exemplo | tratamento proposto" para o relatório —
      `tabela_problemas` em `notebooks/03_tratamento_pm3.ipynb` (9 problemas).

> Implementado em `notebooks/03_tratamento_pm3.ipynb` (seção "5. Diagnóstico da
> qualidade dos dados").

---

## 6. Análise Exploratória de Dados (context.md 6.5) ✅

- [x] Estatísticas descritivas de `valor` (geral e por `tabela_id`, pois as unidades
      diferem entre tabelas).
- [x] Frequência das variáveis categóricas: `sexo`, `uf_nome`/`regiao_nome`,
      `nivel_instrucao` (tabela 7322).
- [x] Gráfico de barras: rendimento médio por UF e sexo (5436) + população por
      nível de instrução e sexo (7322).
- [x] Gráfico de linha: evolução temporal do rendimento (5436) e da taxa de
      informalidade (4093) por trimestre/sexo.
- [x] Boxplot: distribuição de `valor` (rendimento) por sexo / por UF.
- [x] Histograma de `valor` (rendimento) por sexo.
- [x] Mapa de calor de correlação entre indicadores (ocupados, taxa de
      informalidade, rendimento).
- [x] Análise temporal usando `periodo`/`ano`/`trimestre` (lacunas em 2020T2-2022T1
      identificadas e explicadas).
- [x] **Interpretar cada gráfico em texto** — feito em células markdown logo após
      cada gráfico.

> Implementado em `notebooks/03_tratamento_pm3.ipynb` (seção "6. Análise
> Exploratória de Dados").

---

## 7. Seleção dos dados (context.md 6.6) ✅

- [x] **Filtrar por `variavel_nome`** — manter apenas os indicadores relevantes ao
      tema (gap salarial / força de trabalho), descartando todas as linhas
      "Coeficiente de variação - ..." (medida de precisão estatística, não de interesse
      analítico) e "Distribuição percentual - ..." redundantes. Indicadores aplicados
      (`VARIAVEIS_FOCO`, 448 linhas):
  - **4093**: `"Pessoas de 14 anos ou mais de idade ocupadas na semana de referência"`
    (Mil pessoas) e `"Taxa de informalidade das pessoas de 14 anos ou mais de idade ocupadas na semana de referência"` (%).
  - **5436**: `"Rendimento médio mensal real das pessoas de 14 anos ou mais de idade ocupadas na semana de referência com rendimento de trabalho, habitualmente recebido no trabalho principal"` (Reais).
  - **7322**: `"Pessoas de 10 anos ou mais de idade"` (Mil pessoas, por nível de
    instrução).
- [x] Justificar colunas mantidas: `tabela_id`, `uf_nome`, `regiao_nome`, `periodo`
      (depois decomposto em `ano`/`trimestre` na seção 8), `sexo`, `nivel_instrucao`,
      `variavel_nome`, `unidade_medida`, `valor`.
- [x] Justificar colunas removidas: `uf_cod`, `sexo_cod`, `regiao_cod`,
      `variavel_cod`, `nivel_instrucao_cod`, `unidade_medida_cod` (redundantes com as
      versões em texto).
- [x] Justificar filtros de linhas: registros com `valor` ausente são **mantidos**
      em `df_sel` (a ausência é informação relevante — Problemas 4 e 9); a estratégia
      de tratamento é decidida na seção 9.

> Implementado em `notebooks/03_tratamento_pm3.ipynb` (seção "7. Seleção dos
> dados") → dataframe `df_sel` (448 linhas × 9 colunas).

---

## 8. Limpeza e pré-processamento (context.md 6.7) ✅

- [x] Confirmar padronização de nomes de colunas (snake_case já em uso).
- [x] Converter `periodo` (`AAAASS`/`AAAA`, texto) → `ano` (int) + `trimestre`
      (Int64 nullable — `pd.NA` para a tabela 7322, que é anual) + `periodo_label`
      legível (`"2020-T1"` ou `"2021"`).
- [x] Confirmar que `valor` está como `float` (já tratado no silver atual).
- [x] Verificar e remover duplicidades (`df.duplicated()` e checagem pela chave de
      granularidade — 0 duplicatas encontradas).
- [x] Padronizar textos categóricos: `uf_nome`/`regiao_nome`/`nivel_instrucao` com
      `NaN` estrutural preenchidos como `"Não se aplica"`; valores de `sexo`,
      `tabela_id`, `unidade_medida` conferidos sem inconsistências de acentuação/caixa.

> Implementado em `notebooks/03_tratamento_pm3.ipynb` (seção "8. Limpeza e
> pré-processamento").

---

## 9. Tratamento de valores faltantes (context.md 6.8) ✅

- [x] Quantificar `NaN` em `valor` **antes do tratamento**: 96/448 (21,4%), todos em
      `tabela_id == 4093` (indicadores "Pessoas ocupadas" e "Taxa de informalidade"),
      trimestres 2020T2–2022T1 — undercoverage real da PNAD durante a pandemia
      (Problemas 4 e 9).
- [x] Decisão: **manter `valor` como `NaN`** (preserva a informação de que o dado
      não existe na fonte) **e** criar `valor_imputado` (imputação pela média do
      grupo `uf_nome`+`sexo`+`variavel_nome`) para demonstrar a técnica de
      imputação. Ambas as colunas seguem para o dataset final — `NaN` em
      `valor_imputado`: 0/448.
- [x] `nivel_instrucao`/`uf_nome`/`regiao_nome` ausentes (estruturalmente, por
      tabela) → preenchidos com `"Não se aplica"` (já feito na seção 8.4).

> Implementado em `notebooks/03_tratamento_pm3.ipynb` (seção "9. Tratamento de
> valores faltantes").

---

## 10. Tratamento de outliers (context.md 6.9) ✅

- [x] Detecção via **IQR (1,5×)** sobre `valor_imputado`, separado por
      `(tabela_id, variavel_nome)` (cada combinação tem sua própria
      escala/unidade).
- [x] Resultado: 8/448 outliers, **todos** em `tabela_id == 7322` /
      `nivel_instrucao == "Total"` (a categoria "Total" é a soma dos demais
      níveis de instrução — agregação legítima do IBGE, não erro de dado).
      Nenhum outlier nas tabelas 4093/5436 (a queda de rendimento/ocupação em
      2020–2022 está dentro da variação normal da série).
- [x] Decisão: manter os valores e a coluna `is_outlier` no dataset final, para que
      análises que excluam agregações possam filtrar por
      `nivel_instrucao != "Total"` ou `is_outlier == False`.

> Implementado em `notebooks/03_tratamento_pm3.ipynb` (seção "10. Tratamento de
> outliers").

---

## 11. Transformação dos dados (context.md 6.10) ✅

- [x] `ano` + `trimestre` + `periodo_label` a partir de `periodo` — já feito na
      seção 8.1/8.2 (limpeza), pois era pré-requisito dos gráficos temporais da
      seção 6.
- [x] `tabela_id` agrupado em rótulos descritivos via `TABELA_LABELS` →
      `indicador_tabela` ("Força de trabalho e informalidade", "Rendimento médio",
      "Rendimento por nível de instrução").

> Implementado em `notebooks/03_tratamento_pm3.ipynb` (seção "11. Transformação
> dos dados").

---

## 12. Agregação de dados (context.md 6.11) ✅

- [x] Tabela agregada: rendimento médio **anual** (`valor_imputado`, tabela 5436)
      por `uf_nome` + `sexo` + `ano`, via
      `df_sel.groupby(['uf_nome','sexo','ano'])['valor_imputado'].mean()`.
- [x] Interpretação: 2021 não aparece (lacuna da tabela 5436 — Problema 9); de 2020
      a 2025, o rendimento cresce em todas as UFs/sexos, com leve convergência do
      gap salarial em PR (37,3%→33,1%) e RS (37,6%→31,6%) e gap estável em SC
      (~31%).

> Implementado em `notebooks/03_tratamento_pm3.ipynb` (seção "12. Agregação de
> dados").

---

## 13. Normalização e padronização (context.md 6.12) ✅

- [x] `MinMaxScaler` (scikit-learn) aplicado a `valor_imputado`, **separado por
      `(tabela_id, variavel_nome)`**, gerando `valor_normalizado` em `[0, 1]`.
- [x] Min-Max escolhido (em vez de `StandardScaler`) para colocar todos os
      indicadores na mesma escala `[0,1]`, útil para visualizações comparativas
      entre indicadores de unidades diferentes.

> Implementado em `notebooks/03_tratamento_pm3.ipynb` (seção "13. Normalização e
> padronização").

---

## 14. Discretização dos dados (context.md 6.13) ✅

- [x] `faixa_rendimento` (baixo/médio/alto, tercis via `pd.qcut`) criada sobre
      `valor_imputado` da tabela 5436 (32 linhas em cada faixa); `"Não se aplica"`
      para as demais tabelas.
- [x] Tabela com `valor_imputado` original ao lado de `faixa_rendimento`
      apresentada no notebook.

> Implementado em `notebooks/03_tratamento_pm3.ipynb` (seção "14. Discretização
> dos dados").

---

## 15. Feature Engineering (context.md 6.14) ✅

- [x] `ano`, `trimestre`, `periodo_label` (seções 8/11).
- [x] `gap_salarial_pct` por UF/período (tabela 5436):
      `(valor_imputado_Masculino - valor_imputado_Feminino) / valor_imputado_Feminino * 100`,
      calculado via `pivot_table` de `sexo` e reanexado a `df_sel` (mesmo valor
      para as linhas Masc./Fem. de cada UF/período).
- [x] `faixa_rendimento` (seção 14), `is_outlier` (seção 10), `valor_normalizado`
      (seção 13), `indicador_tabela` (seção 11) — todas consolidadas em `df_sel`.

> Implementado em `notebooks/03_tratamento_pm3.ipynb` (seção "15. Feature
> Engineering").

---

## 16. Consolidação do dataset final tratado (context.md 6.15) ✅

- [x] `dados/gold/pnad_tratado_final.csv` gerado: 448 linhas × 17 colunas —
      `tabela_id, uf_nome, regiao_nome, sexo, nivel_instrucao, variavel_nome,
      unidade_medida, valor, ano, trimestre, periodo_label, valor_imputado,
      is_outlier, indicador_tabela, valor_normalizado, faixa_rendimento,
      gap_salarial_pct`.
- [x] Diferente do bronze (JSON por tabela, sem filtro/colunas derivadas) e do
      silver (`pnad_limpo.csv`, 5.920×15, sem as colunas tratadas/derivadas).

> Implementado em `notebooks/03_tratamento_pm3.ipynb` (seção "16. Consolidação do
> dataset final").

---

## 17. Catálogo de dados (context.md 6.16) ✅

- [x] `docs/catalogo_dados.md` criado com tabela
      `coluna | descrição | tipo | exemplo | origem | tratamento aplicado | uso esperado`,
      cobrindo as 17 colunas do dataset final.

> Implementado em `docs/catalogo_dados.md`, referenciado em
> `notebooks/03_tratamento_pm3.ipynb` (seção "17. Catálogo de dados").

---

## 18. DataOps e organização do projeto (context.md 6.17) ✅

- [x] `README.md` criado na raiz: estrutura de pastas, ordem de execução do
      pipeline (`01_coleta.ipynb` → `02_silver.ipynb` → `03_tratamento_pm3.ipynb`)
      e localização dos entregáveis.
- [x] `.gitignore` ajustado: `dados/bronze/` (JSON original) e `dados/gold/`
      (`pnad_tratado_final.csv`) agora são versionados como entregáveis/evidência
      do PM3; `dados/silver/` continua ignorado (intermediário, regenerável).
- [x] `notebooks/03_tratamento_pm3.ipynb` cobre as seções 5–18, executado do
      início ao fim sem erros (77 células).

> Implementado em `README.md`, `.gitignore` e `notebooks/03_tratamento_pm3.ipynb`
> (seção "18. DataOps e organização do projeto").

---

## 19. Entregáveis obrigatórios (context.md seção 7) ✅

- [x] Base de dados original (JSON bronze PNAD preservado em `dados/bronze/`).
- [x] Dataset final tratado (`dados/gold/pnad_tratado_final.csv`).
- [x] Notebook/script de tratamento (`notebooks/03_tratamento_pm3.ipynb`).
- [x] Relatório final (`docs/relatorio_final.md`, estrutura de 23 itens da seção 8
      do `context.md`).
- [x] Catálogo de dados (`docs/catalogo_dados.md`).
- [x] Evidências de EDA (gráficos no notebook, seção 6).
- [x] Tabela de problemas de qualidade encontrados (`tabela_problemas`, seção 5).
- [x] Descrição das etapas de limpeza (seção 8).
- [x] Demonstração de: valores faltantes (9), outliers (10), transformação (11),
      agregação (12), normalização (13), discretização (14), feature engineering (15).
- [x] Explicação de uso em BI e Data Mining — `notebooks/03_tratamento_pm3.ipynb`
      (seções 1–2) e `docs/relatorio_final.md` (item 6).
