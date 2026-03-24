"""
Módulo genérico de inserção de dados em lotes.

Localização : app/model/insert_data.py
Uso         : Compartilhado por create_tb_raw.py e create_tb_cdu.py
"""

import inspect
import logging

import pandas as pd
from sqlalchemy import exc
from sqlalchemy import inspect as sa_inspect
from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.config_app import cfg_app

logger = logging.getLogger(__name__)


def create_table(
    engine: Engine,
    nome_tabela: str,
    colunas: tuple,
    tipos_coluna: dict | str,
    auto_increment: bool = False,
) -> bool:
    """
    Cria uma tabela genérica no banco de dados.

    Args:
        engine         : Engine SQLAlchemy ativo.
        nome_tabela    : Nome da tabela a criar.
        colunas        : Tupla com os nomes das colunas.
        tipos_coluna   : dict {coluna: tipo} ou str quando todas as colunas
                        tiverem o mesmo tipo (ex: "VARCHAR(255)").
        auto_increment : Se True, adiciona coluna num_index INT AUTO_INCREMENT
                        PRIMARY KEY como primeira coluna.

    Returns:
        bool: True se criada com sucesso, False em caso de falha.

    Exemplos:
        # Todas as colunas com mesmo tipo (RAW)
        create_table(engine, "tb_emprestimos_RAW", COLUNAS, "VARCHAR(255)")

        # Colunas com tipos diferentes (CDU)
        create_table(engine, "tb_CDU", COLUNAS, {"id": "INT", ...},
        auto_increment=True)
    """
    _fn: str = inspect.currentframe().f_code.co_name

    # Monta dict de tipos independente do formato recebido
    if isinstance(tipos_coluna, str):
        mapa_tipos: dict[str, str] = {col: tipos_coluna for col in colunas}
    else:
        mapa_tipos: dict[str, str] = tipos_coluna

    colunas_sql: str = ",\n    ".join(
        f"`{col}` {mapa_tipos[col]}" for col in colunas
    )

    # Adiciona AUTO_INCREMENT se solicitado
    pk_sql: str = (
        "`num_index` INT AUTO_INCREMENT PRIMARY KEY,\n    "
        if auto_increment
        else ""
    )

    ddl: str = f"""
        CREATE TABLE `{nome_tabela}` (
            {pk_sql}{colunas_sql}
        )
        ENGINE=InnoDB
        DEFAULT CHARSET=utf8mb4
        COLLATE=utf8mb4_unicode_ci
    """

    try:
        with engine.connect() as conn:
            conn.execute(text(ddl))
            conn.commit()

        logger.info(f"[{_fn}] Tabela '{nome_tabela}' criada com sucesso.")
        return True

    except exc.SQLAlchemyError as e:
        _ex: str = type(e).__name__
        logger.error(
            f"[{_fn}] [{_ex}] Erro ao criar tabela '{nome_tabela}': {e}"
        )
        return False

    except Exception as e:
        _ex = type(e).__name__
        logger.error(f"[{_fn}] [{_ex}] Erro geral: {e}")
        return False


def check_table_exists(engine: Engine, table_name: str) -> bool:
    """
    Verifica se tb_CDU existe no banco.
    """
    return sa_inspect(engine).has_table(table_name)


def insert_data(engine: Engine, df: pd.DataFrame, nome_tabela: str) -> bool:
    """
    Insere um DataFrame em uma tabela do banco de dados em lotes.

    Args:
        engine      : Engine SQLAlchemy ativo.
        df          : DataFrame com os dados a inserir.
        nome_tabela : Nome da tabela destino.

    Returns:
        bool: True se todos os lotes foram inseridos, False em caso de falha.
    """
    _fn: str = inspect.currentframe().f_code.co_name
    lote: int = cfg_app.parametros.QTD_REG_LOTE
    total_linhas: int = len(df)
    total_lotes: int = (total_linhas + lote - 1) // lote

    logger.info(
        f"[{_fn}] - Tabela: '{nome_tabela}' | "
        f"{total_linhas:,} linhas | "
        f"{total_lotes:,} lotes de {lote:,} registros."
    )

    try:
        linhas_inseridas: int = 0

        for num_lote, inicio in enumerate(
            range(0, total_linhas, lote), start=1
        ):
            bloco: pd.DataFrame = df.iloc[inicio : inicio + lote]

            bloco.to_sql(
                name=nome_tabela,
                con=engine,
                if_exists="append",
                index=False,
                method="multi",
            )

            linhas_inseridas += len(bloco)
            pct: float = (linhas_inseridas / total_linhas) * 100

            logger.info(
                f"[{_fn}] - Lote {num_lote:03d}/{total_lotes:03d} - "
                f"{linhas_inseridas:,}/{total_linhas:,} linhas inseridas "
                f"({pct:.1f}%)"
            )

        logger.info(
            f"[{_fn}] - Inserção concluída: "
            f"{linhas_inseridas:,} linhas inseridas na tabela '{nome_tabela}'."
        )
        return True

    except exc.SQLAlchemyError as e:
        _ex: str = type(e).__name__
        logger.error(
            f"[{_fn}] - [{_ex}] - Erro ao inserir lote em '{nome_tabela}': {e}"
        )
        return False

    except Exception as e:
        _ex: str = type(e).__name__
        logger.error(f"[{_fn}] - [{_ex}] - Erro geral em '{nome_tabela}': {e}")
        return False
