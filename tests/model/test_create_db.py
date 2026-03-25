"""
tests/model/test_create_db.py
==============================
Testes unitários para  app/model/create_db.py

Cobertura:
┌──────────────────────┬────────────────────────────────────────────────────┐
│ Alvo                 │ Cenários                                           │
├──────────────────────┼────────────────────────────────────────────────────┤
│ _engine_sem_banco()  │ sucesso → Engine                                   │
│                      │ OperationalError → None                            │
│                      │ SQLAlchemyError  → None                            │
│                      │ Exception genérica → None                          │
│                      │ string sem banco na URL                            │
├──────────────────────┼────────────────────────────────────────────────────┤
│ _banco_existe()      │ banco existe → True                                │
│                      │ banco não existe → False                           │
│                      │ query SQL contém parâmetro correto                 │
├──────────────────────┼────────────────────────────────────────────────────┤
│ create_database()    │ banco já existe → True, sem CREATE                 │
│                      │ banco não existe → True, executa CREATE            │
│                      │ DDL de criação contém utf8mb4                      │
│                      │ engine None → False                                │
│                      │ OperationalError → False                           │
│                      │ SQLAlchemyError  → False                           │
│                      │ engine.dispose() chamado no finally                │
└──────────────────────┴────────────────────────────────────────────────────┘
"""

from unittest.mock import MagicMock, call, patch

import pytest
from sqlalchemy import exc
from sqlalchemy.engine import Engine


def _engine_mock_ok():
    """
    Retorna (engine, conn_ctx) com comportamento de conexão bem-sucedida.

    Função gerada pela Claude AI
    """
    mock_conn = MagicMock()
    mock_conn.execute.return_value = (
        None  # Simula que execute() não retorna nada
    )

    mock_conn_ctx = MagicMock()
    mock_conn_ctx.__enter__.return_value = mock_conn
    mock_conn_ctx.__exit__.return_value = None

    mock_engine = MagicMock(spec=Engine)
    mock_engine.connect.return_value = mock_conn_ctx
    return mock_engine, mock_conn_ctx


# Testes: _engine_sem_banco()


class Test_Engine_Without_DB:
    """
    Testa _engine_sem_banco(): engine administrativo sem DB especificado.
    """

    @patch("app.model.create_db.create_engine")
    def test_return_engine_when_connect_ok_40(self, mock_create_engine):
        """
        Conexão administrativa bem-sucedida → Engine retornado.
        """
        engine, conn_ctx = _engine_mock_ok()
        mock_create_engine.return_value = engine

        from app.model.create_db import _engine_sem_banco

        resultado = _engine_sem_banco()

        assert resultado is engine

    @patch("app.model.create_db.create_engine")
    def test_connection_string_does_not_contain_db_name_41(
        self, mock_create_engine
    ):
        """
        A URL administrativa NÃO deve incluir o DB_NAME na connection string.
        """
        import os

        engine, _ = _engine_mock_ok()
        mock_create_engine.return_value = engine

        from app.model.create_db import _engine_sem_banco

        _engine_sem_banco()

        conn_str: str = mock_create_engine.call_args[0][0]
        assert os.environ["DB_NAME"] not in conn_str

    @patch("app.model.create_db.create_engine")
    def test_connection_string_contains_the_host_and_port_42(
        self, mock_create_engine
    ):
        """
        Host e porta devem constar na connection string administrativa.
        """
        import os

        engine, _ = _engine_mock_ok()
        mock_create_engine.return_value = engine

        from app.model.create_db import _engine_sem_banco

        _engine_sem_banco()

        conn_str: str = mock_create_engine.call_args[0][0]
        assert os.environ["DB_HOST"] in conn_str
        assert os.environ["DB_PORT"] in conn_str

    @patch("app.model.create_db.create_engine")
    def test_returns_none_on_operational_error_43(self, mock_create_engine):
        """
        OperationalError na conexão administrativa → None.
        """
        engine = MagicMock(spec=Engine)
        engine.connect.side_effect = exc.OperationalError(
            "stmt", {}, Exception()
        )
        mock_create_engine.return_value = engine

        from app.model.create_db import _engine_sem_banco

        assert _engine_sem_banco() is None

    @patch("app.model.create_db.create_engine")
    def test_returns_none_on_sqlalchemy_error_44(self, mock_create_engine):
        """
        SQLAlchemyError genérico → None.
        """
        engine = MagicMock(spec=Engine)
        engine.connect.side_effect = exc.SQLAlchemyError("erro alchemy")
        mock_create_engine.return_value = engine

        from app.model.create_db import _engine_sem_banco

        assert _engine_sem_banco() is None

    @patch("app.model.create_db.create_engine")
    def test_returns_none_on_generic_exception_45(self, mock_create_engine):
        """
        Qualquer Exception não prevista → None.
        """
        mock_create_engine.side_effect = Exception("driver indisponível")

        from app.model.create_db import _engine_sem_banco

        assert _engine_sem_banco() is None


