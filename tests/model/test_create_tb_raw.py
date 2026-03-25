"""
tests/model/test_create_tb_raw.py
===================================
Testes unitários para app/model/emprestimos/create_tb_raw.py

Cobertura:
+----------------------+---------------------------------------------------+
| Alvo                 | Cenários                                          |
+----------------------+---------------------------------------------------+
| get_table_columns()  | retorna lista de nomes de colunas do banco        |
|                      | ignora outros atributos do dict de coluna         |
|                      | lista vazia quando tabela sem colunas             |
+----------------------+---------------------------------------------------+
| check_columns()      | listas iguais -> True                             |
|                      | listas diferentes -> False                        |
|                      | ordem importa -> lista invertida -> False         |
|                      | tamanhos diferentes -> False                      |
+----------------------+---------------------------------------------------+
| create_table_raw()   | execute chamado uma vez                           |
|                      | commit chamado apos execute                       |
|                      | DDL contem nome da tabela                         |
|                      | DDL contem VARCHAR(255)                           |
|                      | DDL contem utf8mb4                                |
|                      | DDL contem InnoDB                                 |
|                      | DDL contem todas as colunas do esquema RAW        |
+----------------------+---------------------------------------------------+
| prepare_table_raw()  | connect_db None -> False                          |
|                      | tabela inexistente -> create chamado -> True      |
|                      | tabela existe, colunas iguais -> TRUNCATE -> True |
|                      | tabela existe, colunas dif. -> RENAME+CREATE->True|
|                      | SQLAlchemyError -> False                          |
|                      | Exception genérica -> False                       |
|                      | engine.dispose chamado no finally                 |
+----------------------+---------------------------------------------------+
| check_table_raw()    | prepare_table_raw falha -> False                  |
|                      | connect_db None apos prepare -> False             |
|                      | insert_data falha -> False                        |
|                      | fluxo completo bem-sucedido -> True               |
|                      | engine.dispose chamado apos insercao com sucesso  |
|                      | engine.dispose chamado mesmo com falha na insercao|
+----------------------+---------------------------------------------------+

Estrategia de mock:
    - connect_db e patched em app.model.emprestimos.create_tb_raw para
    controlar o engine sem abrir conexão real.
    - check_table_exists e patched para simular presença/ausência da tabela.
    - insert_data e patched para isolar a lógica de inserção dos testes de
    orquestração.
    - sa_inspect e patched para retornar colunas sintéticas.
"""

from unittest.mock import MagicMock, call, patch

import pandas as pd
import pytest
from sqlalchemy import exc
from sqlalchemy.engine import Engine

# Helpers


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


def _df_emprestimos() -> pd.DataFrame:
    """
    DataFrame sintético com colunas do esquema RAW de empréstimos.
    """
    return pd.DataFrame(
        {
            "id_emprestimo": ["E001", "E002"],
            "codigo_barras": ["123", "456"],
            "data_renovacao": ["2021-01-01", "2021-01-02"],
            "data_emprestimo": ["2021-01-01", "2021-01-02"],
            "data_devolucao": ["2021-01-15", "2021-01-16"],
            "matricula_ou_siape": ["123456", "654321"],
            "tipo_vinculo_usuario": ["ALUNO", "SERVIDOR"],
        }
    )


# Testes: get_table_columns()


class Test_Get_Table_Columns:
    """
    Testa get_table_columns(): listagem de colunas via sa_inspect.
    """

    def test_returns_list_of_column_names_119(self):
        """
        Deve retornar apenas os nomes das colunas, sem outros atributos.
        """
        engine = MagicMock(spec=Engine)

        with patch(
            "app.model.emprestimos.create_tb_raw.sa_inspect"
        ) as mock_inspect:
            mock_inspect.return_value.get_columns.return_value = [
                {"name": "col_a", "type": "VARCHAR"},
                {"name": "col_b", "type": "INT"},
            ]

            from app.model.emprestimos.create_tb_raw import get_table_columns

            resultado = get_table_columns(engine, "tb_teste")

        assert resultado == ["col_a", "col_b"]

    def test_sa_inspect_called_with_engine_120(self):
        """
        sa_inspect deve ser chamado com o engine fornecido.
        """
        engine = MagicMock(spec=Engine)

        with patch(
            "app.model.emprestimos.create_tb_raw.sa_inspect"
        ) as mock_inspect:
            mock_inspect.return_value.get_columns.return_value = []

            from app.model.emprestimos.create_tb_raw import get_table_columns

            get_table_columns(engine, "tb_qualquer")

        mock_inspect.assert_called_once_with(engine)

    def test_returns_empty_list_when_no_columns_121(self):
        """
        Tabela sem colunas -> lista vazia retornada sem exceção.
        """
        engine = MagicMock(spec=Engine)

        with patch(
            "app.model.emprestimos.create_tb_raw.sa_inspect"
        ) as mock_inspect:
            mock_inspect.return_value.get_columns.return_value = []

            from app.model.emprestimos.create_tb_raw import get_table_columns

            resultado = get_table_columns(engine, "tb_vazia")

        assert resultado == []


