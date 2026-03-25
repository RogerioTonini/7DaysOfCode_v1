"""
tests/model/test_connect.py
============================
Testes unitários para  app/model/connect.py

Cobertura:
┌─────────────────┬───────────────────────────────────────────────────────┐
│ Alvo            │ Cenários                                              │
├─────────────────┼───────────────────────────────────────────────────────┤
│ connect_db()    │ sucesso → Engine retornado                            │
│                 │ OperationalError  → None                              │
│                 │ SQLAlchemyError   → None                              │
│                 │ Exception genérica → None                             │
│                 │ string de conexão montada corretamente                │
├─────────────────┼───────────────────────────────────────────────────────┤
│ test_connect()  │ tudo OK → True                                        │
│                 │ create_database falha → False (sem chamar connect_db) │
│                 │ connect_db retorna None → False                       │
│                 │ connect_db levanta exceção → False                    │
└─────────────────┴───────────────────────────────────────────────────────┘

Estratégia de mock:
    - create_engine é substituído em app.model.connect (onde é usado, não onde
    é definido) para isolar a lógica sem abrir sockets reais.
    - create_database é mockado via patch no namespace de connect.py.
"""

from unittest.mock import MagicMock, call, patch

import pytest
from sqlalchemy import exc
from sqlalchemy.engine import Engine


# Funções auxiliares internas
def _engine_mock_ok() -> tuple[MagicMock, MagicMock]:
    """
    Retorna (engine, conn_ctx) com comportamento de conexão bem-sucedida.
    """
    engine = MagicMock(spec=Engine)
    conn_ctx = MagicMock()
    conn_ctx.__enter__ = MagicMock(return_value=conn_ctx)
    conn_ctx.__exit__ = MagicMock(return_value=False)
    engine.connect.return_value = conn_ctx
    return engine, conn_ctx


class Test_Connect_DB:
    """
    Testa a função connect_db().
    """

    @patch("app.model.connect.create_engine")
    def test_returns_engine_when_connect_successful_22(
        self, mock_create_engine
    ):
        """
        Deve retornar o Engine when SELECT 1 é executado sem erros.
        """
        engine, conn_ctx = _engine_mock_ok()
        mock_create_engine.return_value = engine

        from app.model.connect import connect_db

        resultado = connect_db()

        assert resultado is engine

    @patch("app.model.connect.create_engine")
    def test_create_engine_e_chamado_uma_vez_23(self, mock_create_engine):
        """
        create_engine deve ser chamado exatamente uma vez.
        """
        engine, _ = _engine_mock_ok()
        mock_create_engine.return_value = engine

        from app.model.connect import connect_db

        connect_db()

        mock_create_engine.assert_called_once()

    @patch("app.model.connect.db_cfg")  # patcha db_cfg diretamente
    @patch("app.model.connect.create_engine")
    def test_string_de_connect_contem_host_porta_banco_24(
        self,
        mock_create_engine,
        mock_db_cfg,  # ordem: baixo→ cima nos decoradores
    ):
        """
        A connection string passada ao create_engine deve conter host,
        porta e banco.
        """
        mock_db_cfg.DB_USER = "test_user"
        mock_db_cfg.DB_PASSWORD = "test_password"
        mock_db_cfg.DB_NAME = "test_db"
        mock_db_cfg.DB_HOST = "test_host"
        mock_db_cfg.DB_PORT = "3307"

        engine, _ = _engine_mock_ok()
        mock_create_engine.return_value = engine

        from app.model.connect import connect_db

        connect_db()

        conn_str: str = mock_create_engine.call_args[0][0]
        assert mock_db_cfg.DB_HOST in conn_str  # usa mock, não os.environ
        assert mock_db_cfg.DB_PORT in conn_str
        assert mock_db_cfg.DB_NAME in conn_str

    @patch("app.model.connect.create_engine")
    def test_string_de_connect_usa_driver_mysqlconnector_25(
        self, mock_create_engine
    ):
        """
        O driver mysql + mysqlconnector deve estar presente na connection string.
        """
        engine, _ = _engine_mock_ok()
        mock_create_engine.return_value = engine

        from app.model.connect import connect_db

        connect_db()

        conn_str: str = mock_create_engine.call_args[0][0]
        assert "mysql+mysqlconnector" in conn_str

    @patch("app.model.connect.create_engine")
    def test_string_de_connect_tem_charset_utf8mb4_26(self, mock_create_engine):
        """
        charset=utf8mb4 deve estar na connection string.
        """
        engine, _ = _engine_mock_ok()
        mock_create_engine.return_value = engine

        from app.model.connect import connect_db

        connect_db()

        conn_str: str = mock_create_engine.call_args[0][0]
        assert "utf8mb4" in conn_str

    # Tratamento de erros
    @patch("app.model.connect.create_engine")
    def test_retorna_none_em_operational_error_no_connect_27(
        self, mock_create_engine
    ):
        """
        OperationalError ao abrir conexão -> retorna None.
        """
        engine = MagicMock(spec=Engine)
        engine.connect.side_effect = exc.OperationalError(
            "stmt", {}, Exception()
        )
        mock_create_engine.return_value = engine

        from app.model.connect import connect_db

        assert connect_db() is None

    @patch("app.model.connect.create_engine")
    def test_retorna_none_em_sqlalchemy_error_28(self, mock_create_engine):
        """
        SQLAlchemyError genérico -> retorna None.
        """
        engine = MagicMock(spec=Engine)
        engine.connect.side_effect = exc.SQLAlchemyError("erro alchemy")
        mock_create_engine.return_value = engine

        from app.model.connect import connect_db

        assert connect_db() is None

    @patch("app.model.connect.create_engine")
    def test_retorna_none_em_except_generic_29(self, mock_create_engine):
        """
        Exception genérica (ex: ImportError de driver) → retorna None.
        """
        mock_create_engine.side_effect = Exception("driver não encontrado")

        from app.model.connect import connect_db

        assert connect_db() is None

    @patch("app.model.connect.create_engine")
    def test_retorna_none_when_execute_falha_30(self, mock_create_engine):
        """
        Falha no SELECT 1 de validação → retorna None.
        """
        engine = MagicMock(spec=Engine)
        conn_ctx = MagicMock()
        conn_ctx.__enter__ = MagicMock(return_value=conn_ctx)
        conn_ctx.__exit__ = MagicMock(return_value=False)
        conn_ctx.execute.side_effect = exc.OperationalError(
            "stmt", {}, Exception()
        )
        engine.connect.return_value = conn_ctx
        mock_create_engine.return_value = engine

        from app.model.connect import connect_db

        assert connect_db() is None

    # Tratamento de erros
    @patch("app.model.connect.create_engine")
    def test_retorna_none_em_operational_error_no_connect_31(
        self, mock_create_engine
    ):
        """
        OperationalError ao abrir conexão → retorna None.
        """
        engine = MagicMock(spec=Engine)
        engine.connect.side_effect = exc.OperationalError(
            "stmt", {}, Exception()
        )
        mock_create_engine.return_value = engine

        from app.model.connect import connect_db

        assert connect_db() is None

    @patch("app.model.connect.create_engine")
    def test_retorna_none_em_sqlalchemy_error_32(self, mock_create_engine):
        """
        SQLAlchemyError genérico → retorna None.
        """
        engine = MagicMock(spec=Engine)
        engine.connect.side_effect = exc.SQLAlchemyError("erro alchemy")
        mock_create_engine.return_value = engine

        from app.model.connect import connect_db

        assert connect_db() is None

    @patch("app.model.connect.create_engine")
    def test_retorna_none_em_except_generic_33(self, mock_create_engine):
        """
        Exception genérica (ex: ImportError de driver) → retorna None.
        """
        mock_create_engine.side_effect = Exception("driver não encontrado")

        from app.model.connect import connect_db

        assert connect_db() is None

    @patch("app.model.connect.create_engine")
    def test_retorna_none_when_execute_falha_34(self, mock_create_engine):
        """
        Falha no SELECT 1 de validação → retorna None.
        """
        engine = MagicMock(spec=Engine)
        conn_ctx = MagicMock()
        conn_ctx.__enter__ = MagicMock(return_value=conn_ctx)
        conn_ctx.__exit__ = MagicMock(return_value=False)
        conn_ctx.execute.side_effect = exc.OperationalError(
            "stmt", {}, Exception()
        )
        engine.connect.return_value = conn_ctx
        mock_create_engine.return_value = engine

        from app.model.connect import connect_db

        assert connect_db() is None


