import inspect
import logging as log
import time

import pandas as pd

from app.config_app import cfg_app

logger = log.getLogger(__name__)  # Obter logger para este módulo


def load_with_retry(df_file_name: str, file_url: str) -> pd.DataFrame | None:
    """
    Tenta carregar um arquivo CSV com retry automático em caso de falha de rede.

    Args:
        df_file_name : Nome identificador do arquivo (usado no log).
        file_url     : URL completa do arquivo CSV.

    Returns:
        pd.DataFrame se carregado com sucesso, None após esgotar as tentativas.
    """
    _fn: str = inspect.currentframe().f_code.co_name
    max_attempts: int = cfg_app.parametros.MAX_TENTATIVAS
    tmp_wait: int = cfg_app.parametros.ESPERA_SEGUNDOS

    for tentativa in range(1, max_attempts + 1):
        try:
            df = pd.read_csv(file_url, sep=cfg_app.arquivo.SEP_CSV)
            logger.info(
                f"[{_fn}] Arquivo '{df_file_name}' carregado com sucesso "
                f"(tentativa {tentativa}/{max_attempts})."
            )
            return df

        except FileNotFoundError as e:
            _ex = type(e).__name__
            logger.error(
                f"[{_fn}] [{_ex}] Arquivo '{df_file_name}' não encontrado. "
                f"URL: {file_url}"
            )
            return None

        except Exception as e:
            _ex = type(e).__name__
            logger.warning(
                f"[{_fn}] [{_ex}] Tentativa {tentativa}/{max_attempts} "
                f"falhou para '{df_file_name}': {e}"
            )
            if tentativa < max_attempts:
                logger.info(
                    f"[{_fn}] Aguardando {tmp_wait}s antes da próxima tentativa..."
                )
                time.sleep(tmp_wait)

    # Esgotou todas as tentativas
    logger.error(
        f"[{_fn}] Arquivo '{df_file_name}' não pôde ser carregado após "
        f"{max_attempts} tentativas. URL: {file_url}"
    )
    return None


def load_url_emprestimos() -> pd.DataFrame:
    """
    Carrega todos os arquivos CSV do GIT da UFRN e concatena em um único DataFrame.

    Comportamento:
        - Tenta cada arquivo até MAX_TENTATIVAS vezes com intervalo de ESPERA_SEGUNDOS.
        - Arquivos que falharem são logados e ignorados.
        - Retorna os dados que conseguiu carregar (parcial ou total).
        - Emite mensagem no console informando o resultado da carga.

    Returns:
        pd.DataFrame: DataFrame consolidado com todos os arquivos carregados.
                    Vazio se nenhum arquivo for carregado.
    """
    _fn: str = inspect.currentframe().f_code.co_name
    ano_inicio: int = cfg_app.parametros.ANO_INICIAL
    ano_fim: int = cfg_app.parametros.ANO_FINAL

    total_expected: int = 0
    total_loaded: int = 0
    files_failed: list[str] = []
    dfs: list[pd.DataFrame] = []

    logger.info(
        f"[{_fn}] - Iniciando carga CSV: anos {ano_inicio} a {ano_fim - 1}."
    )

    for ano_atual in range(ano_inicio, ano_fim):
        for contador in range(1, 3):  # 2 arquivos por ano
            total_expected += 1

            df_file_name: str = f"df_{ano_atual}_{contador}"
            file_url: str = (
                f"{cfg_app.caminhos.URL_CSV}"
                f"{cfg_app.arquivo.PREFIXO_ARQ_CSV}"
                f"{ano_atual}"
                f"{contador}.{cfg_app.arquivo.EXT_CSV}?raw=true"
            )

            logger.debug(f"[{_fn}] Carregando: {file_url}")

            df_file_data: pd.DataFrame | None = load_with_retry(
                df_file_name, file_url
            )

            if df_file_data is not None:
                dfs.append(df_file_data)
                total_loaded += 1
            else:
                files_failed.append(df_file_name)

    if not dfs:
        msg = (
            f"[{_fn}] - ATENÇÃO: Nenhum arquivo CSV foi carregado. "
            f"Total esperado: {total_expected}. Verifique o arquivo de logs."
        )
        logger.error(msg)
        print(f"\n{msg}\n")
        return pd.DataFrame()

    df_final: pd.DataFrame = pd.concat(dfs, ignore_index=True)

    if total_loaded == total_expected:
        msg = (
            f"Carga CSV concluída com sucesso: "
            f"{total_loaded}/{total_expected} arquivos carregados "
            f"| {len(df_final):,} linhas no total."
        )
        logger.info(f"[{_fn}] {msg}")
        print(f"\n{msg}\n")
    else:
        msg_failed: str = ", ".join(files_failed)
        msg: str = (
            f"Carga CSV parcial: {total_loaded}/{total_expected} "
            f"arquivos carregados | {len(df_final):,} linhas no total.\n"
            f"  Arquivos não carregados: {msg_failed}"
        )
        logger.warning(f"[{_fn}] - {msg}")
        print(f"\n{msg}\n")

    return df_final
