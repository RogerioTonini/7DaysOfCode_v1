"""
Módulo pipeline da aplicação
"""

from app.pipeline.load_cdu import load_tb_cdu
from app.pipeline.load_emprestimos import load_url_emprestimos

# Exportações públicas
__all__ = [
    "load_tb_cdu",
    "load_url_emprestimos",
]

# Metadados
__version__ = "0.1.0"
