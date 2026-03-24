"""
Módulo responsável por criar e manter a tabela tb_CDU.

Localização : app/model/cdu/create_tb_cdu.py
Fonte       : PATH_DATA/tb_CDU.csv

Fluxo:
    1. Lê o CSV de PATH_DATA
    2. Verifica se a tabela existe
        a. Não existe                -> cria + insere
        b. Existe, esquema diferente -> renomeia bkp + recria + insere
        c. Existe, esquema igual
            - Chave existe, nome igual     -> ignora
            - Chave existe, nome diferente -> UPDATE nome_faixa_cdu
            - Chave não existe             -> INSERT
"""

import inspect
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy import Engine, Inspector, exc
from sqlalchemy import inspect as sa_inspect
from sqlalchemy import text

from app.config_app import cfg_app
from app.model.cdu.config_cdu import cfg_cdu

logger = logging.getLogger(__name__)


def read_csv() -> pd.DataFrame | None:
    """
    Lê e valida o arquivo tb_CDU.csv de PATH_DATA.
    """
    _fn: str = inspect.currentframe().f_code.co_name
    file: Path = (
        Path(cfg_app.caminhos.PATH_DATA)
        / f"{cfg_cdu.esquema.ARQUIVO_CSV}.{cfg_app.file.EXT_CSV}"
    )

    logger.info(f"[{_fn}] - Lendo arquivo: {file}")

    if not file.exists():
        logger.error(f"[{_fn}] - Arquivo não encontrado: {file}")
        return None

    try:
        df: pd.DataFrame = pd.read_csv(file, sep=cfg_app.arquivo.SEP_CSV)

        # Valida colunas
        expected_columns: set[str] = set(cfg_cdu.esquema.COLUNAS)
        received_columns: set[str] = set(df.columns.tolist())
        missing_columns: set[str] = expected_columns - received_columns

        if missing_columns:
            logger.error(
                f"[{_fn}] - Colunas ausentes no CSV: {sorted(missing_columns)}\n"
                f"  Esperadas : {sorted(expected_columns)}\n"
                f"  Recebidas : {sorted(received_columns)}"
            )
            return None

        df: pd.DataFrame = df[list(cfg_cdu.esquema.COLUNAS)]
        logger.info(f"[{_fn}] - CSV lido: {len(df):,} registros.")
        return df

    except Exception as e:
        _ex = type(e).__name__
        logger.error(f"[{_fn}] - [{_ex}] - Erro ao ler CSV: {e}")
        return None


def check_schema_match(engine: Engine) -> bool:
    """
    Compara colunas do banco com o esquema definido (ignora num_index).
    """
    inspetor: Inspector = sa_inspect(engine)
    db_columns: list[str] = [
        col["name"]
        for col in inspetor.get_columns(cfg_cdu.tabela.TABELA)
        if col["name"] != "num_index"
    ]
    return db_columns == list(cfg_cdu.esquema.COLUNAS)


def create_table(engine: Engine) -> None:
    """
    Cria a tabela tb_CDU com AUTO_INCREMENT e tipos definidos.
    """
    _fn: str = inspect.currentframe().f_code.co_name

    columns_sql: str = ",\n    ".join(
        f"`{col}` {tipo}" for col, tipo in cfg_cdu.esquema.as_dict().items()
    )

    ddl: str = f"""
        CREATE TABLE `{cfg_cdu.tabela.TABELA}` (
                `num_index` INT AUTO_INCREMENT PRIMARY KEY,
                {columns_sql}
            )
        ENGINE=InnoDB
        DEFAULT CHARSET=utf8mb4
        COLLATE=utf8mb4_unicode_ci
    """

    with engine.connect() as conn:
        conn.execute(text(ddl))
        conn.commit()

    logger.info(f"[{_fn}] Tabela '{cfg_cdu.tabela.TABELA}' criada com sucesso.")


def rename_to_backup(engine: Engine) -> str:
    """
    Renomeia tb_CDU para tb_CDU_bkp_{timestamp}.
    """
    _fn: str = inspect.currentframe().f_code.co_name
    timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    name_bkp: str = f"{cfg_cdu.tabela.BKP_PREFIX}{timestamp}"

    with engine.connect() as conn:
        conn.execute(
            text(f"RENAME TABLE `{cfg_cdu.tabela.TABELA}` TO `{name_bkp}`")
        )
        conn.commit()

    logger.info(f"[{_fn}] - Tabela renomeada para '{name_bkp}'.")
    return name_bkp


