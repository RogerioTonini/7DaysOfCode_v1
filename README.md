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

Layout dos arquivos - https://github.com/RogerioTonini/7DaysOfCode_v1/blob/main/Documentacao/Estrutura-Dados.md

Etapas do projeto - https://github.com/RogerioTonini/7DaysOfCode_v1/blob/main/docs/Etapas-Projeto.md

## Tecnologias utilizadas

- IDE - Visual Studio Code - 1.109.3
- Python - versão 3.11.3
- PIPX - 1.8.0
- ipython - 8.12.3
- Pyenv - 3.1.1
- Poetry - 1.8.5

## Instalação

## Atualização GitHub - Push Inicial

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
