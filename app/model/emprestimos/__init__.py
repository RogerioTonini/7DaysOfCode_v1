"""
Subpacote emprestimos — tabelas RAW, Bronze, Silver e Gold.

Módulos:
    config_emprestimos -> cfg_emprestimos (configuração e esquemas)
    create_tb_raw      -> check_table_raw, prepare_table_raw, insert_data_raw
    util_model         -> insert_data (carga e upsert)
"""

from app.model.emprestimos.config_emprestimos import cfg_emprestimos
from app.model.emprestimos.create_tb_raw import (
    check_columns,
    check_table_raw,
    create_table_raw,
    get_table_columns,
)
from app.model.util_model import insert_data

__all__ = [
    "cfg_emprestimos",
    "check_columns",
    "check_table_raw",
    "create_table_raw",
    "get_table_columns",
    "insert_data",
]