# Testes: _banco_existe()


class Test_DB_Exists:
    """Testa _banco_existe(): consulta ao information_schema."""

    def test_returns_true_when_db_found_46(self):
        """fetchone retorna tupla → banco existe → True."""
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = ("meu_banco",)

        from app.model.create_db import _banco_existe

        assert _banco_existe(mock_conn, "meu_banco") is True

    def test_returns_false_when_db_not_found_47(self):
        """fetchone retorna None → banco não existe → False."""
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = None

        from app.model.create_db import _banco_existe

        assert _banco_existe(mock_conn, "banco_inexistente") is False

    def test_query_uses_parameter_correct_name_48(self):
        """O nome do banco deve ser passado como parâmetro na query."""
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = None

        from app.model.create_db import _banco_existe

        _banco_existe(mock_conn, "meu_banco_teste")

        # Verifica que o segundo argumento do execute contém o nome do banco
        call_kwargs = mock_conn.execute.call_args[0]
        assert call_kwargs[1] == {"nome": "meu_banco_teste"}

    def test_consult_information_schema_schemata_49(self):
        """
        A query deve consultar information_schema.SCHEMATA.
        """
        mock_conn = MagicMock()
        mock_conn.execute.return_value.fetchone.return_value = None

        from app.model.create_db import _banco_existe

        _banco_existe(mock_conn, "qualquer")

        sql_executado: str = str(mock_conn.execute.call_args[0][0])
        assert (
            "SCHEMATA" in sql_executado.upper()
            or "information_schema" in sql_executado.lower()
        )


# Testes: create_database()


