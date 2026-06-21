### 1. Apresentação

Neste Projeto Mensal 3, você deverá escolher uma base de dados real e realizar todo o processo de tratamento, limpeza, transformação, normalização, padronização e documentação dos dados.

O objetivo principal deste projeto é fazer você compreender que, antes de construir dashboards, relatórios ou aplicar técnicas de Data Mining, é necessário preparar corretamente os dados. Dados com erros, valores ausentes, duplicidades, categorias desorganizadas ou formatos inconsistentes podem gerar análises erradas e decisões ruins.

Neste projeto, você não precisa desenvolver um sistema completo. Também não precisa, obrigatoriamente, criar um dashboard final. O foco principal será o **tratamento dos dados** .

Você deverá partir de uma base de dados bruta e chegar a uma base final tratada, organizada, confiável e documentada.

O fluxo geral do projeto será:

**Base bruta → análise da qualidade → limpeza → pré-processamento → transformação → normalização → feature engineering → documentação → dataset final tratado**

### 2. Objetivo geral

Aplicar técnicas de tratamento de dados para preparar uma base real para uso em projetos de Business Intelligence, Data Mining e análise de dados.

### 3. O que você deverá fazer

Você deverá escolher uma base de dados real, analisar sua estrutura, identificar problemas de qualidade, aplicar técnicas de limpeza e transformação, criar novas variáveis quando necessário e entregar uma versão final tratada e documentada.

A base de dados poderá ser sobre qualquer tema, desde que permita análise e tratamento. Exemplos de temas:

Educação, saúde, segurança pública, meio ambiente, transporte, vendas, turismo, agricultura, mercado de trabalho, dados públicos, atendimento ao cliente, tecnologia, redes sociais, finanças públicas ou outro tema aprovado pelo professor.

A escolha do tema é livre, mas a base precisa ter dados suficientes para que você consiga aplicar as técnicas solicitadas.

### 6. Etapas obrigatórias do projeto

### 6.1 Planejamento do tratamento dos dados

Nesta etapa, você deverá explicar qual base escolheu e por que ela é relevante para análise.

Você deverá responder:

Qual é o tema da base?

De onde os dados foram retirados?

Qual problema ou situação essa base ajuda a compreender?

Quem poderia usar esses dados para tomar decisão?

Como essa base poderia ser utilizada em Business Intelligence?

Como essa base poderia ser utilizada em Data Mining?

Quais perguntas poderiam ser respondidas com esses dados?

Exemplo:

Se você escolher uma base de vendas, poderá analisar quais produtos vendem mais, quais regiões têm melhor desempenho, quais meses possuem maior faturamento e quais categorias apresentam maior crescimento.

Se escolher uma base educacional, poderá analisar desempenho dos alunos, evasão, frequência, notas, perfil dos estudantes ou evolução por período.

Se escolher uma base de saúde, poderá analisar atendimentos, regiões com maior demanda, sazonalidade, tipos de ocorrência ou tempo de espera.

Nesta etapa, você deverá entregar um texto explicando o contexto da base e o objetivo da análise.

### 6.2 Relação com Big Data Analytics, Data Mining e BI

Você deverá explicar como a base escolhida se relaciona com os conceitos de Big Data Analytics, Data Mining e Business Intelligence.

Não basta copiar definições genéricas. Você deverá aplicar os conceitos ao seu próprio tema.

Você deverá explicar:

Como os dados poderiam apoiar decisões?

Quais padrões poderiam ser descobertos?

Que tipo de análise poderia ser feita?

A base poderia ser usada em dashboards?

A base poderia ser usada para classificação, agrupamento, previsão ou descoberta de padrões?

Exemplo:

Em uma base de clientes, Data Mining poderia ser usado para identificar grupos de consumidores com comportamento parecido.

Em uma base de ocorrências urbanas, poderia ser usado para descobrir regiões com maior concentração de problemas.

Em uma base de vendas, poderia ser usado para prever demanda ou identificar produtos mais associados.

### 6.3 Modelagem inicial dos dados

Você deverá observar a estrutura da base e identificar como os dados estão organizados.

Você deverá apresentar:

Quantidade de linhas e colunas.

Nome das principais colunas.

