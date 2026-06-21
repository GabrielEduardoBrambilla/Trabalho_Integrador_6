# Análise de cada gráfico do dashboard

Para cada gráfico: onde está, que tipo é, que dado usa, o que ele mostra (com os números reais por trás), e por que esse tipo de gráfico foi escolhido em vez de uma alternativa mais óbvia. Números computados a partir de `dados/gold/pnad_treated_data.csv` e `dados/gold/pnad_context_data.csv`.

---

## Capa (`app.py`)

### 1. Trio de gauges — gap salarial por UF
- **Tipo:** `go.Indicator(mode="gauge+number")`, três instâncias em um grid 1×3.
- **Dados:** `gap_salarial_pct` médio (2020–2025) por UF, tabela 5436.
- **Leitura:** Paraná ≈34%, Rio Grande do Sul ≈31%, Santa Catarina ≈31%. Os três ponteiros ficam na faixa "alta" (rosa escuro) do mostrador — não há nenhum estado onde o gap seja pequeno.
- **Por que gauge, e não um número simples:** um gauge comunica imediatamente *onde* aquele número está dentro de uma escala de referência (aqui, 0–45%, com faixas de cor) — diferente de `st.metric`, que mostra o número isolado, sem dar ao leitor uma noção visual de "isso é alto ou baixo?". É o primeiro elemento visual que o leitor vê, por isso precisa comunicar gravidade sem exigir leitura de eixo ou legenda.

---

## Capítulo 1 — Cenário

### 2. Treemap — pessoas ocupadas por UF e sexo
- **Tipo:** `px.treemap(path=["uf_nome", "sexo"])`.
- **Dados:** média de pessoas ocupadas (mil), tabela 4093, por UF/sexo.
- **Leitura:** Paraná é o maior mercado de trabalho dos três (maior retângulo), seguido por Rio Grande do Sul e Santa Catarina; dentro de cada UF, o retângulo masculino é visivelmente maior que o feminino — refletindo menor participação feminina na força de trabalho ocupada, um fenômeno distinto do gap salarial (mas que vale ter em mente como pano de fundo).
- **Por que treemap, e não barras simples:** o treemap comunica duas informações hierárquicas ao mesmo tempo — o tamanho relativo de cada UF *e* a proporção sexo dentro dela — em uma única figura compacta, sem precisar de eixos duplos ou múltiplos gráficos lado a lado.

---

## Capítulo 2 — O Gap Salarial

### 3. Gráfico borboleta — rendimento médio por sexo e UF
- **Tipo:** `go.Bar` duplo, orientação horizontal, com a série feminina em valores negativos (`x=-valor`) saindo do mesmo eixo central que a série masculina.
- **Dados:** rendimento médio (`valor_imputado`), tabela 5436, por UF/sexo.
- **Leitura:** Feminino ≈ R$ 2.984–3.198 / Masculino ≈ R$ 3.997–4.182, conforme a UF. O "buraco" entre as duas barras de cada UF é visualmente proporcional ao gap percentual.
- **Por que borboleta, e não barras agrupadas:** barras agrupadas (lado a lado) exigem que o leitor compare alturas entre barras vizinhas mentalmente. O gráfico borboleta usa um eixo central compartilhado — a *distância entre as pontas* das duas barras já é a leitura, sem esforço mental extra. É a técnica clássica de pirâmide populacional, aqui aplicada a rendimento.

### 4. Linha — evolução trimestral do gap salarial
- **Tipo:** `px.line`, uma série por UF, com `add_vrect` marcando a lacuna de dados.
- **Dados:** `gap_salarial_pct` por trimestre/UF, tabela 5436.
- **Leitura:** o gap oscila entre ~26% e ~39% nos 16 trimestres com dado disponível, sem tendência de queda visível ao longo de 2020–2025. A faixa cinza (2020T2–2022T1) marca onde a tabela 5436 não retorna dados — uma lacuna real da divulgação do IBGE durante a pandemia, não um erro deste tratamento (ver `docs/relatorio_final.md`, Problema 9).
- **Por que linha, e por que anotar a lacuna:** série temporal é o gráfico correto para "como algo evolui" — mas sem o `vrect`, o leitor veria uma quebra na linha e poderia interpretá-la como dado ruim do próprio dashboard. Anotar a lacuna transforma um "buraco que parece erro" em informação.

