"""
tests/model/test_create_tb_cdu.py
==================================
Testes unitários para app/model/cdu/create_tb_cdu.py

Cobertura:
+-----------------------+--------------------------------------------------+
| Alvo                  | Cenários                                         |
+-----------------------+--------------------------------------------------+
| read_csv()            | arquivo não encontrado -> None                   |
|                       | colunas ausentes no CSV -> None                  |
|                       | leitura bem-sucedida -> DataFrame                |
|                       | DataFrame filtrado com colunas do esquema        |
|                       | exceção genérica -> None                         |
+-----------------------+--------------------------------------------------+
| check_schema_match()  | colunas iguais ao esquema -> True                |
|                       | colunas diferentes -> False                      |
|                       | coluna num_index ignorada na comparação          |
|                       | ordem diferente das colunas -> False             |
+-----------------------+--------------------------------------------------+
| create_table()        | execute chamado uma vez                          |
|                       | commit chamado apos execute                      |
|                       | DDL contem AUTO_INCREMENT PRIMARY KEY            |
|                       | DDL contem coluna num_index                      |
|                       | DDL contem nome da tabela                        |
|                       | DDL contem utf8mb4                               |
|                       | DDL contem todas as colunas do esquema           |
+-----------------------+--------------------------------------------------+
| rename_to_backup()    | retorna string com nome do backup                |
|                       | nome inicia com BKP_PREFIX                       |
|                       | RENAME TABLE executado com nome original         |
|                       | commit chamado apos o rename                     |
+-----------------------+--------------------------------------------------+
| _upsert()             | retorna True no fluxo completo sem erros         |
|                       | INSERT executado quando chave não existe         |
|                       | UPDATE executado quando chave existe e nome dif. |
|                       | nenhum DML quando chave existe e nome igual      |
|                       | commit chamado ao final                          |
|                       | retorna False em SQLAlchemyError                 |
|                       | retorna False em Exception genérica              |
|                       | processa todos os registros do DataFrame         |
+-----------------------+--------------------------------------------------+

Estratégia de mock:
    - Path e patched no modulo cdu.create_tb_cdu para controlar exists().
    - pd.read_csv e patched para retornar DataFrames sintéticos.
    - Engine e substituído por MagicMock com context manager configurado.
    - sa_inspect e patched para simular inspeção de colunas sem banco real.
"""

from unittest.mock import MagicMock, call, patch

import pandas as pd
import pytest
from sqlalchemy import exc
from sqlalchemy.engine import Engine

# Helpers


def _engine_mock_ok() -> tuple[MagicMock, MagicMock]:
    """
    Retorna (engine, conn_ctx) com comportamento de conexao bem-sucedida.
    """
    engine = MagicMock(spec=Engine)
    conn_ctx = MagicMock()
    conn_ctx.__enter__ = MagicMock(return_value=conn_ctx)
    conn_ctx.__exit__ = MagicMock(return_value=False)
    engine.connect.return_value = conn_ctx
    return engine, conn_ctx


def _df_cdu_valid() -> pd.DataFrame:
    """
    DataFrame sintético compatível com o esquema CDU.
    Colunas: id_faixa_cdu, inicio_faixa, fim_faixa, nome_faixa_cdu
    """
    return pd.DataFrame(
        {
            "id_faixa_cdu": [1, 2, 3],
            "inicio_faixa": [0, 100, 200],
            "fim_faixa": [99, 199, 299],
            "nome_faixa_cdu": ["Generalidades", "Filosofia", "Religiao"],
        }
    )


# Testes: read_csv()


