# Projeto: 7DaysOfCode.io - ALURA

## Exploração de dados de empréstimos dos acervos do sistema de bibliotecas da UFRN

## Objetivo:

Os empréstimos realizados podem ser um indicador, mesmo que de forma básica (pois você não consegue garantir que haja uma leitura ou utilização real).

Por este motivo, entender a quantidade de empréstimos se torna importante.

Questões de diferentes perspectivas podem surgir como:

- A quantidade de empréstimos está aumentando ou diminuindo ao decorrer dos últimos anos?
- Em quais bibliotecas do sistema estão a maior quantidade de empréstimos?
- Quais são os temas mais emprestados? E os menos?
- Quais os horários de maior e menor movimento?

Com estas e outras informações será possível entender o cenário e apresentá-lo à diretoria das bibliotecas, para que possam tomar melhores decisões na melhoria da infraestrutura, dos recursos e processos da unidade de informação.

## Documentação

Autor: Francisco Foz - https://github.com/FranciscoFoz/7_Days_of_Code_Alura-Python-Pandas

Layout dos arquivos - https://github.com/RogerioTonini/7DaysOfCode_v1/blob/main/docs/Estrutura-Dados.md

Etapas do projeto - https://github.com/RogerioTonini/7DaysOfCode_v1/blob/main/docs/Etapas-Projeto.md

Estrutura de pastas - https://github.com/RogerioTonini/7DaysOfCode_v1/blob/main/docs/Estrutura-Pastas.md

## Tecnologias utilizadas

- _**IDE**_: Visual Studio Code ou Antigravity
- _**Banco de dados**_: MySQL

| _**Skill**_ | _**Versão**_ |
| - | - |
| Python |  3.11.3 |
| PIPX | 1.8.0 |
| ipython | 8.12.3 |
| Pyenv | 3.1.1 |
| Poetry | 1.8.5 |
| python-dotenv | 1.2.2 |
| sqlalchemy | 2.0.48 |
| psycopg2-binary | 2.9.11 |
| pytest | 9.0.2 |
| pytest-cov | 7.1.0 |
| mysql-connector-python | 9.6.0 |

## Procedimentos de instalação

1. Faça o clone do repositório
  ```bash
   git clone https://github.com/RogerioTonini/7DaysOfCode_v1.git
  ```

2. Entre no diretório
  ```bash
   cd 7DaysOfCode_v1
  ```

3. Execute o comando para o Poetry administrar o ambiente virtual
  ```bash
  poetry config virtualenvs.in-project true
  ```

4. Informe ao Poetry a versão do Python que você utilizará no projeto
  ```bash
  poetry env use 3.11.3
  ```

5. Instalação das bibliotecas utilizadas no projeto
  poetry install

#### _*Importante:*_
  Ao término da instalação de todas as bibliotecas do projeto, você receberá a  mensagem _**warning**_:

  ```bash
  Warning: The current project could not be installed: No file/folder found for package 7daysofcode-v1
  If you do not want to install the current project use --no-root.
  If you want to use Poetry only for dependency management but not for packaging, you can disable package mode by setting package-mode = false in your pyproject.toml file.
  In a future version of Poetry this warning will become an error!
  ```

  **Não se preocupe, esta mensagem é apenas um aviso que a pasta _**7daysofcode-v1**_ não foi encontrada, porém o projeto funcionará normalmente.**

6. Copiar o arquivo de .githooks-scripts/commit-msg para .git/hooks
  ```bash
  cp -r .githooks-scripts/. .git/hooks/
  ```

7. Criar a pasta config e o arquivo .env.
  ```bash
  mkdir config
  cd config
  touch .env
  ```

8. Adicionar as variáveis de ambiente no arquivo .env
  ```bash
  DB_USER     = 'usuario'               # Usuário proprietário do banco de dados
  DB_PASSWORD = '[senha]'               # Senha do usuário proprietário do banco de dados
  DB_NAME     = 'db_bibliotecas_ufrn'   # Nome do banco de dados

  # Aplicação
  DEBUG     = True                     # Ativa o modo debug
  LOG_LEVEL = DEBUG                    # Nível de log
  ```

## Atualização no GitHub - Push Inicial

### Commit: Estrutura inicial - Git

```bash
git add .gitignore .gitattributes .githooks-scripts/
git commit -m "chore(git):
- Adicionar .gitignore, - Adicionar .gitattributes para normalização de arquivos e
configurar tratamento de arquivos binários,
- Adicionar scripts de hooks para Conventional Commits"
```

### Commit: Versão do Python e Dependências do Projeto

```bash
git add .python-version pyproject.toml
git commit -m "build:
- Configuração da versão do Python utilizada no projeto,
- Configuração do Poetry e bibliotecas (dependências) do projeto"
```

### Commit: Configurações do VSCode

```bash
git add .vscode/
git commit -m "chore(vscode): adicionar configurações do editor"
```

### Commit: README.md

```bash
git add README.md docs/.
git commit -m "docs: adicionado documentação do projeto"
```

### Commit: App

```bash
git add main.py app/.
git commit -m "feat(app): adicionado estrutura base da aplicação"
```

### Commit: Testes

```bash
git add pytest.ini tests/
git commit -m "test: adicionado estrutura de testes"
```

## Execução