### 5. Bolhas animadas — rendimento × informalidade × ocupação no tempo
- **Tipo:** `px.scatter` com `animation_frame="periodo_label"`, `facet_col="uf_nome"`, tamanho da bolha = pessoas ocupadas.
- **Dados:** os três indicadores do dataset principal, pivotados por UF/trimestre/sexo (`build_indicator_wide`).
- **Leitura:** ao reproduzir a animação, os pontos femininos (rosa) permanecem consistentemente à esquerda dos masculinos (azul) — ou seja, com rendimento menor — em praticamente todos os trimestres e nas três UFs, não só em média.
- **Por que animação, e não um scatter estático:** um único scatter estático com todos os trimestres sobrepostos ficaria ilegível (são até 16 trimestres × 3 UFs × 2 sexos = até 96 pontos). A animação no estilo Gapminder permite ver o mesmo padrão se repetir período após período — reforçando que o gap é uma característica estrutural da série, não um instante isolado.

### 6. Boxplot — distribuição do rendimento por UF e sexo
- **Tipo:** `px.box`.
- **Dados:** `valor` (rendimento bruto, não imputado), tabela 5436, por UF/sexo.
- **Leitura:** as caixas femininas ficam quase inteiramente abaixo das masculinas, com pouca ou nenhuma sobreposição — o gap não é puxado por outliers ou por um sexo ter mais variabilidade; a distribuição inteira está deslocada.
- **Por que boxplot, e não só a média (já mostrada no gráfico 3):** a média pode esconder se a diferença é só de "alguns trimestres ruins" ou se é sistemática em toda a distribuição. O boxplot responde a essa pergunta diretamente — e aqui a resposta é "sistemática".

---

## Capítulo 3 — Investigação

### 7. Heatmap — correlação entre ocupação, informalidade e rendimento
- **Tipo:** `px.imshow` sobre uma matriz de correlação de Pearson.
- **Dados:** os três indicadores pivotados por UF/trimestre/sexo.
- **Leitura:** Ocupação × Informalidade ≈ 0,86–0,88 (forte); Rendimento × Ocupação ≈ 0,49 (moderada); Rendimento × Informalidade ≈ 0,07 (≈ nula). O rendimento é o indicador mais "independente" dos outros dois.
- **Por que heatmap:** é a forma mais direta de comparar todas as combinações de pares de variáveis numéricas de uma vez, sem precisar de 3 gráficos de dispersão separados.

### 8. Radar — perfil normalizado por sexo (Ocupação / Informalidade / Rendimento)
- **Tipo:** `go.Scatterpolar`, duas séries preenchidas (Feminino/Masculino).
- **Dados:** `valor_normalizado` médio por indicador × sexo (`normalized_profile_por_sexo`): Ocupação F=0,38 / M=0,73; Informalidade F=0,51 / M=0,69; Rendimento F=0,21 / M=0,70.
- **Leitura:** o polígono masculino é maior nos três eixos — mas o *afastamento relativo* entre os dois polígonos é bem maior no eixo Rendimento que nos outros dois. Se ocupação/informalidade explicassem o gap salarial, os três afastamentos seriam proporcionalmente parecidos; não são.
- **Por que radar, e não três gráficos de barra separados (este é o gráfico que motivou a reformulação do dashboard):** o radar é o único formato comum que permite enxergar a "forma" do perfil de cada sexo nos três indicadores *simultaneamente*, em uma única imagem — e mais importante, permite comparar visualmente se a diferença é proporcional (polígonos com a mesma forma, só tamanhos diferentes) ou desproporcional (polígonos com formas diferentes). Aqui, a forma é diferente — o que é exatamente o ponto que três gráficos de barra separados, vistos em sequência, comunicariam com muito mais esforço de memória do leitor.
- **Cuidado de leitura:** o eixo "Ocupação" usa `valor_normalizado` de uma contagem absoluta de pessoas ocupadas (mil), não uma taxa de participação — ele reflete que há mais homens ocupados em número absoluto na amostra, não necessariamente uma "taxa de ocupação" comparável 1:1 entre sexos. Por isso a legenda do gráfico, no dashboard, evita a palavra "taxa" para esse eixo.

