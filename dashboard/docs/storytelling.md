# Storytelling do dashboard — "Elas estudam mais. Elas ganham menos."

## Por que reformular o dashboard

A primeira versão do dashboard (3 abas com filtros genéricos: "Gap salarial",
"Contexto: escolaridade", "Sobre os dados") era uma ferramenta de **exploração**:
o usuário filtrava e via gráficos, sem que o dashboard guiasse a um raciocínio.
Funcionalmente correta, mas sem tensão narrativa — não conduzia a lugar nenhum.

Esta versão é uma ferramenta de **explicação**. Ela assume que o leitor não
conhece os dados, e o conduz por uma investigação com início, meio e fim:
um achado intrigante (hook) → contexto necessário para confiar nos números →
a evidência do problema → a tentativa de explicá-lo por causas mais simples →
a reviravolta que descarta a explicação mais óbvia → a conclusão. Essa estrutura
é o arco clássico de **data storytelling** (ver Cole Nussbaumer Knaflic,
*Storytelling with Data*, e o modelo "hook → context → conflict → resolution"
usado em jornalismo de dados).

## Estrutura escolhida: app multipage, não abas

Trocamos `st.tabs()` por um app multipage do Streamlit (`dashboard/pages/`), com
um capítulo por página, numerado e na ordem da história:

| Arquivo | Capítulo | Papel na história |
|---|---|---|
| `app.py` | Capa | **Hook** — o achado mais chocante, em uma frase e 4 números |
| `pages/1_📖_Cenario.py` | Cenário | **Contexto** — de onde vêm os dados, por que há dois datasets |
| `pages/2_💰_O_Gap_Salarial.py` | O Gap Salarial | **Conflito** — o tamanho do problema, sob vários ângulos |
| `pages/3_🔍_Investigacao.py` | Investigação | **Tentativa de explicação simples** — será que é ocupação/informalidade? |
| `pages/4_🎓_Escolaridade.py` | Escolaridade | **Reviravolta** — a explicação mais citada (educação) não só falha, como se inverte |
| `pages/5_🧭_Conclusao.py` | Conclusão | **Resolução** — o que foi descartado, o que sobra, limitações |

Por que multipage em vez de abas: abas sugerem "visões paralelas e
intercambiáveis" do mesmo assunto — o leitor pode abrir qualquer uma primeiro,
sem perder nada. Capítulos numerados, com um título de página na barra lateral,
sugerem **ordem** — o leitor sabe que "Investigação" pressupõe ter visto
"O Gap Salarial", e que "Conclusão" é, de fato, o fim. A barra lateral do
Streamlit (gerada automaticamente a partir de `dashboard/pages/`) funciona como
um sumário do livro.

## Identidade visual consistente

Definida uma única vez em `dashboard/theme.py` e reutilizada em todas as
páginas — sem isso, cada gráfico "recomeça do zero" para o leitor, que precisa
reaprender as cores a cada tela.

- **Feminino = rosa (`#D6336C`) / Masculino = azul (`#2C6E9B`)**, sempre, em
  todos os 8 gráficos que comparam sexo. É a âncora visual da história inteira:
  o leitor aprende essas duas cores na capa e nunca precisa reaprendê-las.
- **Cada UF tem uma cor fixa** (PR verde-petróleo, SC laranja, RS roxo),
  reutilizada nos gráficos de evolução temporal, treemap e gráfico de bolhas.
- Um template Plotly único (`pm3_gap`, em `theme.py`) garante fontes, grades e
  legendas com a mesma aparência em todo o dashboard.

## O arco, capítulo a capítulo

### Capa — o gancho
Abre com a frase mais forte que os dados sustentam: mulheres ganham ~32% menos
que homens, **mesmo tendo mais formação superior**. Isso é dito *antes* de
qualquer gráfico — o leitor já sabe o que vai ser investigado e por quê. Os
gauges de gap por UF (Paraná, Santa Catarina, Rio Grande do Sul) tornam o
número abstrato em algo visualmente concreto e comparável entre estados.

### Capítulo 1 — Cenário
Antes de mostrar mais números, o leitor precisa confiar na fonte e entender uma
decisão estrutural importante: **por que existem dois datasets, e não um**. Sem
esse capítulo, o leitor chegaria ao capítulo "Escolaridade" sem entender por que
ele não tem os mesmos filtros de UF/trimestre dos outros — pareceria um defeito,
quando é uma decisão deliberada de qualidade de dados (ver
`docs/relatorio_final.md`, seção 22).

### Capítulo 2 — O Gap Salarial
Estabelece o "conflito" da história sob quatro ângulos complementares: a
diferença média (gráfico borboleta), a evolução no tempo (linha, com a lacuna da
pandemia anotada), a relação entre rendimento/informalidade/ocupação ao longo do
tempo (bolhas animadas) e a robustez do achado (boxplot — não é só a média que
está deslocada, é a distribuição inteira). Multiplicar os ângulos sobre o mesmo
fato (o gap existe e é grande) constrói confiança antes de seguir para a
investigação das causas.

### Capítulo 3 — Investigação
O leitor já viu *que* o gap existe; agora a história testa **por quê**. As duas
hipóteses mais "inocentes" — homens trabalham mais, homens estão mais expostos
à informalidade — são testadas com o heatmap de correlação, o radar de perfil
normalizado e o scatter com linha de tendência. As três visualizações convergem
para o mesmo veredito: essas variáveis não explicam o tamanho do gap.

### Capítulo 4 — Escolaridade
A reviravolta. A hipótese mais citada no senso comum — "homens ganham mais
porque têm mais qualificação" — não só falha como **se inverte**: mulheres têm
mais Superior completo, em proporção, que homens. O capítulo usa exatamente os
mesmos elementos visuais do capítulo 3 (radar, mesma paleta) para que o
contraste seja imediato: o leitor já sabe ler um radar de "perfil normalizado
por sexo"; ao ver o segundo radar (educação), a comparação é automática.

### Capítulo 5 — Conclusão
Resolução do arco: lista as hipóteses testadas, o veredito de cada uma, e
fecha repetindo o número da capa (mesmo gauge, mesmo número) — um recurso de
"bookending" que sinaliza ao leitor que o ciclo da investigação se fechou.
Termina com as limitações reais da análise (não é estudo causal) e os próximos
passos já documentados no relatório final do PM3.

## O que foi deliberadamente evitado

- **Mapa coroplético dos estados:** exigiria um GeoJSON externo (risco de
  dependência de rede em ambiente sem internet garantida) só para reproduzir
  uma comparação que o treemap e os gráficos por UF já cobrem. Optou-se por não
  arriscar um elemento visual frágil por um ganho marginal de estética.
- **Gráfico de funil (funnel chart):** cogitado para a conclusão, mas exigiria
  tratar grupos não sequenciais (mulheres ocupadas → mulheres com diploma →
  mulheres bem pagas) como se fossem estágios de um único funil, o que
  distorceria a leitura. Preferiu-se uma lista estruturada de hipóteses
  testadas, mais honesta com o que os dados realmente permitem afirmar.
- **Decomposição "waterfall" do gap** (quanto da diferença viria de
  ocupação/informalidade/escolaridade): exigiria uma regressão multivariada
  formal, fora do escopo de tratamento de dados do PM3. O dashboard mostra a
  evidência que descarta essas explicações, mas não finge quantificar uma
  decomposição causal que os dados não sustentam.