class Test_Read_CSV:
    """
    Testa read_csv(): leitura e validação do arquivo tb_CDU.csv.
    """

    def test_returns_none_when_file_not_found_88(self):
        """
        Arquivo inexistente no PATH_DATA -> retorna None sem exceção.
        """
        with patch("app.model.cdu.create_tb_cdu.Path") as MockPath:
            mock_file = MagicMock()
            mock_file.exists.return_value = False
            MockPath.return_value.__truediv__.return_value = mock_file

            from app.model.cdu.create_tb_cdu import read_csv

            assert read_csv() is None

    def test_returns_none_when_columns_missing_in_csv_89(self):
        """
        CSV com colunas ausentes em relacao ao esquema -> retorna None.
        """
        df_incompleto = pd.DataFrame(
            {
                "id_faixa_cdu": [1],
                "inicio_faixa": [0],
                # fim_faixa e nome_faixa_cdu ausentes
            }
        )

        with patch("app.model.cdu.create_tb_cdu.Path") as MockPath:
            mock_file = MagicMock()
            mock_file.exists.return_value = True
            MockPath.return_value.__truediv__.return_value = mock_file

            with patch("app.model.cdu.create_tb_cdu.pd.read_csv") as mock_read:
                mock_read.return_value = df_incompleto

                from app.model.cdu.create_tb_cdu import read_csv

                assert read_csv() is None

    def test_returns_dataframe_on_success_90(self):
        """
        Arquivo valido com todas as colunas -> retorna DataFrame nao vazio.
        """
        with patch("app.model.cdu.create_tb_cdu.Path") as MockPath:
            mock_file = MagicMock()
            mock_file.exists.return_value = True
            MockPath.return_value.__truediv__.return_value = mock_file

            with patch("app.model.cdu.create_tb_cdu.pd.read_csv") as mock_read:
                mock_read.return_value = _df_cdu_valid()

                from app.model.cdu.create_tb_cdu import read_csv

                resultado = read_csv()

        assert resultado is not None
        assert isinstance(resultado, pd.DataFrame)
        assert len(resultado) == 3

    def test_dataframe_contains_only_schema_columns_91(self):
        """
        O DataFrame retornado deve conter apenas as colunas definidas no esquema.
        """
        df_extra = _df_cdu_valid().copy()
        df_extra["coluna_extra"] = "valor"

        with patch("app.model.cdu.create_tb_cdu.Path") as MockPath:
            mock_file = MagicMock()
            mock_file.exists.return_value = True
            MockPath.return_value.__truediv__.return_value = mock_file

            with patch("app.model.cdu.create_tb_cdu.pd.read_csv") as mock_read:
                mock_read.return_value = df_extra

                from app.model.cdu.create_tb_cdu import read_csv

                resultado = read_csv()

        from app.model.cdu.config_cdu import cfg_cdu

        assert list(resultado.columns) == list(cfg_cdu.esquema.COLUNAS)

    def test_returns_none_on_generic_exception_92(self):
        """
        Exceção genérica durante pd.read_csv -> retorna None.
        """
        with patch("app.model.cdu.create_tb_cdu.Path") as MockPath:
            mock_file = MagicMock()
            mock_file.exists.return_value = True
            MockPath.return_value.__truediv__.return_value = mock_file

            with patch(
                "app.model.cdu.create_tb_cdu.pd.read_csv",
                side_effect=Exception("erro de leitura"),
            ):
                from app.model.cdu.create_tb_cdu import read_csv

                assert read_csv() is None

    def test_read_csv_uses_separator_from_config_93(self):
        """
        pd.read_csv deve ser chamado com sep proveniente de cfg_app.arquivo.SEP_CSV.
        """
        from app.config_app import cfg_app

        with patch("app.model.cdu.create_tb_cdu.Path") as MockPath:
            mock_file = MagicMock()
            mock_file.exists.return_value = True
            MockPath.return_value.__truediv__.return_value = mock_file

            with patch("app.model.cdu.create_tb_cdu.pd.read_csv") as mock_read:
                mock_read.return_value = _df_cdu_valid()

                from app.model.cdu.create_tb_cdu import read_csv

                read_csv()

        call_kwargs = mock_read.call_args[1]
        assert call_kwargs["sep"] == cfg_app.arquivo.SEP_CSV


# Testes: check_schema_match()


