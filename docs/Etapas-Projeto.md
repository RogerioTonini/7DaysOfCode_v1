# 7DaysOfCode.io - ALURA

## Exploração de dados de empréstimos dos acervos do sistema de bibliotecas da UFRN

## Etapas do projeto:

### _1ª Etapa - Base de dados_

- Importar os últimos 10 anos disponíveis.
- São 2 bases de dados:
  - Empréstimos dos acervos das bibliotecas,
  - Títulos dos exemplares do Acervo.

### _2ª Etapa - Tratamento dos dados_

- Dicionário de dados: Arquivo: DB-CadLivros.CSV

  A coluna [_**localizacao**_] - Os itens do acervo em uma biblioteca são organizados por um sistema de classificação de acordo com o respectivo tema. Existem diversos sistemas, mas este conjunto está de acordo com a _**CDU - Classificação Decimal Universal**_. Esta classificação é decimal, pois varia de acordo com a classe de cada assunto:

| _*ID CDU*_ | _*Descrição da CDU*_                     |
| ---------- | ---------------------------------------- |
| 000 a 099  | Generalidades, Ciência e conhecimento    |
| 100 a 199  | Filosofia e psicologia                   |
| 200 a 299  | Religião                                 |
| 300 a 399  | Ciências sociais                         |
| 400 a 499  | Classe vaga. Provisoriamente não ocupada |
| 500 a 599  | Matemática e ciências naturais           |
| 600 a 699  | Ciências aplicadas                       |
| 700 a 799  | Belas artes                              |
| 800 a 899  | Linguagem, Língua, Linguística           |
| 900 a 999  | Geografia, Biografia, História           |

#### _Regras de negócio:_

Criar uma nova coluna NomeFaixaCDU, inserir a descrição da tabela anterior de acordo com o código da coluna [_**localizacao**_].
Exclusão colunas: [_**localizacao**_] e [_**registro_sistema**_].
Converter a coluna [_**matricula_ou_siape**_] para STRING.

### 3ª Etapa - Exploração dos dados

Entender a quantidade e quando se emprestaram os livros é uma das primeiras formas de fazer uma análise desse tipo.
Como evoluíram os empréstimos com o decorrer do tempo?

A diretoria gostaria de entender se a quantidade de empréstimos está diminuindo, aumentando ou permanecendo igual ao decorrer dos últimos anos. Para isso, verifique qual é a quantidade total de exemplares emprestados por cada ano e plote um gráfico de linhas.

Faça uma análise em relação à visualização gerada. Obs.: Atente-se para a quantidade de exemplares emprestados, e não de empréstimos realizados.

A diretoria também gostaria de gerenciar melhor os recursos humanos da biblioteca de acordo com a demanda de trabalho existente. Por exemplo:

gerenciar a programação de férias dos colaboradores de acordo com os meses de menor demanda;
programar atividades que não sejam de atendimento ao usuário para períodos específicos de menor demanda.
Há uma suspeita interna de que os meses com maior número de exemplares emprestados sejam MARÇO e SETEMBRO, mas não foi realizada uma análise real sobre isso. Gere uma tabela com a Quantidade total de exemplares emprestados por mês e descubra quais meses são os que possuem a maior quantidade de empréstimos realizados.

Plote um gráfico linhas.
Traga suas análises em relação a quais meses poderiam ser as melhores opções. Além do gerenciamento anual das atividades, a diretoria também necessita que seja planejada uma programação diária das atividades. Por este motivo, verifique quais foram os horários com maior quantidade de empréstimos ao longo de um dia inteiro.

Plote um gráfico de barras e analise quais seriam os melhores horários para alocar as demais atividades que não sejam de atendimento ao usuário.

### 4ª Etapa - Exploração dos dados II

Explorar algumas das variáveis categóricas das quais precisaremos extrair mais informações. São elas:

- Tipo de vínculo
- Coleção
- Biblioteca
- Classificação geral da CDU

Alguns questionamentos são pertinentes para a diretoria das bibliotecas, como:

- Como se distribuem os empréstimos de exemplares pelos tipos de vínculo dos usuários? Desta forma, a diretoria poderá entender qual é o público que está utilizando a biblioteca e assim tomar decisões em continuar com a estratégia de negócio atual ou modificá-la.
- Quais coleções são mais emprestadas? Da mesma forma, as coleções. Ranquear as coleções mais emprestadas pelo público, será bastante importante para a estratégia atual.
- Quais são as bibliotecas com mais ou menos quantidade de empréstimos? Assim, a diretoria conseguirá entender onde ela deverá melhorar e focar suas iniciativas.
- De quais temas da CDU são os exemplares emprestados? Entender quais os temas mais procurados pelos usuários é fundamental para o desenvolvimento de novos planos de marketing do acervo. Para que possam não apenas fortalecer o que está sendo utilizado, mas também promover o que não está.

