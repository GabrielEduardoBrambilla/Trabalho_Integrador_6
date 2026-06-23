# Plano — Refoco do PM3 para análise de gap salarial + dois gold outputs

## 0. Motivação

A investigação do "Problema 7" (recorte etário 7322 vs. 4093/5436) mostrou que a
tabela 7322 não diverge só na idade: ela está em **outro nível geográfico** (N2/Região,
não N3/UF — restrição da própria API SIDRA, não do tratamento) e em **outra
periodicidade** (anual, 4 anos, vs. trimestral, 6 anos). Confirmado em
`dados/gold/pnad_tratado_final.csv`: as 64 linhas de `tabela_id == 7322` têm
`uf_nome == "Não se aplica"` e `gap_salarial_pct`/`faixa_rendimento` sempre vazios —
ou seja, ela nunca foi de fato uma dimensão joinável a 4093/5436, mesmo antes desta
mudança.

Diante disso, o projeto deixa de tratar as 3 tabelas como "4 pilares equivalentes"
(rendimento, força de trabalho, informalidade, nível de instrução) e passa a ter:

- **Análise principal:** gap salarial entre homens e mulheres na Região Sul, usando
  4093 (força de trabalho/informalidade) + 5436 (rendimento) — joinável por
  `uf_nome`, `sexo`, `periodo_label` (trimestral, 2020–2025).
- **Análise de contexto:** nível de instrução por sexo (7322) — usada apenas para
  testar a hipótese "o gap salarial é explicado por escolaridade?" (resposta: não),
  sem pretensão de ser cruzada por UF/trimestre com a análise principal.

Essa é uma mudança de **enquadramento e de entregável** (dois CSVs gold em vez de
um), não uma mudança de coleta — bronze e silver continuam iguais.

## 1. Novos entregáveis gold (nomes confirmados)

| Arquivo | Conteúdo | Linhas | Granularidade |
|---|---|---|---|
| `dados/gold/pnad_treated_data.csv` | `tabela_id` 4093 + 5436 | 384 (288 + 96) | UF × sexo × trimestre |
| `dados/gold/pnad_context_data.csv` | `tabela_id` 7322 | 64 | Região Sul × sexo × nível de instrução × ano |

Cada arquivo só leva as colunas que de fato se aplicam a ele (hoje várias ficam
`"Não se aplica"`/`NaN` por estarem nesse arquivo único):

**`pnad_treated_data.csv`** (15 colunas — remove `regiao_nome`, `nivel_instrucao`):
`tabela_id, indicador_tabela, uf_nome, sexo, variavel_nome, unidade_medida, valor, ano, trimestre, periodo_label, valor_imputado, is_outlier, valor_normalizado, faixa_rendimento, gap_salarial_pct`

**`pnad_context_data.csv`** (13 colunas — remove `uf_nome`, `trimestre`,
`faixa_rendimento`, `gap_salarial_pct`, que nunca se aplicam à 7322):
`tabela_id, indicador_tabela, regiao_nome, sexo, nivel_instrucao, variavel_nome, unidade_medida, valor, ano, periodo_label, valor_imputado, is_outlier, valor_normalizado`

Catálogo de dados: dois arquivos separados — `docs/catalogo_dados.md` (para
`pnad_treated_data.csv`) e `docs/catalogo_dados_contexto.md` (para
`pnad_context_data.csv`). `docs/silver_relatorio_final.md` só será renomeado de
volta para `docs/relatorio_final.md` ao final de todo o refoco (passo 6 da seção 5).

> `valor_normalizado`/`is_outlier` continuam calculados por `(tabela_id, variavel_nome)`
> como hoje — a separação em dois arquivos não muda a conta, só onde ela é salva.

## 2. Mudanças em `notebooks/03_tratamento_pm3.ipynb`

1. **Seção 1–2 (planejamento / relação com BI-DM):** reescrever o texto para deixar
   explícito que o gap salarial é a pergunta principal, e nível de instrução é
   evidência de suporte (descarta uma hipótese alternativa), não uma dimensão de BI
   igual às demais.
2. **Seção 7 (seleção dos dados):** manter o filtro por `VARIAVEIS_FOCO`, mas explicar
   que o resultado já nasce conceitualmente em dois grupos (`tabela_id in [4093,5436]`
   vs. `tabela_id == 7322`), mesmo continuando em um único `df_sel` até a etapa de
   consolidação (para reaproveitar limpeza/outliers/normalização comuns).
3. **Seções 8–15 (EDA → feature engineering):** sem mudança de lógica — continuam
   operando sobre `df_sel` combinado, já que `valor_imputado`/`is_outlier`/
   `valor_normalizado` são calculados por grupo `(tabela_id, variavel_nome)` e
   `gap_salarial_pct`/`faixa_rendimento` já só populam 4093/5436. Apenas ajustar texto
   das células markdown para a nova narrativa (gap salarial primeiro, instrução depois,
   como evidência).
4. **Seção 16 (consolidação) — principal mudança de código:**
   - Construir `df_gap = df_sel[df_sel["tabela_id"].isin([4093, 5436])]`, remover
     `regiao_nome`/`nivel_instrucao`, salvar em `dados/gold/pnad_gap_salarial.csv`.
   - Construir `df_contexto = df_sel[df_sel["tabela_id"] == 7322]`, remover `uf_nome`,
     `trimestre`, `faixa_rendimento`, `gap_salarial_pct`, salvar em
     `dados/gold/pnad_escolaridade_contexto.csv`.
   - Remover a geração do `pnad_tratado_final.csv` único.