# Testes: check_columns()


class Test_Check_Columns:
    """
    Testa check_columns(): comparação entre colunas do banco e
    esquema definido.
    """

    def test_returns_true_when_columns_match_122(self):
        """
        Listas idênticas (mesma ordem) -> True.
        """
        from app.model.emprestimos.create_tb_raw import check_columns

        colunas = ["col_a", "col_b", "col_c"]
        assert check_columns(colunas, tuple(colunas)) is True

    def test_returns_false_when_columns_differ_123(self):
        """
        Listas com nomes distintos -> False.
        """
        from app.model.emprestimos.create_tb_raw import check_columns

        assert (
            check_columns(
                ["col_a", "col_b"],
                ("col_x", "col_y"),
            )
            is False
        )

    def test_returns_false_when_order_differs_124(self):
        """
        Mesmas colunas em ordem diferente -> False (ordem importa).
        """
        from app.model.emprestimos.create_tb_raw import check_columns

        assert (
            check_columns(
                ["col_b", "col_a"],
                ("col_a", "col_b"),
            )
            is False
        )

    def test_returns_false_when_lengths_differ_125(self):
        """
        Listas com tamanhos diferentes -> False.
        """
        from app.model.emprestimos.create_tb_raw import check_columns

        assert (
            check_columns(
                ["col_a"],
                ("col_a", "col_b"),
            )
            is False
        )


# Testes: create_table_raw()