class Test_Check_Schema_Match:
    """
    Testa check_schema_match(): comparação entre colunas do banco e esquema.
    """

    def _mock_inspect_columns(self, engine: MagicMock, cols: list[str]):
        """
        Configura sa_inspect para retornar colunas especificadas.
        """
        from app.model.cdu.config_cdu import cfg_cdu

        col_dicts = [{"name": c} for c in cols]

        with patch("app.model.cdu.create_tb_cdu.sa_inspect") as mock_inspect:
            mock_inspect.return_value.get_columns.return_value = col_dicts
            yield mock_inspect

    def test_returns_true_when_columns_match_schema_94(self):
        """
        Colunas do banco idênticas ao esquema (sem num_index) -> True.
        """
        from app.model.cdu.config_cdu import cfg_cdu

        engine = MagicMock(spec=Engine)
        cols = list(cfg_cdu.esquema.COLUNAS)

        with patch("app.model.cdu.create_tb_cdu.sa_inspect") as mock_inspect:
            mock_inspect.return_value.get_columns.return_value = [
                {"name": c} for c in cols
            ]

            from app.model.cdu.create_tb_cdu import check_schema_match

            assert check_schema_match(engine) is True

    def test_returns_false_when_columns_differ_95(self):
        """
        Colunas do banco diferentes do esquema -> False.
        """
        engine = MagicMock(spec=Engine)
        cols_erradas = ["coluna_a", "coluna_b", "coluna_c", "coluna_d"]

        with patch("app.model.cdu.create_tb_cdu.sa_inspect") as mock_inspect:
            mock_inspect.return_value.get_columns.return_value = [
                {"name": c} for c in cols_erradas
            ]

            from app.model.cdu.create_tb_cdu import check_schema_match

            assert check_schema_match(engine) is False

    def test_num_index_is_ignored_in_comparison_96(self):
        """
        Coluna num_index deve ser excluída da comparação com o esquema.
        """
        from app.model.cdu.config_cdu import cfg_cdu

        engine = MagicMock(spec=Engine)
        cols_com_pk = ["num_index"] + list(cfg_cdu.esquema.COLUNAS)

        with patch("app.model.cdu.create_tb_cdu.sa_inspect") as mock_inspect:
            mock_inspect.return_value.get_columns.return_value = [
                {"name": c} for c in cols_com_pk
            ]

            from app.model.cdu.create_tb_cdu import check_schema_match

            assert check_schema_match(engine) is True

    def test_returns_false_when_column_order_differs_97(self):
        """
        Mesmas colunas em ordem diferente do esquema -> False.
        """
        from app.model.cdu.config_cdu import cfg_cdu

        engine = MagicMock(spec=Engine)
        cols_invertidas = list(reversed(cfg_cdu.esquema.COLUNAS))

        with patch("app.model.cdu.create_tb_cdu.sa_inspect") as mock_inspect:
            mock_inspect.return_value.get_columns.return_value = [
                {"name": c} for c in cols_invertidas
            ]

            from app.model.cdu.create_tb_cdu import check_schema_match

            assert check_schema_match(engine) is False


# Testes: create_table() CDU