5. **Seção 17 (catálogo) / 18 (DataOps):** atualizar referências de "um dataset final"
   para "dois datasets finais", e linkar os dois arquivos.
6. Revisar contagens citadas em texto (`448 linhas`, `17 colunas`) ao longo do notebook
   para refletir os dois novos totais (384×15 e 64×13).

## 3. Mudanças em `docs/silver_relatorio_final.md`

> Nome atual do arquivo (renomeado de `relatorio_final.md`). Decidir ao final se ele
> deve voltar a se chamar `relatorio_final.md` — sugiro manter `silver_relatorio_final.md`
> só enquanto este refoco está em andamento, e renomear de volta no commit final.

- **Seção 2 (Tema escolhido):** redefinir como "gap salarial entre homens e mulheres
  no mercado de trabalho da Região Sul (força de trabalho, informalidade e
  rendimento)", com nível de instrução citado como evidência de suporte, não como
  parte do tema central.
- **Seção 3 (Fonte dos dados):** marcar 4093/5436 como "tabelas principais" e 7322
  como "tabela de contexto", já citando os dois arquivos gold.
- **Seção 4 (Objetivo):** ajustar para "produzir um dataset principal (gap salarial,
  joinável por UF/sexo/trimestre) e um dataset de contexto (escolaridade por sexo,
  Região Sul) que sustente ou refute hipóteses sobre a causa do gap".
- **Seção 6 (Relação com BI/DM):** ajustar "uso em dashboards" para deixar claro que
  o dashboard principal consome só `pnad_gap_salarial.csv`; `pnad_escolaridade_contexto.csv`
  é uma tabela auxiliar/qualitativa, não uma dimensão do mesmo cubo.
- **Seção 9 (Seleção dos dados):** explicar a divisão em dois conjuntos já nesta
  etapa conceitualmente (ver item 2.2 acima).
- **Seção 16/17 (Discretização / Feature Engineering):** já estão corretas (só se
  aplicam a 5436) — apenas confirmar que o texto não sugere que valem para a 7322.
- **Seção 18 (Dataset final):** reescrever totalmente para descrever os dois arquivos,
  suas colunas e por que a separação existe (ligar com a seção 22 atual, que já
  documenta a diferença de granularidade).
- **Seção 19 (Catálogo de dados):** apontar para dois catálogos (ou duas tabelas
  dentro do mesmo `catalogo_dados.md` — ver seção 4 abaixo).
- **Seção 22 (Limitações):** manter o bullet sobre a granularidade da 7322, mas
  reformular como justificativa da separação em dois arquivos (deixa de ser só uma
  "limitação", passa a ser também a motivação do design).
- **Seção 23 (Próximos passos):** mantém o item de microdados; acrescentar item sobre
  eventualmente padronizar um identificador comum (ex.: `sexo`) para permitir, no
  futuro, ao menos um join parcial entre os dois arquivos por sexo+ano (sem UF/trimestre).

## 4. Outros arquivos a atualizar

- **`docs/catalogo_dados.md`:** dividir em duas tabelas (uma por arquivo gold) ou
  criar `docs/catalogo_dados_contexto.md` separado — decidir formato ao implementar.
  Cada tabela perde as colunas que não existem mais nesse arquivo (ver seção 1).
- **`README.md`:** atualizar a árvore de pastas (`dados/gold/` agora tem 2 arquivos),
  a seção "Como rodar o pipeline" (passo 3) e "Entregáveis do PM3".
- **`docs/plano_pm3.md`:** está congelado como checklist do PM3 original — não
  precisa ser reescrito, mas vale um bloco final apontando para este plano como o
  registro da mudança pós-entrega inicial.
- **`.gitignore`:** confirmar que `dados/gold/*.csv` (plural) continua versionado —
  hoje provavelmente aponta para um nome específico; ajustar para o padrão `*.csv`
  dentro de `dados/gold/` se necessário.

## 5. Ordem de execução sugerida

1. Notebook: implementar o split em `df_gap`/`df_contexto` na seção 16 e gerar os
   dois CSVs (passo que efetivamente muda o pipeline).
2. Rodar o notebook do início ao fim, confirmar contagens (384/15 e 64/13).
3. Atualizar `docs/catalogo_dados.md` com os números reais pós-execução.
4. Atualizar `docs/silver_relatorio_final.md` seção por seção (lista da seção 3).
5. Atualizar `README.md` e remover `dados/gold/pnad_tratado_final.csv` antigo.
6. Revisão final: garantir que nenhum arquivo ainda cite "448 linhas × 17 colunas"
   ou "`pnad_tratado_final.csv`" como entregável único.

## 6. Decisões (resolvidas)

- Nomes finais dos dois arquivos gold: `pnad_treated_data.csv` (principal) e
  `pnad_context_data.csv` (contexto).
- `docs/catalogo_dados.md` (principal) e `docs/catalogo_dados_contexto.md`
  (contexto) — dois arquivos separados.
- `docs/silver_relatorio_final.md` foi renomeado de volta para
  `docs/relatorio_final.md` ao final da implementação deste plano.
