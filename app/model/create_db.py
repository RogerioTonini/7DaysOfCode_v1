"""
Módulo responsável por verificar e criar o banco de dados MySQL.

Localização : app/model/create_db.py
Fluxo       :
    1. Conecta ao MySQL SEM especificar o banco (conexão administrativa)
    2. Verifica se o banco já existe
    3. Se não existir → cria
    4. Se existir     → mantém, apenas loga
    5. Registra todo o procedimento no log
"""

import logging

from sqlalchemy import create_engine, exc, text

from app.config_app import cfg_app
from app.model.config_db import db_cfg


logger = logging.getLogger(__name__)


def _engine_sem_banco():
    """
    Cria engine conectado ao MySQL SEM especificar o banco de dados.
    Necessário para executar CREATE DATABASE.

    Returns:
        Engine | None: Engine administrativo ou None em caso de falha.
    """
    connection_string: str = (
        f"mysql+mysqlconnector://{db_cfg.DB_USER}:{db_cfg.DB_PASSWORD}"
        f"@{db_cfg.DB_HOST}:{db_cfg.DB_PORT}"
        f"?charset=utf8mb4"
    )

    if cfg_app.app.DEBUG:
        logger.debug("[create_db] Conectando ao MySQL sem especificar banco...")
        logger.debug(
            f"[create_db] Host: {db_cfg.DB_HOST} | Porta: {db_cfg.DB_PORT}"
        )

    try:
        engine = create_engine(
            connection_string,
            pool_pre_ping=True,
            echo=cfg_app.app.DEBUG,
        )

        # Valida a conexão administrativa
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        logger.info("[create_db] Conexão administrativa ao MySQL OK.")
        return engine

    except exc.OperationalError as e:
        logger.error(
            f"[create_db] [OperationalError] Falha na conexão administrativa: {e}"
        )
        return None

    except exc.SQLAlchemyError as e:
        logger.error(f"[create_db] [SQLAlchemyError] Erro inesperado: {e}")
        return None

    except Exception as e:
        logger.error(f"[create_db] [Exception] Erro geral: {e}")
        return None


def _banco_existe(conn, nome_banco: str) -> bool:
    """
    Verifica se o banco de dados já existe no MySQL.

    Args:
        conn       : Conexão SQLAlchemy ativa.
        nome_banco : Nome do banco a verificar.

    Returns:
        bool: True se existir, False caso contrário.
    """
    resultado = conn.execute(
        text(
            "SELECT SCHEMA_NAME FROM information_schema.SCHEMATA "
            "WHERE SCHEMA_NAME = :nome"
        ),
        {"nome": nome_banco},
    ).fetchone()

    return resultado is not None


def create_database() -> bool:
    """
    Verifica a existência do banco de dados e cria caso não exista.
    O nome do banco é lido do .env via db_cfg.DB_NAME.

    Returns:
        bool: True se o banco estiver disponível (criado ou já existente),
        False em caso de falha.
    """
    nome_banco: str = db_cfg.DB_NAME

    logger.info(f"[create_db] Verificando banco de dados: '{nome_banco}'...")

    engine = _engine_sem_banco()
    if engine is None:
        logger.error(
            "[create_db] Não foi possível estabelecer conexão administrativa."
        )
        return False

    try:
        with engine.connect() as conn:

            if _banco_existe(conn, nome_banco):
                logger.info(
                    f"[create_db] Banco '{nome_banco}' já existe. "
                    "Nenhuma alteração realizada."
                )
            else:
                logger.info(
                    f"[create_db] Banco '{nome_banco}' não encontrado. Criando..."
                )

                conn.execute(
                    text(
                        f"CREATE DATABASE `{nome_banco}` "
                        f"CHARACTER SET utf8mb4 "
                        f"COLLATE utf8mb4_unicode_ci"
                    )
                )

                logger.info(
                    f"[create_db] Banco '{nome_banco}' criado com sucesso "
                    f"(charset: utf8mb4 | collation: utf8mb4_unicode_ci)."
                )

        return True

    except exc.OperationalError as e:
        logger.error(
            f"[create_db] [OperationalError] Erro ao verificar/criar banco: {e}"
        )
        return False

    except exc.SQLAlchemyError as e:
        logger.error(f"[create_db] [SQLAlchemyError] Erro inesperado: {e}")
        return False

    except Exception as e:
        logger.error(f"[create_db] [Exception] Erro geral: {e}")
        return False

    finally:
        engine.dispose()
        logger.debug("[create_db] Conexão administrativa encerrada.")
