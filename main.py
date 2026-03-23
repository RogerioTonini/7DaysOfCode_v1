# main.py (na raiz do projeto)

"""
Script principal do projeto 7 Days of Code
"""
import logging
import sys

import pandas as pd

import app.model.connect as conn

# import app.model.create_db as db
import app.pipeline.load_URL as url
from app.config_app import cfg_app
from app.utils.config_log import cfg_log

# from sqlalchemy import create_engine, text


cfg_app.pandas_cfg.aplicar()
cfg_log.configurar(cfg_app.caminhos.PATH_LOG)


logger = logging.getLogger(__name__)


def main() -> None:
    """Função principal"""

    logger.info("===== Aplicação iniciada =====")
    logger.debug(f"Caminho dados: {cfg_app.caminhos.PATH_DATA}")
    logger.debug(f"Caminho logs: {cfg_app.caminhos.PATH_LOG}")

    try:
        if not conn.test_connect():
            logger.error("Falha na validação da infraestrutura")
            print(
                "Falha na validação da infraestrutura, verificar arquivo logs"
            )
            sys.exit(1)

        df: pd.DataFrame = url.load_url_csv()

        if df.empty:
            logger.error("Nenhum arquivo CSV carregado")
            print("Nenhum arquivo CSV carregado, verificar arquivo logs")
            sys.exit(1)

        logger.info("===== Arquivos CSV carregados com sucesso =====")

    except Exception as e:
        logger.critical(f"Erro crítico: {e}", exc_info=True)
        print("Erro crítico, verificar arquivo logs")
        sys.exit(1)


if __name__ == "__main__":
    main()