def run_upsert(engine: Engine, df: pd.DataFrame) -> bool:
    """
    Compara cada registro do CSV com o banco pela chave
    (id_faixa_cdu + inicio_faixa + fim_faixa):
        - Chave existe + nome igual     - ignora
        - Chave existe + nome diferente - UPDATE nome_faixa_cdu
        - Chave nao existe              - INSERT
    """
    _fn: str = inspect.currentframe().f_code.co_name
    key_columns: list[str] = list(cfg_cdu.esquema.CHAVE_COMPARACAO)
    field: str = cfg_cdu.esquema.CAMPO_ATUALIZAVEL
    table: str = cfg_cdu.tabela.TABELA

    updated: int = 0
    inserted: int = 0
    ignored: int = 0

    logger.info(f"[{_fn}] - Iniciando upsert: {len(df):,} registros no CSV.")

    try:
        with engine.connect() as conn:
            for _, row in df.iterrows():
                filter_sql: str = " AND ".join(
                    f"`{col}` = :{col}" for col in key_columns
                )
                params: dict[str, Any] = {col: row[col] for col in key_columns}

                resultado: tuple[Any] | None = conn.execute(
                    text(
                        f"SELECT `{field}` FROM `{table}` "
                        f"WHERE {filter_sql} LIMIT 1"
                    ),
                    params,
                ).fetchone()

                if resultado is None:
                    columns: str = ", ".join(f"`{c}`" for c in df.columns)
                    values: str = ", ".join(f":{c}" for c in df.columns)
                    conn.execute(
                        text(
                            f"INSERT INTO `{table}` ({columns}) "
                            f"VALUES ({values})"
                        ),
                        row.to_dict(),
                    )
                    inserted += 1

                elif resultado[0] != row[field]:
                    params_upd: dict[str, Any] = {**params, field: row[field]}
                    conn.execute(
                        text(
                            f"UPDATE `{table}` SET `{field}` = :{field} "
                            f"WHERE {filter_sql}"
                        ),
                        params_upd,
                    )
                    updated += 1

                else:
                    ignored += 1

            conn.commit()

        logger.info(
            f"[{_fn}] - Upsert concluído - "
            f"Inseridos: {inserted:,} | "
            f"Atualizados: {updated:,} | "
            f"Ignorados: {ignored:,}"
        )
        return True

    except exc.SQLAlchemyError as e:
        _ex: str = type(e).__name__
        logger.error(f"[{_fn}] - [{_ex}] - Erro no upsert: {e}")
        return False

    except Exception as e:
        _ex: str = type(e).__name__
        logger.error(f"[{_fn}] - [{_ex}] - Erro geral: {e}")
        return False


def _upsert(engine: Engine, df: pd.DataFrame) -> bool:
    """
    Compara cada registro do CSV com o banco pela chave
    (id_faixa_cdu + inicio_faixa + fim_faixa):
        - Chave existe + nome igual     → ignora
        - Chave existe + nome diferente → UPDATE nome_faixa_cdu
        - Chave não existe              → INSERT
    """
    _fn: str = inspect.currentframe().f_code.co_name
    key_columns: list[str] = list(cfg_cdu.esquema.CHAVE_COMPARACAO)
    field: str = cfg_cdu.esquema.CAMPO_ATUALIZAVEL
    table: str = cfg_cdu.tabela.TABELA

    updated: int = 0
    inserted: int = 0
    ignored: int = 0

    logger.info(f"[{_fn}] - Iniciando upsert: {len(df):,} registros no CSV.")

    try:
        with engine.connect() as conn:
            for _, row in df.iterrows():
                filter_sql: str = " AND ".join(
                    f"`{col}` = :{col}" for col in key_columns
                )
                params: dict[str, Any] = {col: row[col] for col in key_columns}

                # Busca registro pela chave
                resultado: tuple[Any] | None = conn.execute(
                    text(
                        f"SELECT `{field}` FROM `{table}` "
                        f"WHERE {filter_sql} LIMIT 1"
                    ),
                    params,
                ).fetchone()

                if resultado is None:
                    # Chave não existe → INSERT
                    columns: str = ", ".join(f"`{c}`" for c in df.columns)
                    values: str = ", ".join(f":{c}" for c in df.columns)
                    conn.execute(
                        text(
                            f"INSERT INTO `{table}` ({columns}) "
                            f"VALUES ({values})"
                        ),
                        row.to_dict(),
                    )
                    inserted += 1

                elif resultado[0] != row[field]:
                    # Chave existe + nome diferente → UPDATE
                    params_upd = {**params, field: row[field]}
                    conn.execute(
                        text(
                            f"UPDATE `{table}` SET `{field}` = :{field} "
                            f"WHERE {filter_sql}"
                        ),
                        params_upd,
                    )
                    updated += 1

                else:
                    # Chave existe + nome igual → ignora
                    ignored += 1

            conn.commit()

        logger.info(
            f"[{_fn}] - Upsert concluído — "
            f"Inseridos: {inserted:,} | "
            f"Atualizados: {updated:,} | "
            f"Ignorados: {ignored:,}"
        )
        return True

    except exc.SQLAlchemyError as e:
        _ex = type(e).__name__
        logger.error(f"[{_fn}] - [{_ex}] - Erro no upsert: {e}")
        return False

    except Exception as e:
        _ex = type(e).__name__
        logger.error(f"[{_fn}] - [{_ex}] - Erro geral: {e}")
        return False
