# 7DaysOfCode.io - ALURA

## Exploração de dados de empréstimos dos acervos do sistema de bibliotecas da UFRN

## Estrutura de pastas

```
├── 📁 .githooks-scripts
│   └── 📄 commit-mensagem                  # Backup do .git\hooks\commit-msg
│
├── 📁 .vscode                              # Configurações do VSCode/Antigravity
│   ├── ⚙️ extensions.json
│   ├── ⚙️ launch.json
│   ├── ⚙️ settings.json
│   └── ⚙️ tasks.json
│
├── 📁 app
│   ├── 📁 model
│   │   ├── 📁 cdu
│   │   │   ├── 🐍 __init__.py
│   │   │   ├── 🐍 config_cdu.py            # Configuração da tabela CDU
│   │   │   └── 🐍 create_tb_cdu.py         # Criação da tabela CDU
│   │   │
│   │   ├── 📁 emprestimos
│   │   │   ├── 🐍 __init__.py
│   │   │   ├── 🐍 config_emprestimos.py    # Configuração da tabela EMPRESTIMOS
│   │   │   └── 🐍 create_tb_raw.py         # Criação da tabela RAW
│   │   │
│   ├── 🐍 __init__.py
│   ├── 🐍 config_db.py                     # Configuração do banco de dados
│   ├── 🐍 connect.py                       # Conexão com o banco de dados
│   ├── 🐍 create_db.py                     # Criação do banco de dados
│   └── 🐍 util_model.py                    # Utilitários do modelo
│
├── 📁 pipeline
│   ├── 🐍 __init__.py
│   ├── 🐍 load_cdu.py                      # Carga os dados da tabela CDU
│   └── 🐍 load_emprestimos.py              # Carga os dados da tabela EMPRESTIMOS
│
├── 📁 utils
│   ├── 🐍 __init__.py
│   ├── 🐍 config_log.py                    # Configuração do log
│   └── 🐍 utilitarios.py                   # Funções utilizadas em diversas partes do projeto
│
├── 📁 notebooks
│   └── 📄 info-Dados.ipynb                 # Exploração dos dados
│
├── 📁 tests
│   ├── 📁 model
│   │   ├── 🐍 __init__.py
│   │   ├── 🐍 test_config_db.py            # Testes de configuração do banco de dados
│   │   ├── 🐍 test_connect.py              # Testes de conexão com o banco de dados
│   │   ├── 🐍 test_create_db.py            # Testes de criação do banco de dados
│   │   └── 🐍 test_util_model.py           # Testes de utilitários do modelo
│   │
│   ├── 🐍 __init__.py
│   └── 🐍 conftest.py                      # Configurações do pytest
│
├── 🐍 __init__.py
├── 🐍 config_app.py                        # Configuração da aplicação
├── ⚙️ .gitattributes                      # Atributos do git
├── ⚙️ .gitignore                          # Arquivos ignorados pelo git
├── 📄 LICENSE                              # Licença do projeto
├── 📝 README.md                            # README do projeto
├── 📄 poetry.lock                          # Lock do poetry
├── 📄 pytest.ini                           # Configuração de inicialização do pytest
└── ⚙️ pyproject.toml                      # Configuração do poetry
```

