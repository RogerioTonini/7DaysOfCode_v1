import logging as log
import os
import pandas as pd
import time

from pathlib import Path
from sqlalchemy import create_engine, text # type: ignore
from typing import Optional, Union

from utils.utilitarios import concat_path_file
#
TABLE_NAME = "tb_emprestimos"
CHUNK_SIZE = 1000  #


def config_parameters_pandas() -> None:
    pd.options.display.max_rows = 10000
    pd.options.display.max_columns = 30
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)
    return


def main() -> None:
    """Função principal"""
    print(dir())

if __name__ == "__main__":
    main()
