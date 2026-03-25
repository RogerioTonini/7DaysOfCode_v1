"""
conftest.py  –  Raiz da suite de testes

Responsabilidades:
    1. Injetar variáveis de ambiente ANTES de qualquer importação dos módulos
        da aplicação (config_db.py e config_app.py lêem o ambiente no nível
        de módulo, portanto este bloco precisa ser executado no topo do arquivo,
        fora de qualquer fixture).
    2. Configurar o arquivo de log dos testes dinamicamente, usando LOGS_PATH
        do .env — o arquivo gerado será: <LOGS_PATH>/tests.log
    3. Fornecer fixtures compartilhadas entre todos os testes.
"""

import logging
import os
from pathlib import Path

import pytest

# Variáveis de ambiente – definidas ANTES de qualquer import da aplicação
# Usamos setdefault para não sobrescrever valores já presentes no ambiente.
# O load_dotenv nos módulos não afeta pois o arquivo .env não existe em CI.

_TEST_ENV: dict[str, str] = {
    "DB_USER": "test_user",
    "DB_PASSWORD": "test_password",
    "DB_NAME": "test_db",
    "DB_HOST": "localhost",
    "DB_PORT": "3306",
    "DEBUG": "False",
    "LOG_LEVEL": "DEBUG",
    "DATA_PATH": "/tmp/test_data",
    "LOGS_PATH": "test_logs",
}

for _key, _value in _TEST_ENV.items():
    os.environ.setdefault(_key, _value)


# Log de testes → <LOGS_PATH>/tests.log
# Lido do ambiente para respeitar o .env do projeto.
# A pasta é criada automaticamente se não existir.


def pytest_configure(config: pytest.Config) -> None:
    """
    Hook executado pelo pytest antes de qualquer coleta de testes.
    Define o destino do arquivo de log dinamicamente via LOGS_PATH.
    """
    logs_path: Path = Path(os.environ["LOGS_PATH"])
    logs_path.mkdir(parents=True, exist_ok=True)  # cria a pasta se não existir

    log_file: Path = logs_path / "tests.log"

    # Injeta as opções de log no config do pytest em tempo de execução
    config.option.log_file = str(log_file)
    config.option.log_file_level = "DEBUG"
    config.option.log_file_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    config.option.log_file_date_format = "%Y-%m-%d %H:%M:%S"

    # Informa ao usuário onde o log será gravado
    print(f"\n📄 Log dos testes: {log_file}\n")


# Imports e fixtures (após garantia das env vars)

from unittest.mock import MagicMock

import pandas as pd
from sqlalchemy.engine import Engine


@pytest.fixture
def mock_engine() -> tuple[MagicMock, MagicMock]:
    """
    Retorna (engine, conn_ctx): Engine e conexão SQLAlchemy totalmente mockados.

    Simula o padrão:
        with engine.connect() as conn:
            conn.execute(...)
            conn.commit()

    Uso nos testes:
        def test_algo(mock_engine):
            engine, conn = mock_engine
            engine.connect.return_value = conn  # já configurado
    """
    engine = MagicMock(spec=Engine)

    conn_ctx = MagicMock()
    conn_ctx.__enter__ = MagicMock(return_value=conn_ctx)
    conn_ctx.__exit__ = MagicMock(return_value=False)

    engine.connect.return_value = conn_ctx
    return engine, conn_ctx


@pytest.fixture
def df_pequeno() -> pd.DataFrame:
    """
    DataFrame com 5 linhas para testes de inserção.
    """
    return pd.DataFrame(
        {
            "col_a": ["v1", "v2", "v3", "v4", "v5"],
            "col_b": [10, 20, 30, 40, 50],
        }
    )


@pytest.fixture
def df_lotes() -> pd.DataFrame:
    """
    DataFrame com 7 linhas para forçar múltiplos lotes (lote=3 → 3 lotes).
    """
    return pd.DataFrame(
        {
            "col_a": [f"item_{i}" for i in range(7)],
            "col_b": range(7),
        }
    )


# Separador visual entre testes no console e no arquivo de log


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """
    Hook executado ao final de cada fase de um teste (setup, call, teardown).
    Imprime uma linha em branco após a fase 'call' (execução do teste),
    separando visualmente os resultados no console e no log.
    """
    if report.when == "call":
        print()
