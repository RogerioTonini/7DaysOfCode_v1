"""
tests/model/test_util_model.py
===============================
Testes unitários para  app/model/util_model.py

Cobertura:
┌──────────────────────┬────────────────────────────────────────────────────┐
│ Alvo                 │ Cenários                                           │
├──────────────────────┼────────────────────────────────────────────────────┤
│ create_table()       │ tipo uniforme (str) → True                         │
│                      │ tipos por dict       → True                        │
│                      │ auto_increment=True  → DDL com PK AUTO_INCREMENT   │
│                      │ auto_increment=False → sem coluna num_index        │
│                      │ commit chamado após execute                        │
│                      │ SQLAlchemyError → False                            │
│                      │ Exception genérica → False                         │
├──────────────────────┼────────────────────────────────────────────────────┤
│ check_table_exists() │ tabela existe  → True                              │
│                      │ tabela ausente → False                             │
│                      │ delega para sa_inspect().has_table()               │
├──────────────────────┼────────────────────────────────────────────────────┤
│ insert_data()        │ lote único → True, to_sql chamado 1×               │
│                      │ múltiplos lotes → True, contagem correta de calls  │
│                      │ total divisível pelo lote → lotes exatos           │
│                      │ último lote com sobra → ceil correto               │
│                      │ SQLAlchemyError → False                            │
│                      │ Exception genérica → False                         │
└──────────────────────┴────────────────────────────────────────────────────┘
"""

import math
from unittest.mock import MagicMock, call, patch

import pandas as pd
import pytest
from sqlalchemy import exc
from sqlalchemy.engine import Engine


# Helpers
def _engine_mock_ok() -> tuple[MagicMock, MagicMock]:
    """Engine e contexto de conexão com comportamento bem-sucedido."""
    engine = MagicMock(spec=Engine)
    conn_ctx = MagicMock()
    conn_ctx.__enter__ = MagicMock(return_value=conn_ctx)
    conn_ctx.__exit__ = MagicMock(return_value=False)
    engine.connect.return_value = conn_ctx
    return engine, conn_ctx


def _make_df(n_rows: int) -> pd.DataFrame:
    """DataFrame sintético com n_rows linhas."""
    return pd.DataFrame(
        {
            "col_a": [f"item_{i}" for i in range(n_rows)],
            "col_b": range(n_rows),
        }
    )


# Testes: create_table()


class Test_Create_Table:
    """
    Testa create_table(): geração de DDL e execução no banco.
    """

    # Caminho feliz
    def test_return_true_with_uniform_str_type_62(self):
        """
        Quando tipos_coluna é str, todas as colunas recebem o mesmo tipo.
        """
        engine, conn_ctx = _engine_mock_ok()
        colunas = ("titulo", "autor", "ano")

        from app.model.util_model import create_table

        resultado = create_table(engine, "tb_str", colunas, "VARCHAR(255)")

        assert resultado is True

    def test_return_true_with_dict_type_63(self):
        """
        Quando tipos_coluna é dict, cada coluna recebe seu tipo específico.
        """
        engine, conn_ctx = _engine_mock_ok()
        colunas = ("id", "descricao", "valor")
        tipos = {
            "id": "INT",
            "descricao": "VARCHAR(100)",
            "valor": "DECIMAL(10,2)",
        }

        from app.model.util_model import create_table

        resultado = create_table(engine, "tb_dict", colunas, tipos)

        assert resultado is True

    def test_execute_is_called_once_64(self):
        """
        Deve executar exatamente 1 statement DDL.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.util_model import create_table

        create_table(engine, "tb_exec", ("col",), "TEXT")

        conn_ctx.execute.assert_called_once()

    def test_commit_is_called_after_execute_65(self):
        """
        commit() deve ser chamado após o execute() do DDL.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.util_model import create_table

        create_table(engine, "tb_commit", ("col",), "TEXT")

        conn_ctx.commit.assert_called_once()

    # auto_increment

    def test_ddl_contains_auto_increment_when_enabled_66(self):
        """
        auto_increment=True → DDL deve incluir AUTO_INCREMENT PRIMARY KEY.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.util_model import create_table

        create_table(
            engine, "tb_ai", ("descricao",), "TEXT", auto_increment=True
        )

        ddl: str = str(conn_ctx.execute.call_args[0][0])
        assert "AUTO_INCREMENT" in ddl
        assert "PRIMARY KEY" in ddl

    def test_ddl_contains_num_index_when_auto_increment_67(self):
        """
        A coluna gerada pela PK deve se chamar num_index.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.util_model import create_table

        create_table(
            engine, "tb_num_idx", ("col",), "VARCHAR(50)", auto_increment=True
        )

        ddl: str = str(conn_ctx.execute.call_args[0][0])
        assert "num_index" in ddl

    def test_ddl_does_not_contain_auto_increment_when_disabled_68(self):
        """
        auto_increment=False (padrão) → sem coluna num_index no DDL.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.util_model import create_table

        create_table(
            engine, "tb_sem_ai", ("col",), "VARCHAR(50)", auto_increment=False
        )

        ddl: str = str(conn_ctx.execute.call_args[0][0])
        assert "num_index" not in ddl
        assert "AUTO_INCREMENT" not in ddl

    # Conteúdo do DDL

    def test_ddl_contains_table_name_69(self):
        """
        O nome da tabela deve aparecer no DDL gerado.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.util_model import create_table

        create_table(engine, "tb_minha_tabela", ("col",), "VARCHAR(50)")

        ddl: str = str(conn_ctx.execute.call_args[0][0])
        assert "tb_minha_tabela" in ddl

    def test_ddl_contains_charset_utf8mb4_70(self):
        """
        O DDL deve incluir CHARSET=utf8mb4 para suporte a Unicode.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.util_model import create_table

        create_table(engine, "tb_charset", ("col",), "TEXT")

        ddl: str = str(conn_ctx.execute.call_args[0][0])
        assert "utf8mb4" in ddl

    def test_ddl_contains_engine_innodb_71(self):
        """
        O DDL deve especificar ENGINE=InnoDB.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.util_model import create_table

        create_table(engine, "tb_innodb", ("col",), "TEXT")

        ddl: str = str(conn_ctx.execute.call_args[0][0])
        assert "InnoDB" in ddl

    def test_all_columns_present_in_ddl_72(self):
        """
        Cada coluna informada deve aparecer no DDL gerado.
        """
        engine, conn_ctx = _engine_mock_ok()
        colunas = ("nome", "cpf", "email", "telefone")

        from app.model.util_model import create_table

        create_table(engine, "tb_cols", colunas, "VARCHAR(255)")

        ddl: str = str(conn_ctx.execute.call_args[0][0])
        for col in colunas:
            assert col in ddl

    # Tratamento de erros

    def test_return_false_on_sqlalchemy_error_73(self):
        """
        SQLAlchemyError ao executar DDL → retorna False.
        """
        engine, conn_ctx = _engine_mock_ok()
        conn_ctx.execute.side_effect = exc.SQLAlchemyError("erro ddl")

        from app.model.util_model import create_table

        assert create_table(engine, "tb_erro", ("col",), "VARCHAR(50)") is False

    def test_return_false_on_generic_exception_74(self):
        """
        Exception inesperada → retorna False.
        """
        engine, conn_ctx = _engine_mock_ok()
        conn_ctx.execute.side_effect = Exception("falha inesperada")

        from app.model.util_model import create_table

        assert create_table(engine, "tb_erro_gen", ("col",), "TEXT") is False