class Test_Create_DB:
    """
    Testa create_database(): verificação e criação do banco de dados.
    """

    # Caminho feliz – banco já existe

    @patch("app.model.create_db._banco_existe")
    @patch("app.model.create_db._engine_sem_banco")
    def test_returns_true_when_db_already_exists_50(
        self, mock_engine_fn, mock_banco_existe
    ):
        """
        Banco pré-existente → retorna True sem executar CREATE DATABASE.
        """
        engine, conn_ctx = _engine_mock_ok()
        mock_engine_fn.return_value = engine
        mock_banco_existe.return_value = True

        from app.model.create_db import create_database

        assert create_database() is True

    @patch("app.model.create_db._banco_existe")
    @patch("app.model.create_db._engine_sem_banco")
    def test_does_not_execute_create_when_db_already_exists_51(
        self, mock_engine_fn, mock_banco_existe
    ):
        """
        Se banco existir, conn.execute NÃO deve ser chamado
        (apenas SELECT de existência).
        """
        engine, conn_ctx = _engine_mock_ok()
        mock_conn = conn_ctx.__enter__.return_value
        mock_engine_fn.return_value = engine
        mock_banco_existe.return_value = True

        from app.model.create_db import create_database

        create_database()

        # mock_conn é o objeto retornado pelo __enter__ do context manager
        # pois _banco_existe já foi mockado externamente
        mock_conn.execute.assert_not_called()

    # Caminho feliz – banco não existe

    @patch("app.model.create_db._banco_existe")
    @patch("app.model.create_db._engine_sem_banco")
    def test_returns_true_and_creates_db_when_not_exists_52(
        self, mock_engine_fn, mock_banco_existe
    ):
        """
        Banco inexistente → retorna True e executa CREATE DATABASE.
        """
        engine, conn_ctx = _engine_mock_ok()
        mock_engine_fn.return_value = engine
        mock_banco_existe.return_value = False

        from app.model.create_db import create_database

        assert create_database() is True

    @patch("app.model.create_db._banco_existe")
    @patch("app.model.create_db._engine_sem_banco")
    def test_create_database_when_database_does_not_exist_53(
        self, mock_engine_fn, mock_banco_existe
    ):
        """
        Deve chamar conn.execute ao criar o banco.
        """
        engine, conn_ctx = _engine_mock_ok()
        mock_conn = conn_ctx.__enter__.return_value
        mock_engine_fn.return_value = engine
        mock_banco_existe.return_value = False

        from app.model.create_db import create_database

        create_database()

        # mock_conn é o objeto retornado pelo __enter__ do context manager
        mock_conn.execute.assert_called_once()

    @patch("app.model.create_db._banco_existe")
    @patch("app.model.create_db._engine_sem_banco")
    def test_ddl_creation_contains_utf8mb4_54(
        self, mock_engine_fn, mock_banco_existe
    ):
        """
        O DDL de CREATE DATABASE deve especificar charset utf8mb4.
        """
        engine, conn_ctx = _engine_mock_ok()
        mock_conn = conn_ctx.__enter__.return_value
        mock_engine_fn.return_value = engine
        mock_banco_existe.return_value = False

        from app.model.create_db import create_database

        create_database()

        ddl: str = str(mock_conn.execute.call_args[0][0])
        assert "utf8mb4" in ddl

    @patch("app.model.create_db.db_cfg")  # mock de db_cfg
    @patch("app.model.create_db._banco_existe")
    @patch("app.model.create_db._engine_sem_banco")
    def test_ddl_contains_db_name_55(
        self, mock_engine_fn, mock_banco_existe, mock_db_cfg
    ):
        # Define DB_NAME como string no mock
        mock_db_cfg.DB_NAME = "teste_db"

        engine, conn_ctx = _engine_mock_ok()
        mock_conn = conn_ctx.__enter__.return_value
        mock_engine_fn.return_value = engine
        mock_banco_existe.return_value = False

        from app.model.create_db import create_database

        create_database()

        ddl: str = str(mock_conn.execute.call_args[0][0])

        # # Assert usa o valor do mock, não os.environ
        assert mock_db_cfg.DB_NAME in ddl

    # Tratamento de erros
    @patch("app.model.create_db._engine_sem_banco")
    def test_returns_false_when_engine_sem_banco_returns_none_56(
        self, mock_engine_fn
    ):
        """
        Engine administrativo None → create_database retorna False.
        """
        mock_engine_fn.return_value = None

        from app.model.create_db import create_database

        assert create_database() is False

    @patch("app.model.create_db._banco_existe")
    @patch("app.model.create_db._engine_sem_banco")
    def test_returns_false_em_operational_error_57(
        self, mock_engine_fn, mock_banco_existe
    ):
        """
        OperationalError durante verificação → retorna False.
        """
        engine, conn_ctx = _engine_mock_ok()
        mock_engine_fn.return_value = engine
        mock_banco_existe.side_effect = exc.OperationalError(
            "stmt", {}, Exception()
        )

        from app.model.create_db import create_database

        assert create_database() is False

    @patch("app.model.create_db._banco_existe")
    @patch("app.model.create_db._engine_sem_banco")
    def test_returns_false_em_sqlalchemy_error_58(
        self, mock_engine_fn, mock_banco_existe
    ):
        """
        SQLAlchemyError genérico → retorna False.
        """
        engine, conn_ctx = _engine_mock_ok()
        mock_engine_fn.return_value = engine
        mock_banco_existe.side_effect = exc.SQLAlchemyError("erro")

        from app.model.create_db import create_database

        assert create_database() is False

    @patch("app.model.create_db._banco_existe")
    @patch("app.model.create_db._engine_sem_banco")
    def test_returns_false_em_except_generic_59(
        self, mock_engine_fn, mock_banco_existe
    ):
        """
        Exception inesperada → retorna False.
        """
        engine, conn_ctx = _engine_mock_ok()
        mock_engine_fn.return_value = engine
        mock_banco_existe.side_effect = Exception("falha inesperada")

        from app.model.create_db import create_database

        assert create_database() is False

    # Garantia do finally

    @patch("app.model.create_db._banco_existe")
    @patch("app.model.create_db._engine_sem_banco")
    def test_engine_dispose_and_called_in_finally_on_success_60(
        self, mock_engine_fn, mock_banco_existe
    ):
        """
        engine.dispose() DEVE ser chamado no bloco finally (caminho feliz).
        """
        engine, conn_ctx = _engine_mock_ok()
        mock_engine_fn.return_value = engine
        mock_banco_existe.return_value = True

        from app.model.create_db import create_database

        create_database()

        engine.dispose.assert_called_once()

    @patch("app.model.create_db._banco_existe")
    @patch("app.model.create_db._engine_sem_banco")
    def test_engine_dispose_and_called_in_finally_on_error_61(
        self, mock_engine_fn, mock_banco_existe
    ):
        """
        engine.dispose() DEVE ser chamado no finally mesmo when há exceção.
        """
        engine, conn_ctx = _engine_mock_ok()
        mock_engine_fn.return_value = engine
        mock_banco_existe.side_effect = exc.SQLAlchemyError("erro")

        from app.model.create_db import create_database

        create_database()

        engine.dispose.assert_called_once()