class Test_Create_Table_Raw:
    """
    Testa create_table_raw(): criação da tabela RAW com colunas VARCHAR(255).
    """

    def test_execute_called_once_126(self):
        """
        Deve executar exatamente 1 statement DDL.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.emprestimos.create_tb_raw import create_table_raw

        create_table_raw(engine, "tb_emprestimos_raw")

        conn_ctx.execute.assert_called_once()

    def test_commit_called_after_execute_127(self):
        """
        commit() deve ser chamado apos o execute() do DDL.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.emprestimos.create_tb_raw import create_table_raw

        create_table_raw(engine, "tb_emprestimos_raw")

        conn_ctx.commit.assert_called_once()

    def test_ddl_contains_table_name_128(self):
        """
        O nome informado deve constar no DDL gerado.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.emprestimos.create_tb_raw import create_table_raw

        create_table_raw(engine, "tb_nome_customizado")

        ddl: str = str(conn_ctx.execute.call_args[0][0])
        assert "tb_nome_customizado" in ddl

    def test_ddl_contains_varchar255_type_129(self):
        """
        Todas as colunas RAW devem ser do tipo VARCHAR(255).
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.emprestimos.create_tb_raw import create_table_raw

        create_table_raw(engine, "tb_raw")

        ddl: str = str(conn_ctx.execute.call_args[0][0])
        assert "VARCHAR(255)" in ddl

    def test_ddl_contains_utf8mb4_charset_130(self):
        """
        DDL deve incluir utf8mb4 para suporte Unicode.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.emprestimos.create_tb_raw import create_table_raw

        create_table_raw(engine, "tb_raw")

        ddl: str = str(conn_ctx.execute.call_args[0][0])
        assert "utf8mb4" in ddl

    def test_ddl_contains_innodb_engine_131(self):
        """
        DDL deve especificar ENGINE=InnoDB.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.emprestimos.create_tb_raw import create_table_raw

        create_table_raw(engine, "tb_raw")

        ddl: str = str(conn_ctx.execute.call_args[0][0])
        assert "InnoDB" in ddl

    def test_ddl_contains_all_schema_columns_132(self):
        """
        Cada coluna do esquema RAW deve aparecer no DDL.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.emprestimos.config_emprestimos import cfg_emprestimos
        from app.model.emprestimos.create_tb_raw import create_table_raw

        create_table_raw(engine, "tb_raw")

        ddl: str = str(conn_ctx.execute.call_args[0][0])
        for col in cfg_emprestimos.esquema_raw.COLUNAS:
            assert col in ddl, f"Coluna '{col}' ausente no DDL"


# Testes: prepare_table_raw()


class Test_Prepare_Table_Raw:
    """
    Testa prepare_table_raw(): verificação e preparação da tabela RAW.
    """

    @patch("app.model.emprestimos.create_tb_raw.connect_db")
    def test_returns_false_when_connect_db_returns_none_133(
        self, mock_connect_db
    ):
        """
        connect_db retorna None -> prepare_table_raw retorna False.
        """
        mock_connect_db.return_value = None

        from app.model.emprestimos.create_tb_raw import prepare_table_raw

        assert prepare_table_raw(_df_emprestimos()) is False

    @patch("app.model.emprestimos.create_tb_raw.create_table_raw")
    @patch("app.model.emprestimos.create_tb_raw.check_table_exists")
    @patch("app.model.emprestimos.create_tb_raw.connect_db")
    def test_creates_table_when_not_exists_and_returns_true_134(
        self, mock_connect_db, mock_check_exists, mock_create_raw
    ):
        """
        Tabela nao existe -> create_table_raw chamado -> retorna True.
        """
        engine, _ = _engine_mock_ok()
        mock_connect_db.return_value = engine
        mock_check_exists.return_value = False

        from app.model.emprestimos.create_tb_raw import prepare_table_raw

        resultado = prepare_table_raw(_df_emprestimos())

        assert resultado is True
        mock_create_raw.assert_called_once()

    @patch("app.model.emprestimos.create_tb_raw.check_columns")
    @patch("app.model.emprestimos.create_tb_raw.get_table_columns")
    @patch("app.model.emprestimos.create_tb_raw.check_table_exists")
    @patch("app.model.emprestimos.create_tb_raw.connect_db")
    def test_truncates_when_columns_match_135(
        self,
        mock_connect_db,
        mock_check_exists,
        mock_get_cols,
        mock_check_cols,
    ):
        """
        Tabela existe e colunas iguais -> TRUNCATE executado -> retorna True.
        """
        engine, conn_ctx = _engine_mock_ok()
        mock_connect_db.return_value = engine
        mock_check_exists.return_value = True
        mock_get_cols.return_value = ["col_a"]
        mock_check_cols.return_value = True

        from app.model.emprestimos.create_tb_raw import prepare_table_raw

        resultado = prepare_table_raw(_df_emprestimos())

        assert resultado is True
        sqls = [
            str(c.args[0]).upper()
            for c in conn_ctx.execute.call_args_list
            if c.args
        ]
        assert any("TRUNCATE" in sql for sql in sqls)

    @patch("app.model.emprestimos.create_tb_raw.create_table_raw")
    @patch("app.model.emprestimos.create_tb_raw.check_columns")
    @patch("app.model.emprestimos.create_tb_raw.get_table_columns")
    @patch("app.model.emprestimos.create_tb_raw.check_table_exists")
    @patch("app.model.emprestimos.create_tb_raw.connect_db")
    def test_renames_and_recreates_when_columns_differ_136(
        self,
        mock_connect_db,
        mock_check_exists,
        mock_get_cols,
        mock_check_cols,
        mock_create_raw,
    ):
        """
        Tabela existe com colunas divergentes -> RENAME executado e nova
        tabela criada -> retorna True.
        """
        engine, conn_ctx = _engine_mock_ok()
        mock_connect_db.return_value = engine
        mock_check_exists.return_value = True
        mock_get_cols.return_value = ["col_errada"]
        mock_check_cols.return_value = False

        from app.model.emprestimos.create_tb_raw import prepare_table_raw

        resultado = prepare_table_raw(_df_emprestimos())

        assert resultado is True
        sqls = [
            str(c.args[0]).upper()
            for c in conn_ctx.execute.call_args_list
            if c.args
        ]
        assert any("RENAME" in sql for sql in sqls)
        mock_create_raw.assert_called_once()

    @patch("app.model.emprestimos.create_tb_raw.check_table_exists")
    @patch("app.model.emprestimos.create_tb_raw.connect_db")
    def test_returns_false_on_sqlalchemy_error_137(
        self, mock_connect_db, mock_check_exists
    ):
        """
        SQLAlchemyError durante operação -> retorna False.
        """
        engine, _ = _engine_mock_ok()
        mock_connect_db.return_value = engine
        mock_check_exists.side_effect = exc.SQLAlchemyError("erro prepare")

        from app.model.emprestimos.create_tb_raw import prepare_table_raw

        assert prepare_table_raw(_df_emprestimos()) is False

    @patch("app.model.emprestimos.create_tb_raw.check_table_exists")
    @patch("app.model.emprestimos.create_tb_raw.connect_db")
    def test_returns_false_on_generic_exception_138(
        self, mock_connect_db, mock_check_exists
    ):
        """
        Exception genérica -> retorna False.
        """
        engine, _ = _engine_mock_ok()
        mock_connect_db.return_value = engine
        mock_check_exists.side_effect = Exception("falha inesperada")

        from app.model.emprestimos.create_tb_raw import prepare_table_raw

        assert prepare_table_raw(_df_emprestimos()) is False

    @patch("app.model.emprestimos.create_tb_raw.check_table_exists")
    @patch("app.model.emprestimos.create_tb_raw.connect_db")
    def test_engine_dispose_called_in_finally_on_success_139(
        self, mock_connect_db, mock_check_exists
    ):
        """
        engine.dispose() deve ser chamado no finally em caso de sucesso.
        """
        engine, _ = _engine_mock_ok()
        mock_connect_db.return_value = engine
        mock_check_exists.return_value = False

        with patch("app.model.emprestimos.create_tb_raw.create_table_raw"):
            from app.model.emprestimos.create_tb_raw import prepare_table_raw

            prepare_table_raw(_df_emprestimos())

        engine.dispose.assert_called_once()

    @patch("app.model.emprestimos.create_tb_raw.check_table_exists")
    @patch("app.model.emprestimos.create_tb_raw.connect_db")
    def test_engine_dispose_called_in_finally_on_error_140(
        self, mock_connect_db, mock_check_exists
    ):
        """
        engine.dispose() deve ser chamado no finally mesmo quando ha exceção.
        """
        engine, _ = _engine_mock_ok()
        mock_connect_db.return_value = engine
        mock_check_exists.side_effect = exc.SQLAlchemyError("erro")

        from app.model.emprestimos.create_tb_raw import prepare_table_raw

        prepare_table_raw(_df_emprestimos())

        engine.dispose.assert_called_once()

    @patch("app.model.emprestimos.create_tb_raw.create_table_raw")
    @patch("app.model.emprestimos.create_tb_raw.check_columns")
    @patch("app.model.emprestimos.create_tb_raw.get_table_columns")
    @patch("app.model.emprestimos.create_tb_raw.check_table_exists")
    @patch("app.model.emprestimos.create_tb_raw.connect_db")
    def test_backup_name_contains_raw_prefix_when_columns_differ_141(
        self,
        mock_connect_db,
        mock_check_exists,
        mock_get_cols,
        mock_check_cols,
        mock_create_raw,
    ):
        """
        Nome do backup deve iniciar com RAW_BKP_PREFIX quando colunas divergem.
        """
        engine, conn_ctx = _engine_mock_ok()
        mock_connect_db.return_value = engine
        mock_check_exists.return_value = True
        mock_get_cols.return_value = ["col_errada"]
        mock_check_cols.return_value = False

        from app.model.emprestimos.config_emprestimos import cfg_emprestimos
        from app.model.emprestimos.create_tb_raw import prepare_table_raw

        prepare_table_raw(_df_emprestimos())

        sqls = [
            str(c.args[0])
            for c in conn_ctx.execute.call_args_list
            if c.args and "RENAME" in str(c.args[0]).upper()
        ]

        assert len(sqls) > 0
        assert cfg_emprestimos.tabelas.RAW_BKP_PREFIX in sqls[0]


# Testes: check_table_raw()


class Test_Check_Table_Raw:
    """
    Testa check_table_raw(): orquestrador de preparação e inserção
    na tabela RAW.
    """

    @patch("app.model.emprestimos.create_tb_raw.prepare_table_raw")
    def test_returns_false_when_prepare_table_raw_fails_142(self, mock_prepare):
        """
        prepare_table_raw retorna False -> check_table_raw retorna False.
        """
        mock_prepare.return_value = False

        from app.model.emprestimos.create_tb_raw import check_table_raw

        assert check_table_raw(_df_emprestimos()) is False

    @patch("app.model.emprestimos.create_tb_raw.connect_db")
    @patch("app.model.emprestimos.create_tb_raw.prepare_table_raw")
    def test_returns_false_when_connect_db_returns_none_after_prepare_143(
        self, mock_prepare, mock_connect_db
    ):
        """
        prepare_table_raw bem-sucedido mas connect_db retorna None -> False.
        """
        mock_prepare.return_value = True
        mock_connect_db.return_value = None

        from app.model.emprestimos.create_tb_raw import check_table_raw

        assert check_table_raw(_df_emprestimos()) is False

    @patch("app.model.emprestimos.create_tb_raw.insert_data")
    @patch("app.model.emprestimos.create_tb_raw.connect_db")
    @patch("app.model.emprestimos.create_tb_raw.prepare_table_raw")
    def test_returns_false_when_insert_data_fails_144(
        self, mock_prepare, mock_connect_db, mock_insert
    ):
        """
        insert_data retorna False -> check_table_raw retorna False.
        """
        engine, _ = _engine_mock_ok()
        mock_prepare.return_value = True
        mock_connect_db.return_value = engine
        mock_insert.return_value = False

        from app.model.emprestimos.create_tb_raw import check_table_raw

        assert check_table_raw(_df_emprestimos()) is False

    @patch("app.model.emprestimos.create_tb_raw.insert_data")
    @patch("app.model.emprestimos.create_tb_raw.connect_db")
    @patch("app.model.emprestimos.create_tb_raw.prepare_table_raw")
    def test_returns_true_on_complete_success_145(
        self, mock_prepare, mock_connect_db, mock_insert
    ):
        """
        prepare_table_raw e insert_data bem-sucedidos -> retorna True.
        """
        engine, _ = _engine_mock_ok()
        mock_prepare.return_value = True
        mock_connect_db.return_value = engine
        mock_insert.return_value = True

        from app.model.emprestimos.create_tb_raw import check_table_raw

        assert check_table_raw(_df_emprestimos()) is True

    @patch("app.model.emprestimos.create_tb_raw.insert_data")
    @patch("app.model.emprestimos.create_tb_raw.connect_db")
    @patch("app.model.emprestimos.create_tb_raw.prepare_table_raw")
    def test_engine_dispose_called_after_success_146(
        self, mock_prepare, mock_connect_db, mock_insert
    ):
        """
        engine.dispose() deve ser chamado apos inserção bem-sucedida.
        """
        engine, _ = _engine_mock_ok()
        mock_prepare.return_value = True
        mock_connect_db.return_value = engine
        mock_insert.return_value = True

        from app.model.emprestimos.create_tb_raw import check_table_raw

        check_table_raw(_df_emprestimos())

        engine.dispose.assert_called_once()

    @patch("app.model.emprestimos.create_tb_raw.insert_data")
    @patch("app.model.emprestimos.create_tb_raw.connect_db")
    @patch("app.model.emprestimos.create_tb_raw.prepare_table_raw")
    def test_engine_dispose_called_after_insert_failure_147(
        self, mock_prepare, mock_connect_db, mock_insert
    ):
        """
        engine.dispose() deve ser chamado mesmo quando insert_data falha.
        """
        engine, _ = _engine_mock_ok()
        mock_prepare.return_value = True
        mock_connect_db.return_value = engine
        mock_insert.return_value = False

        from app.model.emprestimos.create_tb_raw import check_table_raw

        check_table_raw(_df_emprestimos())

        engine.dispose.assert_called_once()

    @patch("app.model.emprestimos.create_tb_raw.insert_data")
    @patch("app.model.emprestimos.create_tb_raw.connect_db")
    @patch("app.model.emprestimos.create_tb_raw.prepare_table_raw")
    def test_insert_data_called_with_correct_table_name_148(
        self, mock_prepare, mock_connect_db, mock_insert
    ):
        """
        insert_data deve ser chamado com o nome da tabela RAW do config.
        """
        engine, _ = _engine_mock_ok()
        mock_prepare.return_value = True
        mock_connect_db.return_value = engine
        mock_insert.return_value = True

        from app.model.emprestimos.config_emprestimos import cfg_emprestimos
        from app.model.emprestimos.create_tb_raw import check_table_raw

        df = _df_emprestimos()
        check_table_raw(df)

        call_args = mock_insert.call_args
        assert call_args[0][2] == cfg_emprestimos.tabelas.RAW