# Testes: check_table_exists()


class Test_Check_Table_Exists:
    """
    Testa check_table_exists(): delegação ao sa_inspect().has_table().
    """

    def test_return_true_when_table_exists_75(self):
        engine = MagicMock(spec=Engine)
        with patch("app.model.util_model.sa_inspect") as mock_inspect:
            mock_inspect.return_value.has_table.return_value = True

            from app.model.util_model import check_table_exists

            assert check_table_exists(engine, "tb_existe") is True

    def test_return_false_when_table_does_not_exist_76(self):
        engine = MagicMock(spec=Engine)
        with patch("app.model.util_model.sa_inspect") as mock_inspect:
            mock_inspect.return_value.has_table.return_value = False

            from app.model.util_model import check_table_exists

            assert check_table_exists(engine, "tb_ausente") is False

    def test_delegates_to_sa_inspect_with_correct_engine_77(self):
        """
        sa_inspect deve ser chamado com o engine fornecido.
        """
        engine = MagicMock(spec=Engine)
        with patch("app.model.util_model.sa_inspect") as mock_inspect:
            mock_inspect.return_value.has_table.return_value = True

            from app.model.util_model import check_table_exists

            check_table_exists(engine, "tb_qualquer")

            mock_inspect.assert_called_once_with(engine)

    def test_has_table_receives_correct_name_78(self):
        """
        has_table() deve ser chamado com o nome exato da tabela.
        """
        engine = MagicMock(spec=Engine)
        with patch("app.model.util_model.sa_inspect") as mock_inspect:
            mock_inspect.return_value.has_table.return_value = False

            from app.model.util_model import check_table_exists

            check_table_exists(engine, "tb_nome_exato")

            mock_inspect.return_value.has_table.assert_called_once_with(
                "tb_nome_exato"
            )


# Testes: insert_data()