### 5ª Etapa - Desenvolver estratégias para o uso da informação

#### _Contexto:_

Devido às diversas mudanças que ocorrem o tempo todo: os usuários estão evoluindo seus conhecimentos, novos alunos chegam, alunos que se formam saem e as informações estão sempre em movimento e transformação.

Por este motivo, é importante realizar avaliações constantes do uso da biblioteca e entender em quais cenários:

- tipos de usuários,
- estratégias de marketing,
- atualização de acervo,
- cenário sócio político (interno e externo) é melhor manter a estratégia atual ou mudá-la

#### _Demanda:_

Fazer dois recortes em seus dados para entender como eles se distribuíram ao decorrer desses anos e, desta forma, possa trazer inferências para levar à diretoria da biblioteca, a fim de que eles possam tomar decisões para o ano atual. Para isso, você vai avaliar dentre os alunos de graduação e pós graduação a distribuição de empréstimos mensais por ano realizados entre 2010 e 2020 da coleção que tiver a maior frequência de empréstimos.

Plote um gráfico para cada tipo de usuário.
Tenha um boxplots para cada ano e analise o que ocorreu.

Dica: Desenvolva a tarefa uma etapa por vez:

- Q qual é a coleção com maior frequência para cada tipo de usuário.
- Filtre os dados com condições solicitadas.
- Selecione apenas os empréstimos.
- Faça a contagem de empréstimos mensais por cada ano.
- Crie uma função para gerar a visualização do gráfico de box plot por cada ano.
- Crie o gráfico de _boxplot_.

#### _Respostas a serem entregue_

1-) O que está ocorrendo ao decorrer do tempo? Houve algum ano ou anos em específico que te chamaram atenção para alguma diferença?
2-) Quais as maiores diferenças entre os empréstimos para os alunos de graduação e pós graduação?

### 6ª Etapa - Enriquecendo as análises

#### _Contexto:_

As instituições de ensino superior (IES) têm a necessidade de passar por avaliações do Ministério da Educação (MEC) para que possam ofertar e continuar ofertando cursos de graduação e pós-graduação. A biblioteca universitária faz parte de um dos indicadores da avaliação dos cursos, em principalmente três aspectos: acervo, infraestrutura e serviços. Dentre os serviços, são avaliados se existem recursos de bases referenciais para pesquisa, se há treinamentos para os usuários utilizarem os materiais, e a presença de indicadores sobre o uso dos materiais do acervo (empréstimos, consultas) dentre outros tópicos.

#### _Demanda:_

Calcular a quantidade de empréstimos realizados entre 2015 e 2020 por cada curso de graduação que passará pela avaliação.
Os cursos serão:

- Biblioteconomia
- Ciências sociais
- Comunicação social
- Direito
- Filosofia
- Pedagogia

A universidade forneceu os dados dos usuários, mas uma parte deles está em planilhas de Excel, a outra parte veio através de uma API do sistema em formato JSON.

Extraia os dados destes arquivos, agrupe-os em apenas um só, e verifique depois a quantidade de empréstimos.

Gere uma tabela com as seguintes características:

- Índice: Cursos
- Colunas: Ano
- Valores: Quantidade de empréstimos
- Total: Acrescente uma linha e uma coluna de total a tabela

#### _*Regra Geral: Garanta que a coluna de matrícula dos alunos estejam no mesmo formato de dados e não tenha nenhum dado nulo.*_

### 7ª Etapa - Plano de ação de Marketing

#### _*Contexto:*_

A diretoria da biblioteca está montando uma ação de marketing focado nos alunos da pós-graduação. Para isso, precisará analisar a diferença percentual de empréstimos realizados nos últimos anos (2017, 2018, 2019) para cada curso.

Devido à pandemia do COVID-19, ela não poderá utilizar os dados de 2020 e 2021. Entretanto, seu colega de equipe já realizou uma análise de previsão de empréstimos de 2022 e a disponibilizou para que você também possa realizar o comparativo entre 2019-2022.

#### _*Demanda :*_

Você precisará criar uma tabela com as diferenças percentuais de empréstimos entre 2017-2018, 2018-2019, 2019-2022. Porém, essa análise será disponibilizada em conjunto com outros dados, através de uma página da web, e a equipe de Front-end te solicitou que enviassem para eles o HTML da tabela.

Eles precisam que ela tenha as seguintes características:

- Não contenha numeração de índice;
- Os nomes dos cursos tenham apenas a primeira letra maiúscula;
- Os números percentuais estejam indicados pelo símbolo “%”;
- Cor dos números: Positivos = Verde; Negativos = Vermelho