# Testes: test_connect()
class Test_Connection:
    """
    Testa a função orquestradora test_connect().
    """

    @patch("app.model.connect.connect_db")
    @patch("app.model.create_db.create_database")
    def test_retorna_true_when_banco_ok_e_connect_ok_35(
        self, mock_create_db, mock_connect_db
    ):
        """
        Fluxo completo sem falhas → True.
        """
        mock_create_db.return_value = True
        mock_connect_db.return_value = MagicMock(spec=Engine)

        from app.model.connect import test_connect

        assert test_connect() is True

    @patch("app.model.connect.connect_db")
    @patch("app.model.create_db.create_database")
    def test_create_database_e_chamado_antes_de_connect_db_36(
        self, mock_create_db, mock_connect_db
    ):
        """
        create_database deve ser chamado uma vez antes de connect_db.
        """
        mock_create_db.return_value = True
        mock_connect_db.return_value = MagicMock(spec=Engine)

        from app.model.connect import test_connect

        test_connect()

        mock_create_db.assert_called_once()

    @patch("app.model.connect.connect_db")
    @patch("app.model.create_db.create_database")
    def test_retorna_false_when_create_database_falha_37(
        self, mock_create_db, mock_connect_db
    ):
        """
        Se create_database retornar False, test_connect deve retornar False.
        """
        mock_create_db.return_value = False

        from app.model.connect import test_connect

        assert test_connect() is False

    @patch("app.model.connect.connect_db")
    @patch("app.model.create_db.create_database")
    def test_connect_db_nao_e_chamado_se_create_database_falha_38(
        self, mock_create_db, mock_connect_db
    ):
        """
        Se create_database falha, connect_db não deve ser chamado (fail-fast).
        """
        mock_create_db.return_value = False

        from app.model.connect import test_connect

        test_connect()

        mock_connect_db.assert_not_called()

    @patch("app.model.connect.connect_db")
    @patch("app.model.create_db.create_database")
    def test_retorna_false_when_connect_db_retorna_none_39(
        self, mock_create_db, mock_connect_db
    ):
        """
        Engine None de connect_db → test_connect retorna False.
        """
        mock_create_db.return_value = True
        mock_connect_db.return_value = None

        from app.model.connect import test_connect

        assert test_connect() is False
