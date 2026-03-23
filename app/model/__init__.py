"""
Módulo de modelos de dados
"""

from app.model.config_db import cfg_db

# Exportações públicas
__all__ = [
    "cfg_db",
    "connect",
    "create_db",
]

# Metadados
__version__ = "0.1.0"
