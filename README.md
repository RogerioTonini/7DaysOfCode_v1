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

## Tecnologias utilizadas

- IDE - Visual Studio Code - 1.109.3
- Python - versão 3.11.3
- PIPX - 1.8.0
- ipython - 8.12.3
- Pyenv - 3.1.1
- Poetry - 1.8.5

## Extensões do VSCode que tenho habilitadas no projeto

| _*Nome da extensão*_                          | _*ID Identifier*_                                          |
| --------------------------------------------- | ---------------------------------------------------------- |
| autoDocstring - Python Docstring Generator    | njpwerner.autodocstring                                    |
| Auto Rename Tag                               | formulahendry.auto-rename-tag                              |
| Bash Debug                                    | rogalmic.bash-debug                                        |
| Brazilian Portuguese - Code Spell Checker     | streetsidesoftware.code-spell-checker-portuguese-brazilian |
| Code Runner                                   | formulahendry.code-runner                                  |
| Code Spell Checker                            | streetsidesoftware.code-spell-checker                      |
| Draw.io Integration                           | hediet.vscode-drawio                                       |
| GitHub Copilot Chat                           | github.copilot-chat                                        |
| GitHub Issue Notebooks                        | ms-vscode.vscode-github-issue-notebooks                    |
| GitHub Pull Requests                          | github.vscode-pull-request-github                          |
| Jupyter                                       | ms-toolsai.jupyter                                         |
| Jupyter Keymap                                | ms-toolsai.jupyter-keymap                                  |
| Jupyter Notebook Rendere                      | ms-toolsai.jupyter-renderers                               |
| Jupyter Cell Tags                             | ms-toolsai.vscode-jupyter-cell-tags                        |
| Live Server                                   | ritwickdey.liveserver                                      |
| Markdown All in One                           | yzhang.markdown-all-in-one                                 |
| Markdown Preview Github Styling               | bierner.markdown-preview-github-styles                     |
| Notepad++ keymap                              | ms-vscode.notepadplusplus-keybindings                      |
| Prettier - Code formatter                     | esbenp.prettier-vscode                                     |
| Python Indent                                 | kevinrose.vsc-python-indent                                |
| Python                                        | ms-python.python                                           |
| Python                                        | ms-python.python                                           |
| Python                                        | ms-python.python                                           |
| Pylance                                       | ms-python.vscode-pylance                                   |
| Test Adapter Converter                        | ms-vscode.test-adapter-converter                           |
| shell-format                                  | foxundermoon.shell-format                                  |
| ShellCheck                                    | timonwong.shellcheck                                       |
| Test Explorer UI                              | hbenl.vscode-test-explorer                                 |
| vscode-icons                                  | vscode-icons-team.vscode-icons                             |
| vscode-pdf                                    | tomoki1207.pdf                                             |
| vscode-solution-explorer                      | fernandoescolar.vscode-solution-explorer                   |
| vscode-styled-components                      | styled-components.vscode-styled-components                 |
| VS Code Jupyter Notebook Previewer            | jithurjacob.nbpreviewer                                    |

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

## Estrutura do projeto

```
├── 📁 .githooks-scripts
│   └── 📄 commit-mensagem            # Backup do .git\hooks\commit-msg
│
├── 📁 .vscode
│   ├── 📝 extensions.json
│   ├── 📝 launch.json
│   ├── 📝 settings.json
│   └── 📝 tasks.json
│
├── 📁 app
│   ├── 📄 info-Dados.ipynb           # Informações sobre a estrutura de dados
│   └── 📄 main.ipynb                 # Faz o processo de ETL
│
│
├── 📁 docs
│   ├── 📝 Dicas-Solucoes.md          # Dicas e as Soluções do Autor
│   ├── 📝 Estrutura-Dados.md         # Estrutura dos dados ao efetuar o ETL
│   └── 📝 Etapas-Projeto.md          # Etapas do Projeto
│
├── ⚙️ .gitattributes
├── ⚙️ .gitignore
├── 📄 LICENSE
├── 📝 README.md
├── 📄 poetry.lock
└── ⚙️ pyproject.toml
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
git add .python-version pyproject.toml poetry.lock
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
git add README.md
git commit -m "docs: adicionar README.md com informações do projeto"
```

### Commit: App

```bash
git add app/
git commit -m "feat(app): criar estrutura base da aplicação"
```

### Commit: Testes

```bash
git add tests/
git commit -m "test: adicionar estrutura de testes"
```

## Execução

O arquivo _**main.ipynb**_ é responsável por realizar a etapa de ETL.
Criei  uma *Contante* chamada _*PATH_BASE*_, responsável por armazenar o local onde serão gravados os diversos arquivos gerados no processo.
Altere o conteúdo para pasta que desejar.

_**Importante:**_ Como os arquivos gerados podem ser maiores que 100GB e o GitHub não aceita arquivos maiores que isso porque o objetivo não é armazenar dados.
