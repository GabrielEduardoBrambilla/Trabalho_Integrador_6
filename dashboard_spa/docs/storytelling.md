# Design do dashboard — gap salarial na Região Sul

## Histórico: por que duas versões antes desta

A primeira versão tinha 3 abas genéricas com filtros soltos — funcional, mas sem
profundidade analítica (gráficos isolados, sem indicar o que olhar). A segunda
versão corrigiu a profundidade, mas foi longe demais na direção oposta: um app
multipage com um capítulo por página e parágrafos de texto explicando cada
gráfico como uma reportagem. Bom para ensinar o achado a alguém que nunca viu os
dados; ruim como ferramenta de trabalho — um analista que já conhece o domínio
não quer ler 5 páginas de prosa para chegar a um número.

Esta versão consolida as duas: **um único dashboard, uma única tela**, com
filtros globais persistentes e a profundidade analítica da v2 (radar, gauges,
bolhas animadas), mas sem capítulos nem texto narrativo — exatamente o formato
que um analista de dados sênior entrega para um time que vai usar o dashboard
no dia a dia, não lê-lo uma vez como reportagem.

## Princípios de design

1. **Filtros globais, não estáticos.** UF e período (ano) ficam na sidebar e
   recalculam todos os gráficos e KPIs — nenhum número no dashboard é fixo.
   Isso é o que diferencia uma ferramenta de BI de uma série de imagens.
2. **KPI strip acima da dobra.** As cinco métricas mais importantes (gap médio,
   rendimento por sexo, correlação ocupação×informalidade, vantagem educacional
   feminina) aparecem no topo, sempre visíveis, antes de qualquer gráfico —
   o que um executivo vê em 3 segundos de olhada.
3. **Texto mínimo, só onde o gráfico não fala por si.** Cada gráfico tem um
   título direto (não uma pergunta retórica) e, quando necessário, uma legenda
   de uma linha — nunca um parágrafo. A explicação detalhada de cada gráfico
   (o porquê da escolha, os números por trás) fica em
   `dashboard/docs/analise_graficos.md`, não na tela.
4. **Três grupos, não três páginas.** `st.tabs()` organiza os gráficos em
   "Mercado de Trabalho", "Investigação" e "Escolaridade" — uma navegação
   leve, sem recarregar a página nem sair da URL, diferente do app multipage
   anterior (que tinha 5 scripts separados e uma barra de navegação lateral
   dedicada a "capítulos").
5. **Sem redundância visual.** A v2 tinha 14 elementos visuais, alguns
   mostrando o mesmo fato de formas diferentes (ex.: bar + radar + sunburst
   para a mesma distribuição educacional). Esta versão usa 9, removendo o
   treemap de contexto, o sunburst e o scatter+tendência — cada gráfico
   remanescente cobre um ângulo que nenhum outro cobre.

## Identidade visual

Mantida de `theme.py`: **Feminino = rosa (`#D6336C`)**, **Masculino = azul
(`#2C6E9B`)**, sempre — é a âncora visual de todo o dashboard. UFs com cores
fixas (PR verde-petróleo, SC laranja, RS roxo). Um template Plotly único
(`pm3_gap`) garante consistência tipográfica em todos os gráficos.

## Estrutura final

```
KPI strip (5 métricas, recalculadas pelos filtros da sidebar)
├── Tab "Mercado de Trabalho"
│   ├── Rendimento médio por sexo e UF (borboleta)      Gap médio por UF (barras)
│   ├── Evolução trimestral do gap (linha, com lacuna anotada)
│   └── Distribuição do rendimento por UF/sexo (boxplot)
├── Tab "Investigação"
│   ├── Correlação entre indicadores (heatmap)          Perfil normalizado por sexo (radar)
│   └── Rendimento × Informalidade × Ocupação (bolhas animadas)
└── Tab "Escolaridade"  [dataset de contexto — não joinável ao principal]
    ├── KPIs de Superior completo (Fem./Masc./diferença)
    └── Distribuição educacional (radar)                 População por nível (barras)
```

## O que foi removido da v2, e por quê

- **5 páginas → 1 página com 3 abas.** Multipage cria a sensação de "capítulos
  de um livro" — bom para uma reportagem, ruim para um painel de consulta
  rápida e recorrente.
- **Parágrafos narrativos → títulos + 1 legenda curta por gráfico.** O
  raciocínio completo (por que cada gráfico, o que ele prova) continua
  documentado, mas em `analise_graficos.md`, não competindo por atenção na
  tela com os próprios dados.
- **Treemap de "Cenário" e sunburst de "Escolaridade":** redundantes com
  gráficos que já mostram a mesma informação de forma mais direta (KPIs e
  barras). Um dashboard enterprise não duplica visualização do mesmo fato.
- **Scatter + linha de tendência (capítulo Investigação):** a mesma
  informação (correlação ocupação×informalidade) já está no heatmap, de forma
  mais densa e sem precisar de um segundo gráfico.
- **Cartões de "hipóteses testadas" e gauge de fechamento (capítulo
  Conclusão):** eram recursos de fechamento de uma narrativa linear; em um
  dashboard de uso recorrente, sem capítulos, não há "fechamento" — o usuário
  entra, lê os KPIs e os gráficos relevantes ao que precisa, e sai.