Quais colunas são numéricas.

Quais colunas são categóricas.

Quais colunas representam datas ou períodos.

Quais colunas poderiam ser usadas como dimensões em BI.

Quais colunas poderiam ser usadas como medidas.

Exemplo:

Em uma base de vendas, as dimensões poderiam ser produto, cliente, cidade, estado e data. As medidas poderiam ser quantidade vendida, valor unitário, valor total e desconto.

Você não precisa criar um Data Warehouse completo neste projeto, mas precisa demonstrar que entende como a base poderia ser organizada para análise em BI.

### 6.4 Diagnóstico da qualidade dos dados

Nesta etapa, você deverá analisar a qualidade da base original.

Você deverá verificar se existem:

Valores ausentes.

Linhas duplicadas.

Colunas com nomes inadequados.

Tipos de dados incorretos.

Datas em formato errado.

Textos com espaços extras.

Categorias escritas de formas diferentes.

Valores numéricos fora do padrão.

Outliers.

Colunas sem utilidade.

Dados inconsistentes.

Exemplo de problemas:

A mesma categoria escrita como “PR”, “Paraná”, “parana” e “PARANA”.

Datas armazenadas como texto.

Valores monetários com vírgula, ponto e símbolo de real misturados.

Campos vazios.

Registros repetidos.

Nesta etapa, você deverá apresentar uma tabela ou descrição com os problemas encontrados.

### 6.5 Análise Exploratória de Dados

Você deverá realizar uma análise exploratória da base antes e/ou depois do tratamento.

A Análise Exploratória de Dados serve para entender o comportamento dos dados.

Você deverá apresentar:

Estatísticas descritivas das variáveis numéricas.

Frequência das variáveis categóricas.

Gráficos de distribuição.

Gráficos de comparação.

Identificação de padrões.

Identificação de possíveis relações entre variáveis.

Análise de valores extremos.

Análise temporal, se a base possuir datas.

Você poderá usar gráficos como:

Gráfico de barras.

Histograma.

Boxplot.

Gráfico de linha.

Gráfico de setores, quando adequado.

Mapa de calor de correlação, se fizer sentido.

O importante não é apenas gerar gráficos. Você precisa explicar o que os gráficos mostram.

### 6.6 Seleção dos dados

Você deverá escolher quais colunas e registros serão mantidos para o dataset final.

Você deverá justificar:

Quais colunas foram mantidas.

Quais colunas foram removidas.

Quais registros foram filtrados.

Por que determinadas informações foram descartadas.

Quais variáveis são importantes para a análise.

A seleção precisa ter justificativa técnica. Não remova colunas apenas porque “não quis usar”.

### 6.7 Limpeza e pré-processamento dos dados

Nesta etapa, você deverá aplicar o tratamento inicial dos dados.

Você deverá realizar ações como:

Renomear colunas.

Padronizar nomes de colunas.

Corrigir tipos de dados.

Converter datas.

Remover duplicidades.

Corrigir categorias inconsistentes.

Padronizar textos.

Corrigir valores inválidos.

Tratar valores ausentes.

Preparar a base para análise.

Exemplo:

Antes:

Data Venda, VALOR R$, nome_cliente, Estado

Depois:

data_venda, valor, nome_cliente, estado

O objetivo é deixar a base mais organizada, padronizada e pronta para as próximas etapas.

### 6.8 Tratamento de valores faltantes

Você deverá identificar os valores ausentes da base e decidir como tratá-los.

Você poderá:

Remover registros com muitos valores ausentes.

Remover colunas sem utilidade.

Preencher valores com média.

Preencher valores com mediana.

Preencher valores com moda.

Preencher valores com uma categoria como “Não informado”.

Preencher valores com base em grupos.

Manter o valor ausente, desde que justifique.

Você deverá apresentar a quantidade de valores ausentes antes e depois do tratamento.

Atenção: não basta aplicar dropna() em toda a base sem explicar. Isso pode eliminar dados importantes.

### 6.9 Tratamento de outliers

Você deverá verificar se existem valores extremos nas variáveis numéricas.

Você poderá identificar outliers usando:

Boxplot.

Intervalo interquartil, conhecido como IQR.

Z-score.

