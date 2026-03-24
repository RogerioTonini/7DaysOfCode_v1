"""
Pipeline de carga da tabela tb_CDU.

Localização : app/pipeline/load_cdu.py
Responsabilidade: ponto de entrada do pipeline CDU, chamado pelo main.py
"""

import inspect
import logging

import pandas as pd

from app.model.cdu.config_cdu import cfg_cdu
from app.model.cdu.create_tb_cdu import (
    check_schema_match,
    read_csv,
    rename_to_backup,
    run_upsert,
)
from app.model.connect import connect_db
from app.model.util_model import check_table_exists, create_table, insert_data

logger = logging.getLogger(__name__)


def load_tb_cdu() -> bool:
    """
    Orquestra a carga completa da tabela tb_CDU.

    Returns:
        bool: True se carga bem-sucedida, False em caso de falha.
    """
    _fn: str = inspect.currentframe().f_code.co_name

    logger.info(f"[{_fn}] - Iniciando carga: '{cfg_cdu.tabela.TABELA}'")

    df: pd.DataFrame | None = read_csv()
    if df is None:
        logger.error(f"[{_fn}] - Falha na leitura do CSV. Abortando.")
        return False

    engine = connect_db()
    if engine is None:
        logger.error(f"[{_fn}] - Falha ao conectar ao banco. Abortando.")
        return False

    try:
        if not check_table_exists(engine, cfg_cdu.tabela.TABELA):

            logger.info(f"[{_fn}] - Tabela nao encontrada. Criando...")
            if not create_table(
                engine=engine,
                nome_tabela=cfg_cdu.tabela.TABELA,
                colunas=cfg_cdu.esquema.COLUNAS,
                tipos_coluna=cfg_cdu.esquema.as_dict(),  # dict com tipos diferentes
                auto_increment=True,  # adiciona num_index
            ):
                return False
            return insert_data(engine, df, cfg_cdu.tabela.TABELA)

        if not check_schema_match(engine):
            logger.warning(
                f"[{_fn}] - Esquema diverge do esperado. "
                "Realizando backup e recriando tabela..."
            )

            nome_bkp = rename_to_backup(engine)
            logger.info(
                f"[{_fn}] - Tabela antiga salva como '{nome_bkp}'. "
                "Criando tabela com novo layout..."
            )

            if not create_table(
                engine=engine,
                nome_tabela=cfg_cdu.tabela.TABELA,
                colunas=cfg_cdu.esquema.COLUNAS,
                tipos_coluna=cfg_cdu.esquema.as_dict(),
                auto_increment=True,
            ):
                return False

            return insert_data(engine, df, cfg_cdu.tabela.TABELA)

        logger.info(f"[{_fn}] - Esquema OK. Executando upsert...")
        return run_upsert(engine, df)

    except Exception as e:
        _ex = type(e).__name__
        logger.error(f"[{_fn}] - [{_ex}] - Erro geral: {e}")
        return False

    finally:
        engine.dispose()
        logger.debug(f"[{_fn}] - Conexão encerrada.")
