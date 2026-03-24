# main.py (na raiz do projeto)

"""
Script principal do projeto 7 Days of Code
"""
import inspect
import logging
import sys

import pandas as pd

from app.config_app import cfg_app
from app.model import connect as conn
from app.model.emprestimos import check_table_raw
from app.pipeline.load_cdu import load_tb_cdu
from app.pipeline.load_emprestimos import load_url_emprestimos
from app.utils.config_log import cfg_log

cfg_app.pandas_cfg.aplicar()
cfg_log.configurar(cfg_app.caminhos.PATH_LOG)

logger: logging.Logger = logging.getLogger(__name__)

def main() -> None:
    """Função principal"""
    _fn: str = inspect.currentframe().f_code.co_name

    logger.info("===== Aplicação iniciada =====")
    logger.debug(f"Caminho dados: {cfg_app.caminhos.PATH_DATA}")
    logger.debug(f"Caminho logs: {cfg_app.caminhos.PATH_LOG}")

    try:
        # Verifica a existência do DB e testa a conexão
        if not conn.test_connect():
            logger.error("Falha na validação da infraestrutura")
            print(
                "Falha na validação da infraestrutura, verificar arquivo logs"
            )
            sys.exit(1)

        # Verifica a existência da tabela tb_cdu e carrega os dados
        if not load_tb_cdu():
            logger.error("Falha no pipeline CDU.")
            print("Falha no pipeline CDU, verificar arquivo logs.")
            sys.exit(1)

        # Verifica a existência da tabela tb_emprestimos_raw e carrega os dados
        df: pd.DataFrame = load_url_emprestimos()

        if df.empty:
            logger.error("Nenhum arquivo CSV carregado")
            print("Nenhum arquivo CSV carregado, verificar arquivo logs")
            sys.exit(1)

        if not check_table_raw(df):
            logger.error(f"[{_fn}] - Falha ao criar tabela RAW")
            print("Falha ao criar tabela RAW, verificar arquivo logs")
            sys.exit(1)

        logger.info(f"[{_fn}] - Carga de dados finalizada com sucesso")

    except Exception as e:
        logger.critical(f"Erro crítico: {e}", exc_info=True)
        print("Erro crítico, verificar arquivo logs")
        sys.exit(1)


if __name__ == "__main__":
    main()