class Test_Create_Table_CDU:
    """
    Testa create_table(): criação da tabela tb_CDU com AUTO_INCREMENT.
    """

    def test_execute_called_once_98(self):
        """
        Deve executar exatamente 1 statement DDL.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.cdu.create_tb_cdu import create_table

        create_table(engine)

        conn_ctx.execute.assert_called_once()

    def test_commit_called_after_execute_99(self):
        """
        commit() deve ser chamado apos o execute() do DDL.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.cdu.create_tb_cdu import create_table

        create_table(engine)

        conn_ctx.commit.assert_called_once()

    def test_ddl_contains_auto_increment_primary_key_100(self):
        """
        DDL deve incluir AUTO_INCREMENT PRIMARY KEY para a chave numérica.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.cdu.create_tb_cdu import create_table

        create_table(engine)

        ddl: str = str(conn_ctx.execute.call_args[0][0])
        assert "AUTO_INCREMENT" in ddl
        assert "PRIMARY KEY" in ddl

    def test_ddl_contains_num_index_column_101(self):
        """
        A coluna de chave primaria deve se chamar num_index.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.cdu.create_tb_cdu import create_table

        create_table(engine)

        ddl: str = str(conn_ctx.execute.call_args[0][0])
        assert "num_index" in ddl

    def test_ddl_contains_table_name_102(self):
        """
        O nome configurado em cfg_cdu.tabela.TABELA deve constar no DDL.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.cdu.config_cdu import cfg_cdu
        from app.model.cdu.create_tb_cdu import create_table

        create_table(engine)

        ddl: str = str(conn_ctx.execute.call_args[0][0])
        assert cfg_cdu.tabela.TABELA in ddl

    def test_ddl_contains_utf8mb4_charset_103(self):
        """
        DDL deve incluir utf8mb4 para suporte a Unicode completo.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.cdu.create_tb_cdu import create_table

        create_table(engine)

        ddl: str = str(conn_ctx.execute.call_args[0][0])
        assert "utf8mb4" in ddl

    def test_ddl_contains_all_schema_columns_104(self):
        """
        Cada coluna definida no esquema deve aparecer no DDL.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.cdu.config_cdu import cfg_cdu
        from app.model.cdu.create_tb_cdu import create_table

        create_table(engine)

        ddl: str = str(conn_ctx.execute.call_args[0][0])
        for col in cfg_cdu.esquema.COLUNAS:
            assert col in ddl, f"Coluna '{col}' ausente no DDL"


# Testes: rename_to_backup()


class Test_Rename_To_Backup:
    """
    Testa rename_to_backup(): renomeação de tb_CDU para nome com timestamp.
    """

    def test_returns_backup_name_string_105(self):
        """
        Retorna uma string com o nome completo do backup.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.cdu.create_tb_cdu import rename_to_backup

        resultado = rename_to_backup(engine)

        assert isinstance(resultado, str)
        assert len(resultado) > 0

    def test_backup_name_starts_with_bkp_prefix_106(self):
        """
        Nome do backup deve começar com o prefixo definido em
        cfg_cdu.tabela.BKP_PREFIX.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.cdu.config_cdu import cfg_cdu
        from app.model.cdu.create_tb_cdu import rename_to_backup

        resultado = rename_to_backup(engine)

        assert resultado.startswith(cfg_cdu.tabela.BKP_PREFIX)

    def test_rename_table_executed_with_original_name_107(self):
        """
        O DDL de RENAME deve referenciar o nome original da tabela.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.cdu.config_cdu import cfg_cdu
        from app.model.cdu.create_tb_cdu import rename_to_backup

        rename_to_backup(engine)

        sql_executado: str = str(conn_ctx.execute.call_args[0][0])
        assert cfg_cdu.tabela.TABELA in sql_executado

    def test_commit_called_after_rename_108(self):
        """
        commit() deve ser chamado apos o RENAME TABLE.
        """
        engine, conn_ctx = _engine_mock_ok()

        from app.model.cdu.create_tb_cdu import rename_to_backup

        rename_to_backup(engine)

        conn_ctx.commit.assert_called_once()


# Testes: _upsert()