Análise visual.

Regras de negócio.

Depois de identificar os outliers, você deverá decidir o que fazer com eles.

Você poderá:

Manter o valor, caso ele represente uma situação real.

Remover o registro, se for erro evidente.

Substituir o valor por um limite aceitável.

Aplicar transformação matemática.

Criar uma coluna indicando se aquele registro é outlier.

Você deverá justificar sua decisão. Outlier não é automaticamente erro. Às vezes ele é justamente o dado mais importante da análise.

### 6.10 Transformação dos dados

Você deverá transformar os dados para deixá-los mais adequados à análise.

Exemplos de transformação:

Converter texto em número.

Converter texto em data.

Criar coluna de ano, mês ou trimestre.

Criar faixas de valores.

Agrupar categorias.

Padronizar nomes.

Converter valores monetários.

Transformar variáveis categóricas.

Criar indicadores.

O objetivo é melhorar a utilidade dos dados para BI e Data Mining.

### 6.11 Agregação de dados

Você deverá realizar pelo menos uma agregação de dados.

Agregação significa resumir os dados por algum grupo.

Exemplos:

Total de vendas por mês.

Quantidade de alunos por curso.

Média de nota por turma.

Número de atendimentos por cidade.

Receita por categoria.

Quantidade de ocorrências por estado.

Média de tempo de atendimento por tipo de serviço.

Você deverá apresentar a tabela agregada e explicar o que ela mostra.

### 6.12 Normalização e padronização dos dados

Você deverá aplicar normalização ou padronização em pelo menos uma variável numérica.

Essa etapa é importante quando os dados possuem escalas muito diferentes ou quando podem ser usados em técnicas de Data Mining e Machine Learning.

Você poderá usar:

Pandas.

NumPy.

Scikit-learn.

Técnicas possíveis:

Min-Max Scaling.

StandardScaler.

RobustScaler.

Normalização manual.

Você deverá explicar:

Quais colunas foram normalizadas.

Qual técnica foi usada.

Por que essa técnica foi escolhida.

Qual a diferença entre os dados antes e depois.

### 6.13 Discretização dos dados

Você deverá transformar pelo menos uma variável numérica em categorias ou faixas.

Exemplos:

Idade → jovem, adulto, idoso.

Valor de venda → baixo, médio, alto.

Nota → baixo desempenho, médio desempenho, alto desempenho.

Tempo de atendimento → curto, médio, longo.

Renda → baixa, média, alta.

Você poderá usar:

pd.cut().

pd.qcut().

Regras manuais.

Faixas por quartis.

Faixas por critérios de negócio.

Você deverá apresentar a variável original e a nova variável discretizada.

### 6.14 Feature Engineering

Você deverá criar novas variáveis a partir dos dados existentes.

Feature Engineering significa criar atributos que ajudem a melhorar a análise.

Exemplos:

Criar ano, mês e trimestre a partir de uma data.

Criar idade a partir da data de nascimento.

Criar tempo_de_atendimento a partir da diferença entre duas datas.

Criar valor_total a partir de quantidade e preço unitário.

Criar percentual_crescimento.

Criar faixa_etaria.

Criar indicador_de_atraso.

Criar categoria_de_risco.

As novas variáveis precisam ter utilidade analítica. Não crie colunas apenas para aumentar o tamanho da base.

### 6.15 Consolidação do dataset final tratado

Ao final do tratamento, você deverá gerar uma nova base de dados.

Essa base final deverá estar:

Limpa.

Padronizada.

Sem duplicidades indevidas.

Com valores ausentes tratados ou justificados.

Com outliers analisados.

Com colunas relevantes.

Com novas variáveis criadas.

Com nomes de colunas claros.

Com tipos de dados corretos.

Pronta para uso em BI, Data Mining ou análise exploratória.

Você deverá entregar esse dataset final em formato CSV, XLSX ou outro formato autorizado pelo professor.

### 6.16 Catálogo de dados

Você deverá criar um catálogo de dados do dataset final.

O catálogo serve para documentar o significado de cada coluna.

O catálogo deverá conter:

Nome da coluna.

Descrição da coluna.

Tipo de dado.

Exemplo de valor.

Origem da coluna.

