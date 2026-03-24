import inspect
import logging as log

from sqlalchemy import create_engine, exc, text
from sqlalchemy.engine import Engine

from app.config_app import cfg_app
from app.model.config_db import db_cfg  # Configurações exclusivas do banco

logger = log.getLogger(__name__)


def connect_db() -> Engine | None:
    """
    Função responsável por conectar ao banco de dados MySQL.

    Returns:
        Engine | None: Engine do SQLAlchemy se conexão OK, None caso contrário.
    """
    _fn: str = inspect.currentframe().f_code.co_name

    connection_string: str = (
        f"mysql+mysqlconnector://{db_cfg.DB_USER}:{db_cfg.DB_PASSWORD}"
        f"@{db_cfg.DB_HOST}:{db_cfg.DB_PORT}/{db_cfg.DB_NAME}"
        f"?charset=utf8mb4"
    )

    if cfg_app.app.DEBUG:
        logger.debug(f"[{_fn}] - Iniciando conexão com o banco de dados...")
        logger.debug(
            f"[{_fn}] - Host: {db_cfg.DB_HOST} | Porta: {db_cfg.DB_PORT}"
        )
        logger.debug(
            f"[{_fn}] - Banco: {db_cfg.DB_NAME} | Usuário: {db_cfg.DB_USER}"
        )

    try:
        engine: Engine = create_engine(
            connection_string,
            pool_pre_ping=True,  # Valida conexão antes de usar do pool
            echo=False,
            # Gera mensagem no arquivo de LOG PARA DEBUG
            # echo=cfg_app.app.DEBUG,  # Exibe SQL gerado somente em modo debug
        )

        # Valida a conexão de forma explícita (SQLAlchemy 2.x)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info(f"[{_fn}] - Conexão com o Banco de Dados OK")

        return engine

    except exc.OperationalError as e:
        _ex: str = type(e).__name__
        logger.error(
            f"[{_fn}] - [{_ex}] - Verifique host/porta/credenciais: {e}"
        )
        return None

    except exc.SQLAlchemyError as e:
        _ex: str = type(e).__name__
        logger.error(f"[{_fn}] - [{_ex}] - Erro inesperado do SQLAlchemy: {e}")
        return None

    except Exception as e:
        _ex: str = type(e).__name__
        logger.error(
            f"[{_fn}] - [{_ex}] - Erro geral ao conectar ao banco de dados: {e}"
        )
        return None


def test_connect() -> bool:
    """
    Verifica/cria o banco de dados e testa a conexão MySQL.
    Centraliza as validações de infraestrutura que eram feitas no main.py.

    Returns:
        bool: True se banco disponível e conexão OK, False caso contrário.
    """
    from app.model.create_db import create_database

    _fn: str = inspect.currentframe().f_code.co_name

    logger.info(f"[{_fn}] Iniciando validação de infraestrutura...")

    if not create_database():
        logger.error(f"[{_fn}] Falha ao verificar/criar banco de dados.")
        return False

    engine: Engine | None = connect_db()

    if engine is None:
        logger.error(f"[{_fn}] Falha ao conectar ao banco de dados.")
        return False

    logger.info(f"[{_fn}] Infraestrutura validada com sucesso.")
    return True
