"""
Subpacote CDU — tabela de classificação decimal universal.

Módulos:
    config_cdu    -> cfg_cdu (configuração e esquema)
    create_tb_cdu -> load_tb_cdu (carga e upsert)
"""

from app.model.cdu.config_cdu import cfg_cdu
from app.model.cdu.create_tb_cdu import read_csv

__all__ = [
    "cfg_cdu",
    "read_csv",
]

__version__ = "1.0.0"
