"""
Módulo principal da aplicação
"""
from app.config_app import cfg_app

# Exportações públicas
__all__ = [
    "cfg_app",
]

# Metadados
__version__ = "0.1.0"

# Aplicar configurações do Pandas ao importar o pacote
cfg_app.pandas_cfg.aplicar()