Tratamento aplicado.

Indicação se a coluna é original ou criada.

Uso esperado na análise.

Exemplo:

| Coluna      | Descrição                       | Tipo       | Exemplo    | Origem        | Tratamento aplicado         | Uso              |
| ----------- | ------------------------------- | ---------- | ---------- | ------------- | --------------------------- | ---------------- |
| data_venda  | Data em que a venda ocorreu     | Data       | 2024-05-10 | Base original | Conversão para datetime     | Análise temporal |
| valor_total | Valor total da venda            | Numérico   | 250.90     | Criada        | Quantidade x valor unitário | Medida           |
| faixa_valor | Classificação do valor da venda | Categórico | Alto       | Criada        | Discretização               | Segmentação      |

### 6.17 DataOps e organização do projeto

Você deverá organizar os arquivos do projeto de forma clara.

A ideia é que outra pessoa consiga entender e reproduzir o que você fez.

Sugestão de estrutura:

PM3_Tratamento_Dados/

│

├── dados_brutos/

│ └── base_original.csv

│

├── dados_tratados/

│ └── dataset_final_tratado.csv

│

├── notebooks/

│ └── tratamento_dados_pm3.ipynb

│

├── documentacao/

│ ├── catalogo_dados.xlsx

│ └── relatorio_final.pdf

│

└── README.md

Você deverá preservar a base original e entregar o código usado no tratamento.

O processo precisa ser reprodutível. Ou seja, o professor deve conseguir executar seu notebook ou script e chegar ao mesmo dataset final.

### 7. Entregáveis obrigatórios

Ao final do PM3, você deverá entregar:

1. Base de dados original.
2. Dataset final tratado.
3. Notebook ou script Python utilizado no tratamento.
4. Relatório final.
5. Catálogo de dados.
6. Evidências da análise exploratória.
7. Tabela com problemas de qualidade encontrados.
8. Descrição das etapas de limpeza.
9. Demonstração do tratamento de valores faltantes.
10. Demonstração do tratamento de outliers.
11. Demonstração de transformação dos dados.
12. Demonstração de agregação dos dados.
13. Demonstração de normalização ou padronização.
14. Demonstração de discretização.
15. Demonstração de Feature Engineering.
16. Explicação sobre como a base poderia ser usada em BI e Data Mining.

### 8. Estrutura sugerida do relatório final

O relatório final deverá conter:

1. Introdução.
2. Tema escolhido.
3. Fonte dos dados.
4. Objetivo da análise.
5. Descrição da base original.
6. Relação da base com BI, Big Data Analytics e Data Mining.
7. Diagnóstico da qualidade dos dados.
8. Análise Exploratória de Dados.
9. Seleção das variáveis.
10. Limpeza e pré-processamento.
11. Tratamento de valores faltantes.
12. Tratamento de outliers.
13. Transformações realizadas.
14. Agregações realizadas.
15. Normalização e padronização.
16. Discretização.
17. Feature Engineering.
18. Descrição do dataset final.
19. Catálogo de dados.
20. Organização DataOps.
21. Conclusão.
22. Limitações.
23. Próximos passos.

### 9. Orientações importantes

A base deve ser real. A fonte dos dados deve ser informada. A base original deve ser preservada. O dataset final deve ser diferente da base original.

Todas as decisões de tratamento devem ser justificadas.

O notebook ou script deve estar organizado e executável. Não basta mostrar código; é necessário explicar o que foi feito. Não basta gerar gráficos; é necessário interpretar os resultados.

Não serão aceitos trabalhos apenas teóricos. Não serão aceitos datasets tratados sem documentação.

O foco do projeto é a qualidade do dado.

### 10. Resultado esperado

Ao final do PM3, espera-se que você consiga demonstrar domínio sobre o processo de preparação de dados para Business Intelligence.

Você deverá mostrar que sabe sair de uma base bruta, identificar problemas, corrigir inconsistências, transformar variáveis, normalizar dados, criar novas informações úteis e documentar o dataset final.

Em outras palavras, você deverá provar que sabe preparar dados antes de analisá-los.

No mundo real, essa etapa é decisiva. Um dashboard bonito com dados ruins continua sendo ruim — só que mais colorido.
