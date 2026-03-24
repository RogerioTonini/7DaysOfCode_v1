"""
Módulo responsável por criar e gerenciar tabelas no padrão medalhão.

Localização : app/model/create_tb_raw.py
Fluxo RAW   :
    1. Verifica se a tabela RAW existe
    2. Se existir  -> compara colunas com o esquema definido
        a. Colunas iguais     -> apaga os dados (TRUNCATE)
        b. Colunas diferentes -> renomeia para tb_emprestimos_RAW_bkp_{data}
            e cria nova tabela com esquema atual
    3. Se não existir.........-> cria a tabela
    4. Insere dados em lotes de QTD_REG_LOTE linhas
"""

import inspect
import logging
from datetime import datetime

import pandas as pd
from sqlalchemy import Engine, exc
from sqlalchemy import inspect as sa_inspect
from sqlalchemy import text

from app.model.connect import connect_db
from app.model.emprestimos.config_emprestimos import cfg_emprestimos
from app.model.util_model import check_table_exists, insert_data

logger = logging.getLogger(__name__)


def get_table_columns(engine: Engine, nome_tabela: str) -> list[str]:
    """
    Retorna a lista de colunas da tabela no banco.
    """
    inspetor = sa_inspect(engine)
    return [col["name"] for col in inspetor.get_columns(nome_tabela)]


def check_columns(columns_table: list[str], columns_schema: tuple) -> bool:
    """
    Compara se as colunas do banco são iguais ao esquema definido.
    """
    return list(columns_table) == list(columns_schema)


def create_table_raw(engine: Engine, table_name: str) -> None:
    """
    Cria a tabela RAW com todas as colunas VARCHAR(255).
    """
    _fn: str = inspect.currentframe().f_code.co_name

    columns_sql: str = ",\n    ".join(
        f"`{col}` {cfg_emprestimos.esquema_raw.TIPO_COLUNA}"
        for col in cfg_emprestimos.esquema_raw.COLUNAS
    )

    ddl: str = f"""
        CREATE TABLE `{table_name}` ({columns_sql})
        ENGINE=InnoDB
        DEFAULT CHARSET=utf8mb4
        COLLATE=utf8mb4_unicode_ci
    """

    with engine.connect() as conn:
        conn.execute(text(ddl))
        conn.commit()

    logger.info(f"[{_fn}] - Tabela '{table_name}' criada com sucesso.")


def prepare_table_raw(df: pd.DataFrame) -> bool:
    """
    Verifica/cria a tabela RAW e prepara para receber novos dados.

    Args:
        df: DataFrame com os dados carregados do CSV.

    Returns:
        bool: True se a tabela estiver pronta, False em caso de falha.
    """
    _fn: str = inspect.currentframe().f_code.co_name

    table_name: str = cfg_emprestimos.tabelas.RAW
    columns_schema: tuple = cfg_emprestimos.esquema_raw.COLUNAS

    logger.info(f"[{_fn}] - Verificando tabela '{table_name}'...")

    engine: Engine | None = connect_db()
    if engine is None:
        logger.error(f"[{_fn}] - Falha ao obter conexão com o banco.")
        return False

    try:
        if not check_table_exists(engine, table_name):
            # Tabela não existe -> criar
            logger.info(
                f"[{_fn}] - Tabela '{table_name}' não encontrada. Criando..."
            )
            create_table_raw(engine, table_name)

        else:
            columns_table: list[str] = get_table_columns(engine, table_name)

            if check_columns(columns_table, columns_schema):
                # Colunas iguais -> truncar dados
                logger.info(
                    f"[{_fn}] - Esquema da tabela '{table_name}' está"
                    " atualizado. Removendo dados anteriores (TRUNCATE)..."
                )
                with engine.connect() as conn:
                    conn.execute(text(f"TRUNCATE TABLE `{table_name}`"))
                    conn.commit()
                logger.info(f"[{_fn}] TRUNCATE executado com sucesso.")

            else:
                # Colunas diferentes -> renomear + recriar
                timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
                name_bkp: str = (
                    f"{cfg_emprestimos.tabelas.RAW_BKP_PREFIX}{timestamp}"
                )

                logger.warning(
                    f"[{_fn}] - Esquema da tabela '{table_name}' diverge do"
                    f" esperado.\n"
                    f"  Colunas no banco  : {columns_table}\n"
                    f"  Colunas esperadas : {list(columns_schema)}"
                )
                logger.info(
                    f"[{_fn}] - Renomeando '{table_name}' → '{name_bkp}'..."
                )

                with engine.connect() as conn:
                    conn.execute(
                        text(f"RENAME TABLE `{table_name}` TO `{name_bkp}`")
                    )
                    conn.commit()

                logger.info(
                    f"[{_fn}] - Tabela renomeada para '{name_bkp}'. "
                    "Criando nova tabela com layout atualizado..."
                )
                create_table_raw(engine, table_name)
                logger.info(
                    f"[{_fn}] - Nova tabela '{table_name}' criada com layout"
                    f" atualizado."
                )

        return True

    except exc.SQLAlchemyError as e:
        _ex = type(e).__name__
        logger.error(f"[{_fn}] - [{_ex}] - Erro ao preparar tabela RAW: {e}")
        return False

    except Exception as e:
        _ex = type(e).__name__
        logger.error(f"[{_fn}] - [{_ex}] - Erro geral: {e}")
        return False

    finally:
        engine.dispose()


def check_table_raw(df: pd.DataFrame) -> bool:
    """
    Orquestra a preparação e inserção de dados na tabela RAW.

    Args:
        df: DataFrame com os dados carregados do CSV.

    Returns:
        bool: True se preparação e inserção bem-sucedidas, False em caso de falha.
    """
    _fn: str = inspect.currentframe().f_code.co_name

    if not prepare_table_raw(df):
        logger.error(f"[{_fn}] - Falha ao preparar tabela RAW.")
        print("Falha ao preparar tabela RAW, verificar arquivo logs.")
        return False

    engine = connect_db()
    if engine is None:
        logger.error(f"[{_fn}] - Falha ao obter conexão com o banco.")
        return False

    if not insert_data(engine, df, cfg_emprestimos.tabelas.RAW):
        logger.error(f"[{_fn}] - Falha ao inserir dados na tabela RAW.")
        print("Falha ao inserir dados na tabela RAW, verificar arquivo logs.")
        engine.dispose()
        return False

    engine.dispose()
    return True
