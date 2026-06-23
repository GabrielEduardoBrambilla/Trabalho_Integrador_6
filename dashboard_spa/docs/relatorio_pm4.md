# Relatório Final — PM4: Visualização de Dados e Dashboard (Gap Salarial, Região Sul)

> Dashboard implementado em [link](https://gabrieleduardobrambilla-trabalho-integ-dashboard-spaapp-86prob.streamlit.app/);

## 1. Introdução

Este relatório documenta o PM4 — construção de visualizações e de um dashboard a partir do dataset tratado no PM3 (PNAD Contínua/IBGE, mercado de trabalho da Região Sul). Enquanto o PM3 entregou dados limpos, documentados e prontos para uso analítico, o PM4 transforma esses dados em indicadores, gráficos e um dashboard interativo voltado à pergunta central: **existe gap salarial de gênero na Região Sul, e ele se sustenta mesmo descontando explicações mais simples (ocupação, informalidade, escolaridade)?**

## 2. Tema da base

Mercado de trabalho da Região Sul do Brasil (Paraná, Santa Catarina, Rio Grande do Sul), 2020–2025 — força de trabalho, informalidade, rendimento e nível de instrução, por sexo. Mesmo tema do PM3 (`docs/relatorio_final.md`, seção 2), com o foco de análise já consolidado em **gap salarial entre homens e mulheres**, com escolaridade como evidência de apoio.

## 3. Fonte dos dados

Os dois datasets finais gerados pelo PM3 (`notebooks/03_tratamento_pm3.ipynb`), consumidos diretamente pelo dashboard, sem nenhum reprocessamento adicional:

- **`dados/gold/pnad_treated_data.csv`** (384 linhas × 15 colunas) — dataset principal: força de trabalho, informalidade e rendimento (tabelas SIDRA 4093 e 5436), por UF, sexo e trimestre.
- **`dados/gold/pnad_context_data.csv`** (64 linhas × 13 colunas) — dataset de contexto: nível de instrução por sexo, Região Sul (tabela SIDRA 7322), anual.

Catálogos completos em `docs/catalogo_dados.md` e `docs/catalogo_dados_contexto.md`.

## 4. Relação com o PM3

O PM3 entregou exatamente o que o PM4 exige como ponto de partida: uma base real, tratada, que permite análise por categorias (UF, sexo, nível de instrução), análise de valores numéricos (rendimento, taxa de informalidade), e já estruturada para criação de indicadores e gráficos — incluindo uma feature derivada própria para este fim, `gap_salarial_pct` (PM3, seção 17). O PM4 não exigiu nem motivou nenhuma mudança nos dados; o dashboard lê os CSVs do PM3 como estão.

## 5. Objetivo da análise

Construir um dashboard que responda, com indicadores e gráficos — não com texto —, se a diferença de rendimento entre homens e mulheres na Região Sul é real, de que tamanho, e se diferenças de ocupação, informalidade ou escolaridade a explicam.

## 6. Perguntas analíticas

1. **Qual o tamanho do gap salarial entre homens e mulheres, e como ele varia entre Paraná, Santa Catarina e Rio Grande do Sul?**
   **Resposta:** o gap médio é de 32,1% (rendimento masculino R$ 4.065 vs. feminino R$ 3.080), e ele é alto nas três UFs, sem nenhum estado onde o gap seja pequeno: Paraná ≈34%, Rio Grande do Sul ≈31% e Santa Catarina ≈31%. A variação entre estados é pequena (3 p.p.) comparada ao tamanho do gap em si — não há UF "exceção" (gráficos 1 e 2, `dashboard_spa/docs/analise_graficos.md`).
2. **O gap salarial está diminuindo, aumentando ou estável entre 2020 e 2025?**
   **Resposta:** estável, sem tendência de queda. O gap trimestral oscila entre ~26% e ~39% ao longo dos 16 trimestres com dado disponível (2020–2025), mas não há trajetória consistente de redução nem de aumento — apenas ruído em torno de um nível persistentemente alto (gráfico 3).
3. **Diferenças de ocupação ou de informalidade entre os sexos explicam o gap salarial?**
   **Resposta:** não. Ocupação e informalidade têm correlação forte entre si (0,88), mas o rendimento é o indicador mais independente dos dois (correlação ≈0,49 com ocupação e ≈0,07 com informalidade). O radar de perfil normalizado (gráfico 6) mostra que o afastamento entre os sexos é desproporcionalmente maior no eixo Rendimento do que nos eixos Ocupação e Informalidade — se essas duas variáveis explicassem o gap salarial, os três afastamentos seriam proporcionalmente parecidos, e não são (gráficos 5–7).
4. **Mulheres têm menos escolaridade que homens — o que justificaria um rendimento menor?**
   **Resposta:** o oposto é verdadeiro. Mulheres têm proporcionalmente mais "Superior completo" que homens (19,0% vs. 14,6%, +4,4 p.p.) — exatamente o nível de instrução mais associado a remunerações mais altas. Essa diferença de escolaridade não apenas não explica o gap salarial como vai na direção contrária dele (gráficos 8–9).

(mínimo exigido: 3 — apresentadas 4, cada uma respondida por pelo menos um gráfico do dashboard, ver seção 8).

## 7. Indicadores utilizados

| Indicador                              | Valor (sem filtro)          | Fonte                                   |
| -------------------------------------- | --------------------------- | --------------------------------------- |
| Gap salarial médio (Masc. vs. Fem.)    | 32,1%                       | `gap_salarial_pct`, tabela 5436         |
| Rendimento médio — Masculino           | R$ 4.065                    | `valor_imputado`, tabela 5436           |
| Rendimento médio — Feminino            | R$ 3.080                    | `valor_imputado`, tabela 5436           |
| Correlação Ocupação × Informalidade    | 0,88                        | `valor_imputado`, tabela 4093, pivotada |
| Vantagem feminina em Superior completo | +4,4 p.p. (19,0% vs. 14,6%) | `valor_imputado`, tabela 7322           |

Os cinco indicadores aparecem como `st.metric` no topo do dashboard, recalculados a cada mudança nos filtros da sidebar (UF, período) — nenhum é estático.

## 8. Gráficos planejados

| #   | Título                                              | Tipo                           | Colunas usadas                                                                | Pergunta que responde | Justificativa da escolha                                                                                        |
| --- | --------------------------------------------------- | ------------------------------ | ----------------------------------------------------------------------------- | --------------------- | --------------------------------------------------------------------------------------------------------------- |
| 1   | Rendimento médio por sexo e UF                      | Barras horizontais (borboleta) | `uf_nome`, `sexo`, `valor_imputado`                                           | Pergunta 1            | Eixo central compartilhado deixa o tamanho do gap visualmente óbvio, sem comparação mental de barras agrupadas. |
| 2   | Gap salarial médio por UF                           | Barras horizontais             | `uf_nome`, `gap_salarial_pct`                                                 | Pergunta 1            | Ranking de 3 categorias — barra horizontal é o gráfico mais direto.                                             |
| 3   | Evolução trimestral do gap salarial                 | Linha                          | `periodo_label`, `gap_salarial_pct`, `uf_nome`                                | Pergunta 2            | Série temporal é o gráfico correto para tendência; anotação da lacuna de dados evita má interpretação.          |
| 4   | Distribuição do rendimento por UF e sexo            | Boxplot                        | `uf_nome`, `sexo`, `valor`                                                    | Pergunta 1            | Mostra se a diferença é só na média ou em toda a distribuição.                                                  |
| 5   | Correlação entre indicadores                        | Mapa de calor                  | `Ocupação`, `Informalidade`, `Rendimento` (derivadas de `valor_imputado`)     | Pergunta 3            | Compara todos os pares de variáveis numéricas de uma vez.                                                       |
| 6   | Perfil normalizado por sexo                         | Radar (`Scatterpolar`)         | `indicador`, `sexo`, `valor_normalizado`                                      | Pergunta 3            | Único formato que mostra a forma do perfil multivariado dos dois sexos numa imagem só.                          |
| 7   | Rendimento × Informalidade × Ocupação por trimestre | Dispersão animada (bolhas)     | `Rendimento`, `Informalidade`, `Ocupação`, `sexo`, `uf_nome`, `periodo_label` | Pergunta 2 e 3        | Evita sobreposição de até 96 pontos; mostra o padrão se repetindo trimestre a trimestre.                        |
| 8   | Distribuição educacional por sexo                   | Radar (`Scatterpolar`)         | `nivel_instrucao`, `sexo`, `valor_imputado` (% do total)                      | Pergunta 4            | Mesma lógica do gráfico 6 — compara a forma da distribuição, não o volume.                                      |
| 9   | População por nível de instrução                    | Barras agrupadas               | `nivel_instrucao`, `sexo`, `valor_imputado`                                   | Pergunta 4            | Complementa o radar com a escala populacional absoluta.                                                         |

(mínimo exigido: 4 — planejados e construídos 9).

## 9. Visualizações construídas

Todas as 9 visualizações da seção 8 foram construídas no dashboard (`dashboard_spa/app.py`), com título claro, eixos/legendas identificados (`labels=` em cada `px.*`/`go.Figure`), paleta de cor consistente (`dashboard_spa/theme.py`: Feminino sempre rosa, Masculino sempre azul, cada UF com cor fixa) e organização em 3 abas temáticas. A análise gráfico a gráfico — dados exatos, leitura, e por que aquele tipo de gráfico foi escolhido — está em `dashboard_spa/docs/analise_graficos.md` (não duplicada aqui para evitar dois documentos divergentes sobre o mesmo conteúdo).

## 10. Interpretação dos resultados

- **O gap é real e estável:** rendimento médio feminino (R$ 3.080) é 32,1% menor que o masculino (R$ 4.065), em todos os trimestres com dado disponível e nas três UFs, sem tendência de queda entre 2020 e 2025 (gráficos 1–4).
- **Não é explicado por ocupação/informalidade:** esses dois indicadores têm correlação forte entre si (0,88), mas o rendimento é o mais independente dos três (correlação ≈0,49 e ≈0,07) — o radar de perfil normalizado (gráfico 6) confirma que o afastamento entre os sexos é desproporcionalmente maior no rendimento que nos outros dois eixos (gráficos 5–7).
- **Não é explicado por escolaridade — pelo contrário:** mulheres têm proporcionalmente mais "Superior completo" que homens (19,0% vs. 14,6%, +4,4 p.p.) — exatamente o nível mais associado a remunerações mais altas (gráficos 8–9).
- **Conclusão analítica:** descartadas as explicações mais simples, o gap salarial de 32,1% permanece sem explicação nos dados disponíveis — consistente com fatores estruturais não capturados nesta base (ver `docs/relatorio_final.md`, seção 22, Limitações do PM3).

## 11. Descrição do dashboard

- **Título:** "📊 Gap Salarial — Mercado de Trabalho da Região Sul" (`st.title`).
- **Fonte dos dados:** exibida sob o título e na sidebar (`st.caption`): PNAD Contínua/IBGE via API SIDRA, com os nomes exatos dos dois arquivos CSV consumidos.
- **Indicadores principais:** 5 KPIs no topo (seção 7), recalculados pelos filtros — acima do mínimo de 3 exigido.
- **Gráficos:** 9, organizados em 3 abas — "💰 Mercado de Trabalho" (4 gráficos), "🔍 Investigação" (3 gráficos), "🎓 Escolaridade" (2 gráficos + 3 KPIs adicionais) — acima do mínimo de 4 exigido.
- **Filtros interativos:** 2 — `UF` (multiseleção) e `Período/ano` (slider de intervalo), ambos na sidebar, afetando KPIs e todos os gráficos — acima do mínimo de 1 exigido.
- **Organização visual:** sidebar fixa para filtros e fonte; corpo principal com KPIs sempre visíveis seguidos de abas temáticas; paleta de cor consistente em todo o dashboard (`dashboard_spa/theme.py`).
- **Robustez:** validado com `streamlit.testing.v1.AppTest` para os filtros default e para casos de borda (UF única, nenhuma UF selecionada, período sem dado de escolaridade) — sem exceções (ver seção 12).

## 12. Conclusão

O dashboard do PM4 cumpre integralmente os e responde 4 perguntas analíticas propostas: o gap salarial de 32,1% entre homens e mulheres na Região Sul é real, persistente ao longo do tempo e nas três UFs, e não é explicado por ocupação, informalidade ou escolaridade — pelo contrário, a escolaridade favorece as mulheres. O dashboard está pronto para uso recorrente por gestores públicos, sindicatos e pesquisadores (público identificado em `docs/relatorio_final.md`, seção 2).

## 13. Checklist de conformidade com `docs/gold_context.md`

| Requisito (seção do gold_context.md)                  | Exigido                                             | Entregue                      | Onde                                                                                  |
| ----------------------------------------------------- | --------------------------------------------------- | ----------------------------- | ------------------------------------------------------------------------------------- |
| Tema, problema, quem usa (6.1/Etapa 1)                | texto                                               | ✅                            | Seções 2, 5 deste relatório                                                           |
| Perguntas analíticas (Etapa 1)                        | ≥ 3                                                 | ✅ 4                          | Seção 6                                                                               |
| Indicadores utilizados (Etapa 1)                      | citar                                               | ✅ 5                          | Seção 7                                                                               |
| Gráficos planejados (Etapa 2)                         | ≥ 4, com título/tipo/colunas/pergunta/justificativa | ✅ 9                          | Seção 8                                                                               |
| Visualizações finais com interpretação (Etapa 3)      | ≥ 4                                                 | ✅ 9                          | Seções 9–10,`analise_graficos.md`                                                     |
| Indicadores principais no dashboard (Etapa 4)         | ≥ 3                                                 | ✅ 5 (+3 na aba Escolaridade) | `dashboard_spa/app.py`, KPI strip                                                     |
| Gráficos no dashboard (Etapa 4)                       | ≥ 4                                                 | ✅ 9                          | `dashboard_spa/app.py`, 3 abas                                                        |
| Filtro interativo (Etapa 4)                           | ≥ 1                                                 | ✅ 2 (UF, período)            | Sidebar,`dashboard_spa/app.py`                                                        |
| Título do dashboard (Etapa 4)                         | sim                                                 | ✅                            | `st.title`                                                                            |
| Fonte dos dados no dashboard (Etapa 4)                | sim                                                 | ✅                            | `st.caption` sob o título + sidebar                                                   |
| Organização visual clara (Etapa 4)                    | sim                                                 | ✅                            | Sidebar + KPI strip + abas                                                            |
| Base utilizada (Entregável 1)                         | sim                                                 | ✅                            | `dados/gold/pnad_treated_data.csv` + `pnad_context_data.csv`                          |
| Briefing da visualização (Entregável 2)               | sim                                                 | ✅                            | Seções 2, 5, 6, 7 deste relatório                                                     |
| Planejamento de gráficos (Entregável 4)               | ≥ 4                                                 | ✅ 9                          | Seção 8                                                                               |
| Visualizações finais com interpretação (Entregável 5) | ≥ 4                                                 | ✅ 9                          | Seções 9–10                                                                           |
| Dashboard final (Entregável 6)                        | sim                                                 | ✅                            | `dashboard_spa/app.py`, `streamlit run dashboard_spa/app.py`                          |
| Prints ou link do dashboard (Entregável 7)            | sim                                                 | ✅                            | https://gabrieleduardobrambilla-trabalho-integ-dashboard-spaapp-86prob.streamlit.app/ |
| Relatório final (Entregável 8)                        | sim                                                 | ✅                            | Este documento                                                                        |
