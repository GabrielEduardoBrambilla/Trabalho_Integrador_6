# Análise de cada gráfico do dashboard

Para cada gráfico: aba, tipo, dados, o que mostra (com números reais) e por que
esse tipo foi escolhido. Números computados a partir de
`dados/gold/pnad_treated_data.csv` e `dados/gold/pnad_context_data.csv`, sem
filtros (UF = todas, ano = 2020–2025).

## KPI strip (topo, todas as abas)

5 `st.metric`: gap salarial médio (≈32,1%), rendimento médio Masc. (≈R$ 4.065)
e Fem. (≈R$ 3.080), correlação Ocupação×Informalidade (≈0,86–0,88), e vantagem
feminina em Superior completo (+4,4 p.p.: 19,0% das mulheres vs. 14,6% dos
homens). Recalculados a cada mudança de filtro na sidebar — são os únicos
números que um usuário apressado precisa ver antes de abrir qualquer gráfico.

---

## Aba "Mercado de Trabalho"

### 1. Rendimento médio por sexo e UF (gráfico borboleta)

- **Tipo:** `go.Bar` duplo horizontal, feminino em valores negativos a partir
  de um eixo central compartilhado.
- **Leitura:** Feminino ≈ R$ 2.984–3.198 / Masculino ≈ R$ 3.997–4.182, conforme
  a UF — o vão entre as duas pontas é proporcional ao gap percentual.
- **Por que esse tipo:** o eixo central compartilhado elimina a necessidade de
  comparar alturas de barras vizinhas mentalmente (como em barras agrupadas) —
  a distância entre as pontas já é a leitura.

### 2. Gap salarial médio por UF (barras horizontais)

- **Tipo:** `go.Bar` horizontal, cor por UF (paleta fixa de `theme.py`).
- **Leitura:** Paraná ≈34%, Rio Grande do Sul ≈31%, Santa Catarina ≈31%.
- **Por que esse tipo:** ranking simples de 3 categorias — barra horizontal é
  o gráfico mais direto para isso, sem necessidade de eixo polar ou áreas.

### 3. Evolução trimestral do gap salarial (linha)

- **Tipo:** `px.line`, uma série por UF, com `add_vrect` marcando a lacuna de
  dados (2020T2–2022T1).
- **Leitura:** o gap oscila entre ~26% e ~39% nos 16 trimestres com dado
  disponível, sem tendência de queda visível. A faixa cinza evita que o
  usuário confunda a lacuna real de divulgação do IBGE (Problema 9,
  `docs/relatorio_final.md`) com um erro do dashboard.
- **Por que esse tipo:** série temporal é o gráfico correto para "como algo
  evolui"; a anotação contextualiza um padrão que, sem ela, pareceria um bug.

### 4. Distribuição do rendimento por UF e sexo (boxplot)

- **Tipo:** `px.box`.
- **Leitura:** as caixas femininas ficam quase inteiramente abaixo das
  masculinas, com pouca sobreposição — o gap não é puxado por outliers, é uma
  diferença sistemática em toda a distribuição.
- **Por que esse tipo:** a média (gráficos 1–2) pode esconder se a diferença é
  pontual ou estrutural; o boxplot responde isso diretamente.

---

## Aba "Investigação"

### 5. Correlação entre indicadores (heatmap)

- **Tipo:** `px.imshow` sobre matriz de correlação de Pearson.
- **Dados:** Ocupação, Informalidade e Rendimento, pivotados por
  UF/trimestre/sexo (`build_indicator_wide`).
- **Leitura:** Ocupação×Informalidade ≈0,86–0,88 (forte); Rendimento×Ocupação ≈0,49; Rendimento×Informalidade ≈0,07 (quase nula). O endimento é o indicador mais independente dos outros dois.
- **Por que esse tipo:** compara todos os pares de variáveis de uma vez, sem
  precisar de 3 scatters separados.

### 6. Perfil normalizado por sexo (radar)

- **Tipo:** `go.Scatterpolar`, duas séries preenchidas, 3 eixos.
- **Dados:** `valor_normalizado` médio por indicador × sexo: Ocupação F=0,38 /
  M=0,73; Informalidade F=0,51 / M=0,69; Rendimento F=0,21 / M=0,70.
- **Leitura:** o polígono masculino é maior nos três eixos, mas o afastamento
  relativo entre os polígonos é desproporcionalmente maior no eixo Rendimento —
  se ocupação/informalidade explicassem o gap salarial, os três afastamentos
  seriam parecidos; não são.
- **Por que radar, e não 3 gráficos de barra:** é o único formato que mostra a
  _forma_ do perfil de cada sexo nos três indicadores simultaneamente — e
  permite ver se a diferença é proporcional (polígonos de mesma forma) ou
  não (polígonos de forma diferente, como aqui).
- **Cuidado de leitura:** o eixo "Ocupação" usa uma contagem absoluta de
  pessoas ocupadas (mil), não uma taxa — reflete tamanho populacional ocupado,
  não participação relativa.

### 7. Rendimento × Informalidade × Ocupação por trimestre (bolhas animadas)

- **Tipo:** `px.scatter` com `animation_frame="periodo_label"`,
  `facet_col="uf_nome"`, tamanho = pessoas ocupadas.
- **Leitura:** ao animar, os pontos femininos (rosa) permanecem à esquerda dos
  masculinos (azul) — rendimento menor — em praticamente todos os trimestres e
  UFs, não só em média.
- **Por que esse tipo:** um scatter estático com até 96 pontos sobrepostos
  (16 trimestres × 3 UFs × 2 sexos) seria ilegível; a animação no estilo
  Gapminder mostra o mesmo padrão se repetir período após período.

---

## Aba "Escolaridade"

> Usa o dataset de **contexto** (`pnad_context_data.csv`, tabela 7322) — Região
> Sul, anual, não cruzado por UF/trimestre com o dataset principal.

### 8. Distribuição educacional por sexo (radar)

- **Tipo:** `go.Scatterpolar`, 7 eixos (um por nível de instrução, exceto
  "Total").
- **Dados:** % da população de cada sexo em cada nível (soma 100% por sexo).
- **Leitura:** o polígono feminino se estica mais em "Superior completo"
  (19,0% vs. 14,6%); o masculino é ligeiramente maior em níveis intermediários
  (Fundamental/Médio). A vantagem feminina é concentrada exatamente no nível
  mais associado a remunerações mais altas.
- **Por que radar, e com a mesma paleta do radar da aba Investigação:**
  reaproveitar o mesmo tipo de gráfico cria reconhecimento imediato de padrão —
  o usuário já sabe ler "polígono maior = mais peso naquele eixo" sem precisar
  de nova legenda.

### 9. População por nível de instrução (barras agrupadas)

- **Tipo:** `px.bar(barmode="group")`.
- **Leitura:** valores absolutos (mil pessoas) por nível × sexo — complementa
  o radar (que mostra só proporção) com a escala real da população.
- **Por que manter as duas (radar + barras) e não só uma:** o radar responde
  "qual a forma da distribuição"; as barras respondem "quantas pessoas, de
  fato" — perguntas diferentes, ambas relevantes, sem se sobrepor (diferente do
  sunburst da v2, que respondia a mesma pergunta das barras de outro jeito).
