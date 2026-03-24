"""
Pacote de modelos e acesso ao banco de dados.

Módulos disponíveis:
    connect      -> connect_db(), test_connect()
    create_db    -> create_database()
    config_db    -> db_cfg
    util_model   -> create_table(), insert_data()
    cdu/         -> cfg_cdu, load_tb_cdu
    emprestimos/ -> cfg_emprestimos, check_table_raw
"""

from app.model.config_db import db_cfg
from app.model.connect import connect_db, test_connect
from app.model.create_db import create_database
from app.model.util_model import create_table, insert_data

__all__ = [
    "connect_db",
    "test_connect",
    "create_database",
    "db_cfg",
    "create_table",
    "insert_data",
]
