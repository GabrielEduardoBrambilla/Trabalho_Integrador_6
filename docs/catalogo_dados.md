# Catálogo de dados — `dados/gold/pnad_tratado_final.csv`

Dataset final do PM3, gerado por `notebooks/03_tratamento_pm3.ipynb` a partir do
silver `dados/silver/pnad_limpo.csv`. 448 linhas × 17 colunas. Cada linha representa
um indicador da PNAD Contínua (IBGE/SIDRA) para um recorte de UF/Região, sexo,
período e (quando aplicável) nível de instrução.

| Coluna | Descrição | Tipo | Exemplo | Origem | Tratamento aplicado | Uso esperado |
|---|---|---|---|---|---|---|
| `tabela_id` | Identificador da tabela SIDRA de origem (4093, 5436 ou 7322) | int | `5436` | Original | Mantida sem alteração | Dimensão (filtro) |
| `uf_nome` | Unidade da Federação (apenas tabelas 4093/5436, nível UF) | texto | `Paraná` | Original | `NaN` → `"Não se aplica"` (tabela 7322, nível Região) | Dimensão |
| `regiao_nome` | Grande Região (apenas tabela 7322, nível Região) | texto | `Sul` | Original | `NaN` → `"Não se aplica"` (tabelas 4093/5436, nível UF) | Dimensão |
| `sexo` | Sexo (Masculino/Feminino) | texto | `Feminino` | Original (`sexo_cod` descartado) | — | Dimensão |
| `nivel_instrucao` | Nível de instrução (apenas tabela 7322) | texto | `Superior completo` | Original | `NaN` → `"Não se aplica"` (tabelas 4093/5436) | Dimensão |
| `variavel_nome` | Nome do indicador SIDRA (um dos 4 selecionados em `VARIAVEIS_FOCO`) | texto | `Rendimento médio mensal real ...` | Original | Filtrado para 4 indicadores de interesse (de 34+8+4 disponíveis) | Dimensão (filtro) |
| `unidade_medida` | Unidade de medida do `valor` | texto | `Reais` | Original | — | Contexto da medida |
| `valor` | Valor numérico bruto do indicador, conforme divulgado pelo IBGE | float | `3997.0` ou `NaN` | Original | Códigos de ausência IBGE (`-`, `...`, `X`, `x`, `C`, `""`) convertidos para `NaN` | Medida (com lacunas documentadas) |
| `ano` | Ano do período de referência | int | `2023` | Derivada de `periodo` (seção 8.1) | `periodo // 100` (4093/5436) ou `periodo` (7322) | Dimensão temporal |
| `trimestre` | Trimestre do período (1–4); `NA` para tabela 7322 (indicador anual) | Int64 (nullable) | `3` | Derivada de `periodo` (seção 8.1) | `periodo % 100` (4093/5436) ou `pd.NA` (7322) | Dimensão temporal |
| `periodo_label` | Rótulo legível do período | texto | `2023-T3` ou `2021` | Derivada de `ano`/`trimestre` (seção 8.2) | Concatenação `"{ano}-T{trimestre}"` ou `"{ano}"` | Eixo de gráficos temporais |
| `valor_imputado` | `valor` com lacunas preenchidas pela média do grupo (UF, sexo, indicador) | float | `3390.44` | Derivada (seção 9) | Imputação por média de grupo (`uf_nome`, `sexo`, `variavel_nome`) | Medida (sem `NaN`), base para normalização/outliers |
| `is_outlier` | Indica se `valor_imputado` é outlier (IQR 1.5×) dentro de `(tabela_id, variavel_nome)` | bool | `True` | Derivada (seção 10) | Regra IQR 1.5× por grupo | Filtro/flag analítico |
| `indicador_tabela` | Rótulo descritivo da tabela de origem | texto | `Rendimento médio` | Derivada de `tabela_id` (seção 11) | Mapeamento `TABELA_LABELS` | Dimensão (legibilidade) |
| `valor_normalizado` | `valor_imputado` normalizado para `[0, 1]` (Min-Max) dentro de `(tabela_id, variavel_nome)` | float | `0.62` | Derivada (seção 13) | `MinMaxScaler` por grupo | Medida comparável entre indicadores |
| `faixa_rendimento` | Faixa de rendimento (tercis): `baixo`/`médio`/`alto`; `"Não se aplica"` fora da tabela 5436 | texto | `alto` | Derivada (seção 14) | `pd.qcut` (3 quantis) sobre `valor_imputado` da tabela 5436 | Dimensão categórica (BI) |
| `gap_salarial_pct` | Gap salarial percentual (Masc. vs. Fem.) por UF/período, tabela 5436; `NaN` para outras tabelas | float | `37.33` | Derivada (seção 15) | `(rendimento_M - rendimento_F) / rendimento_F * 100`, via pivot de `sexo` | Medida derivada (indicador de desigualdade) |

## Observações gerais

- **Recorte etário:** indicadores das tabelas 4093/5436 cobrem pessoas de 14+ anos;
  o indicador da tabela 7322 cobre pessoas de 10+ anos (Problema 7) — não comparar
  diretamente sem essa ressalva.
- **Lacuna temporal:** a tabela 5436 não possui dados para 2020T2–2022T1 (Problema 9);
  consequentemente `gap_salarial_pct` também não existe para esse intervalo.
- **Categoria "Total" (tabela 7322):** `nivel_instrucao == "Total"` é a soma dos
  demais níveis de instrução — gera os 8 `is_outlier == True` da tabela 7322
  (estrutural, não erro de dado — ver seção 10 do notebook).