### 9. Scatter com linha de tendência — ocupação × informalidade
- **Tipo:** `px.scatter` + `go.Scatter` de uma reta de regressão linear simples (calculada com `numpy.polyfit`, sem dependência de `statsmodels`).
- **Dados:** mesma base do heatmap, sem agregação.
- **Leitura:** confirma visualmente a correlação forte do heatmap — os pontos sobem da esquerda para a direita — e mostra que os pontos femininos e masculinos seguem a *mesma* reta, só deslocados pela diferença de escala populacional, reforçando que essa relação não diferencia os sexos do jeito que o rendimento diferencia.
- **Por que scatter + tendência, e não só o heatmap:** o heatmap dá o número (0,86), mas não a forma da relação. Um leitor que confia mais em "ver o padrão" do que em "ler um coeficiente" precisa do scatter.

---

## Capítulo 4 — Escolaridade

### 10. Barras agrupadas — nível de instrução por sexo
- **Tipo:** `px.bar(barmode="group")`.
- **Dados:** população média (mil) por nível de instrução × sexo, tabela 7322 (sem a categoria "Total").
- **Leitura:** distribuição similar na maior parte dos níveis; a diferença mais visível aparece em "Superior completo", onde a barra feminina supera a masculina.
- **Por que manter esse gráfico (já existia na v1):** é a forma mais direta de ver os valores absolutos antes de ver a versão normalizada (radar, abaixo) — funciona como "tabela visual" de apoio aos outros dois gráficos da página.

### 11. Radar — forma da distribuição educacional por sexo
- **Tipo:** `go.Scatterpolar`, 7 eixos (um por nível de instrução, excluindo "Total").
- **Dados:** % da população de cada sexo em cada nível (soma 100% por sexo) — não os valores absolutos, para que a comparação seja sobre *proporção*, não sobre tamanho populacional.
- **Leitura:** o polígono feminino se estica mais no eixo "Superior completo" (19,0% das mulheres vs. 14,6% dos homens); o masculino é ligeiramente maior nos eixos "Fundamental incompleto", "Fundamental completo" e "Médio completo". Ou seja, a vantagem feminina não é uniforme em todos os níveis — está concentrada exatamente no nível mais associado a remunerações mais altas.
- **Por que radar de novo, e com a mesma estrutura visual do capítulo anterior:** repetir o tipo de gráfico (mesma forma de leitura, mesma paleta de cor) faz o leitor reconhecer instantaneamente "este é o mesmo tipo de comparação de perfil que vi no capítulo anterior" — e perceber o contraste entre os dois radares (no capítulo 3, o polígono masculino era maior nos indicadores de mercado de trabalho; aqui, no de escolaridade, o polígono feminino é maior no nível mais qualificado) sem precisar de texto extra explicando.

### 12. Sunburst — população por sexo e nível de instrução
- **Tipo:** `px.sunburst(path=["sexo", "nivel_instrucao"])`.
- **Dados:** mesma base do gráfico 10, em formato hierárquico.
- **Leitura:** mesma informação do gráfico de barras, mas com a vantagem de mostrar a fatia de cada nível como proporção do total daquele sexo de forma mais direta visualmente (área da fatia = peso no total).
- **Por que incluir, ao lado do radar e das barras:** é deliberadamente redundante com os gráficos 10 e 11 — em um capítulo que carrega a "revelação" da história, vale reforçar o mesmo fato com uma terceira forma visual, para leitores que processam melhor proporção-de-todo (sunburst) do que forma-de-perfil (radar) ou valor-absoluto (barras).

---

## Capítulo 5 — Conclusão

### 13. Lista estruturada de hipóteses testadas
- **Tipo:** cartões Streamlit (`st.container(border=True)`) com ícone de veredito (❌ não explica / ⚠️ piora a pergunta / 🔁 confirma, não explica).
- **Dados:** síntese textual dos capítulos 2–4, sem novo cálculo.
- **Por que não é um gráfico de funil ou waterfall:** ver `dashboard/docs/storytelling.md`, seção "O que foi deliberadamente evitado". Uma lista com veredito explícito é mais honesta do que forçar os dados em um formato que sugere uma precisão quantitativa (causal) que a análise não tem.

### 14. Gauge de fechamento — gap salarial médio
- **Tipo:** igual ao gráfico 1 (capa), agora em uma única instância.
- **Por que repetir o mesmo gráfico da capa:** fecha o arco narrativo (bookending) — o leitor termina a investigação revendo o mesmo número que abriu a história, agora com contexto para interpretá-lo.
