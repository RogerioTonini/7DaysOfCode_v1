# Procedimentos

1. Analise da base de Dados

- **1.1.** Arquivos: **emprestimos-20nn[1 ou 2].csv**

  **1.1.1.** Perído de análise: 10 anos e 6 meses.

  **1.1.2.** Quantidade de arquivos: 21 arquivos (cada ano possui 2 arquivos semestrais e o último (2020), somente o 1º semestre)

  **1.1.3.** Repositório dos dados Dia 1: [Repositório de dados](https://github.com/FranciscoFoz/7_Days_of_Code_Alura-Python-Pandas/blob/main/Dia_1-Importando_dados/Datasets/dados_emprestimos/)

  **1.1.4.** Repositório dos dados Dia 6: [Novos dados, Novas Análises](https://github.com/FranciscoFoz/7_Days_of_Code_Alura-Python-Pandas/tree/main/Dia_6-Novos_dados_novas_analises/Datasets)

  **1.1.5.** Estrutura dos dados:

| _*#*_ | _*Column*_           | _*Dtype*_      | _*Descrição do Campo*_                                                     | _*Ação a ser realizada na coluna*_             |
| :---: | :------------------- | :------------- | :------------------------------------------------------------------------- | :--------------------------------------------- |
|   1   | id_emprestimo        | int64          | ID do empréstimo                                                           |                                                |
|   2   | codigo_barras        | object         | Código de barras do produto (livro)                                        |                                                |
|   3   | data_renovacao       | datetime64[ns] | Data da renovação do empréstimo                                            | Transformar a coluna em Data/Time 23:59:59.999 |
|   4   | data_emprestimo      | datetime64[ns] | Data inicial do empréstimo                                                 | Transformar a coluna em Data/Time 23:59:59.999 |
|   5   | data_devolucao       | datetime64[ns] | Data devolução                                                             | Transformar a coluna em Data/Time 23:59:59.999 |
|   6   | tipo_vinculo_usuario | object         | Tipo de vínculo do usuário: Aluno (Graduação, Pós-Graduação), Docente, etc |                                                |

- **1.2.** Arquivo: **dados_exemplares.parquet**

  **1.2.1.** Quantidade de arquivos: 1 arquivo

  **1.2.2.** Repositório dos dados: [Dados referente aos empréstimos dos livros](https://github.com/FranciscoFoz/7_Days_of_Code_Alura-Python-Pandas/blob/main/Dia_1-Importando_dados/Datasets/)

  **1.2.3.** Estrutura dos dados:

| _*#*_ | Column           | Dtype  | Descrição do Campo                     | Ação a ser realizada na coluna                 |
| :---: | ---------------- | ------ | -------------------------------------- | ---------------------------------------------- |
|   1   | index            | int64  | Índice                                 |                                                |
|   2   | id_exemplar      | int64  | ID Exemplar                            |                                                |
|   3   | codigo_barras    | object | Código de barras do produto            |                                                |
|   4   | colecao          | object | Tipo da coleção pertencente o exemplar |                                                |
|   5   | biblioteca       | object | Localização física do exemplar         |                                                |
|   6   | status_material  | object | Situação em que se encontra o material |                                                |
|   7   | localizacao      | int64  | CDU - Classificação Decimal Universal  | Criar coluna CDU_exemplar, conforme requisitos |
|   8   | registro_sistema | int64  | Registro do sistema                    | Excluir coluna                                 |

- **1.3.** Arquivo: **matricula_alunos.xlsx**

  **1.3.1.** Quantidade de arquivos: 1 arquivo

  **1.3.2.** Repositório dos dados: [Novos dados, Novas Análises](https://github.com/FranciscoFoz/7_Days_of_Code_Alura-Python-Pandas/tree/main/Dia_6-Novos_dados_novas_analises/Datasets)

  **1.3.3.** Arquivo possui 2 planilhas: **Até 2010** e **Depois 2010**. Os dados referem-se as matrículas realizadas nos períodos. As 2 planilhas possuem a mesma estrutura.

  **1.3.4.** Estrutura dos dados:

| _*#*_ | Column              | Dtype   | Descrição do Campo      | Ação a ser realizada na coluna |
| :---: | ------------------- | ------- | ----------------------- | ------------------------------ |
|   1   | Número da matrícula | float64 | Índice                  |                                |
|   2   | Tipo de vinculo     | str     | GRADUAÇÃO, PÓSGRADUAÇÃO |                                |
|   3   | Curso               | str     | Descrição do curso      |                                |

- **1.4.** Arquivo: **cadastro_alunos.json**

  **1.4.1.** Quantidade de arquivos: 1 arquivo

  **1.4.2.** Repositório dos dados: [Novos dados, Novas Análises](https://github.com/FranciscoFoz/7_Days_of_Code_Alura-Python-Pandas/tree/main/Dia_6-Novos_dados_novas_analises/Datasets)

  **1.4.3.** Arquivo possui 2 planilhas: **Até 2010** e **Depois 2010**. Os dados referem-se as matrículas realizadas nos períodos. As 2 planilhas possuem a mesma estrutura.

  **1.4.4.** Estrutura dos dados:

| _*#*_ | Column              | Dtype   | Descrição do Campo      | Ação a ser realizada na coluna |
| :---: | ------------------- | ------- | ----------------------- | ------------------------------ |
|   1   | Número da matrícula | float64 | Índice                  |                                |
|   2   | Tipo de vinculo     | str     | GRADUAÇÃO, PÓSGRADUAÇÃO |                                |
|   3   | Curso               | str     | Descrição do curso      |                                |