class Test_Insert_Data:
    """
    Testa insert_data(): inserção em lotes via to_sql.
    """

    # Caminho feliz – lote único

    @patch("app.model.util_model.cfg_app")
    def test_return_true_with_single_batch_79(self, mock_cfg):
        """
        Menos linhas que o tamanho do lote → 1 chamada to_sql → True.
        """
        mock_cfg.parametros.QTD_REG_LOTE = 1000
        engine = MagicMock(spec=Engine)
        df = _make_df(5)

        with patch("pandas.DataFrame.to_sql") as mock_to_sql:
            from app.model.util_model import insert_data

            resultado = insert_data(engine, df, "tb_unico")

        assert resultado is True
        mock_to_sql.assert_called_once()

    @patch("app.model.util_model.cfg_app")
    def test_to_sql_called_with_correct_parameters_80(self, mock_cfg):
        """
        to_sql deve receber nome da tabela, engine, if_exists='append' e index=False.
        """
        mock_cfg.parametros.QTD_REG_LOTE = 1000
        engine = MagicMock(spec=Engine)
        df = _make_df(3)

        with patch("pandas.DataFrame.to_sql") as mock_to_sql:
            from app.model.util_model import insert_data

            insert_data(engine, df, "tb_parametros")

        call_kwargs = mock_to_sql.call_args[1]
        assert call_kwargs["name"] == "tb_parametros"
        assert call_kwargs["con"] is engine
        assert call_kwargs["if_exists"] == "append"
        assert call_kwargs["index"] is False

    # Caminho feliz – múltiplos lotes

    @patch("app.model.util_model.cfg_app")
    def test_return_true_with_multiple_batches_81(self, mock_cfg):
        """
        7 linhas com lote=3 → ceil(7/3)=3 chamadas to_sql → True.
        """
        mock_cfg.parametros.QTD_REG_LOTE = 3
        engine = MagicMock(spec=Engine)
        df = _make_df(7)

        with patch("pandas.DataFrame.to_sql") as mock_to_sql:
            from app.model.util_model import insert_data

            resultado = insert_data(engine, df, "tb_multi")

        assert resultado is True
        assert mock_to_sql.call_count == 3

    @patch("app.model.util_model.cfg_app")
    def test_total_divisible_by_exact_lots_82(self, mock_cfg):
        """
        6 linhas com lote=3 → exatamente 2 lotes, sem sobra.
        """
        mock_cfg.parametros.QTD_REG_LOTE = 3
        engine = MagicMock(spec=Engine)
        df = _make_df(6)

        with patch("pandas.DataFrame.to_sql") as mock_to_sql:
            from app.model.util_model import insert_data

            insert_data(engine, df, "tb_exato")

        assert mock_to_sql.call_count == 2

    @patch("app.model.util_model.cfg_app")
    def test_number_of_batches_follows_ceil_formula_83(self, mock_cfg):
        """
        A fórmula ceil(total/lote) deve determinar o número de chamadas.
        """
        lote = 4
        total = 9  # ceil(9/4) = 3 lotes
        mock_cfg.parametros.QTD_REG_LOTE = lote
        engine = MagicMock(spec=Engine)
        df = _make_df(total)

        esperado = math.ceil(total / lote)

        with patch("pandas.DataFrame.to_sql") as mock_to_sql:
            from app.model.util_model import insert_data

            insert_data(engine, df, "tb_ceil")

        assert mock_to_sql.call_count == esperado

    @patch("app.model.util_model.cfg_app")
    def test_single_row_generates_one_batch_84(self, mock_cfg):
        """
        DataFrame de 1 linha → exatamente 1 chamada to_sql.
        """
        mock_cfg.parametros.QTD_REG_LOTE = 1000
        engine = MagicMock(spec=Engine)
        df = _make_df(1)

        with patch("pandas.DataFrame.to_sql") as mock_to_sql:
            from app.model.util_model import insert_data

            insert_data(engine, df, "tb_uma_linha")

        mock_to_sql.assert_called_once()

    # Tratamento de erros

    @patch("app.model.util_model.cfg_app")
    def test_return_false_on_sqlalchemy_error_85(self, mock_cfg):
        """
        SQLAlchemyError no to_sql → retorna False.
        """
        mock_cfg.parametros.QTD_REG_LOTE = 1000
        engine = MagicMock(spec=Engine)
        df = _make_df(5)

        with patch(
            "pandas.DataFrame.to_sql",
            side_effect=exc.SQLAlchemyError("erro insert"),
        ):
            from app.model.util_model import insert_data

            assert insert_data(engine, df, "tb_sql_err") is False

    @patch("app.model.util_model.cfg_app")
    def test_return_false_on_generic_exception_86(self, mock_cfg):
        """
        Exception inesperada no to_sql → retorna False.
        """
        mock_cfg.parametros.QTD_REG_LOTE = 1000
        engine = MagicMock(spec=Engine)
        df = _make_df(5)

        with patch(
            "pandas.DataFrame.to_sql", side_effect=Exception("falha geral")
        ):
            from app.model.util_model import insert_data

            assert insert_data(engine, df, "tb_exc") is False

    @patch("app.model.util_model.cfg_app")
    def test_error_in_second_batch_returns_false_87(self, mock_cfg):
        """
        Falha no segundo lote (após sucesso no primeiro) → retorna False.
        """
        mock_cfg.parametros.QTD_REG_LOTE = 3
        engine = MagicMock(spec=Engine)
        df = _make_df(6)  # 2 lotes de 3

        chamadas = 0

        def to_sql_falha_no_segundo(*args, **kwargs):
            nonlocal chamadas
            chamadas += 1
            if chamadas == 2:
                raise exc.SQLAlchemyError("falha no 2º lote")

        with patch(
            "pandas.DataFrame.to_sql", side_effect=to_sql_falha_no_segundo
        ):
            from app.model.util_model import insert_data

            assert insert_data(engine, df, "tb_lote2_err") is False