class Test_Upsert_CDU:
    """
    Testa _upsert(): logica de INSERT/UPDATE/IGNORE por comparacao de chave.
    """

    def _df_upsert(self) -> pd.DataFrame:
        """
        DataFrame com 1 linha para testes unitários de upsert.
        """
        return pd.DataFrame(
            {
                "id_faixa_cdu": [1],
                "inicio_faixa": [0],
                "fim_faixa": [99],
                "nome_faixa_cdu": ["Generalidades"],
            }
        )

    def test_returns_true_on_success_109(self):
        """
        Fluxo completo sem erros -> retorna True.
        """
        engine, conn_ctx = _engine_mock_ok()
        conn_ctx.execute.return_value.fetchone.return_value = None

        from app.model.cdu.create_tb_cdu import _upsert

        assert _upsert(engine, self._df_upsert()) is True

    def test_insert_executed_when_key_not_found_110(self):
        """
        fetchone retorna None (chave inexistente) -> INSERT deve ser executado.
        """
        engine, conn_ctx = _engine_mock_ok()
        conn_ctx.execute.return_value.fetchone.return_value = None

        from app.model.cdu.create_tb_cdu import _upsert

        _upsert(engine, self._df_upsert())

        sqls_executados = [
            str(c.args[0]).upper()
            for c in conn_ctx.execute.call_args_list
            if c.args
        ]
        assert any("INSERT" in sql for sql in sqls_executados)

    def test_update_executed_when_key_found_and_name_differs_111(self):
        """
        fetchone retorna nome diferente do CSV -> UPDATE deve ser executado.
        """
        engine, conn_ctx = _engine_mock_ok()
        conn_ctx.execute.return_value.fetchone.return_value = ("Nome Antigo",)

        from app.model.cdu.create_tb_cdu import _upsert

        _upsert(engine, self._df_upsert())

        sqls_executados = [
            str(c.args[0]).upper()
            for c in conn_ctx.execute.call_args_list
            if c.args
        ]
        assert any("UPDATE" in sql for sql in sqls_executados)

    def test_no_dml_when_key_found_and_name_equal_112(self):
        """
        fetchone retorna nome idêntico ao CSV -> nenhum INSERT ou UPDATE.
        """
        engine, conn_ctx = _engine_mock_ok()
        conn_ctx.execute.return_value.fetchone.return_value = ("Generalidades",)

        from app.model.cdu.create_tb_cdu import _upsert

        _upsert(engine, self._df_upsert())

        sqls_executados = [
            str(c.args[0]).upper()
            for c in conn_ctx.execute.call_args_list
            if c.args
        ]
        assert not any("INSERT" in sql for sql in sqls_executados)
        assert not any("UPDATE" in sql for sql in sqls_executados)

    def test_commit_called_after_all_rows_113(self):
        """
        commit() deve ser chamado uma vez ao final do processamento.
        """
        engine, conn_ctx = _engine_mock_ok()
        conn_ctx.execute.return_value.fetchone.return_value = None

        from app.model.cdu.create_tb_cdu import _upsert

        _upsert(engine, self._df_upsert())

        conn_ctx.commit.assert_called_once()

    def test_returns_false_on_sqlalchemy_error_114(self):
        """
        SQLAlchemyError durante execute -> retorna False.
        """
        engine, conn_ctx = _engine_mock_ok()
        conn_ctx.execute.side_effect = exc.SQLAlchemyError("erro upsert")

        from app.model.cdu.create_tb_cdu import _upsert

        assert _upsert(engine, self._df_upsert()) is False

    def test_returns_false_on_generic_exception_115(self):
        """
        Exception generica durante execute -> retorna False.
        """
        engine, conn_ctx = _engine_mock_ok()
        conn_ctx.execute.side_effect = Exception("falha inesperada")

        from app.model.cdu.create_tb_cdu import _upsert

        assert _upsert(engine, self._df_upsert()) is False

    def test_processes_all_rows_in_dataframe_116(self):
        """
        Todos os registros do DataFrame devem ser verificados
        (1 SELECT por linha).
        """
        engine, conn_ctx = _engine_mock_ok()
        conn_ctx.execute.return_value.fetchone.return_value = None

        df = pd.DataFrame(
            {
                "id_faixa_cdu": [1, 2, 3],
                "inicio_faixa": [0, 100, 200],
                "fim_faixa": [99, 199, 299],
                "nome_faixa_cdu": ["A", "B", "C"],
            }
        )

        from app.model.cdu.create_tb_cdu import _upsert

        _upsert(engine, df)

        # Para cada linha: 1 SELECT + 1 INSERT = 2 calls
        # 3 linhas * 2 calls + 1 commit = mas commit nao e execute
        # Verificamos que execute foi chamado ao menos 3 vezes (1 por linha)
        assert conn_ctx.execute.call_count >= 3

    def test_select_uses_key_columns_117(self):
        """
        O SELECT de verificação deve usar as colunas de chave
        definidas no esquema.
        """
        engine, conn_ctx = _engine_mock_ok()
        conn_ctx.execute.return_value.fetchone.return_value = None

        from app.model.cdu.config_cdu import cfg_cdu
        from app.model.cdu.create_tb_cdu import _upsert

        _upsert(engine, self._df_upsert())

        primeiro_sql: str = str(conn_ctx.execute.call_args_list[0].args[0])
        for col in cfg_cdu.esquema.CHAVE_COMPARACAO:
            assert (
                col in primeiro_sql
            ), f"Coluna de chave '{col}' ausente no SELECT de verificação"

    def test_insert_uses_all_dataframe_columns_118(self):
        """
        O INSERT deve incluir todas as colunas presentes no DataFrame.
        """
        engine, conn_ctx = _engine_mock_ok()
        conn_ctx.execute.return_value.fetchone.return_value = None

        from app.model.cdu.create_tb_cdu import _upsert

        df = self._df_upsert()
        _upsert(engine, df)

        sqls_executados = [
            str(c.args[0])
            for c in conn_ctx.execute.call_args_list
            if c.args and "INSERT" in str(c.args[0]).upper()
        ]

        assert len(sqls_executados) > 0
        for col in df.columns:
            assert (
                col in sqls_executados[0]
            ), f"Coluna '{col}' ausente no INSERT"
