"""
Configurações de logging do projeto.

Responsabilidade: definir níveis, formato, rotação e inicialização do logger.
Localização: app/utils/config_log.py
"""

import logging as log
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from pathlib import Path


@dataclass(frozen=True)
class LoggingConfig:
    """Configurações do sistema de logging."""

    LEVEL: str = "INFO"
    FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    FILENAME: str = "app.log"
    MAX_BYTES: int = 10 * 1024 * 1024  # 10 MB
    BACKUP_COUNT: int = 5
    ENCODING: str = "utf-8"

    def get_log_file(self, path_log: Path) -> Path:
        """
        Retorna o caminho completo do arquivo de log.

        Args:
            path_log: Diretório onde o log será salvo.

        Returns:
            Path completo do arquivo de log.
        """
        return path_log / self.FILENAME

    def configurar(self, path_log: Path) -> None:
        """
        Inicializa o sistema de logging com handler de arquivo (rotativo)
        e handler de console.

        Args:
            path_log: Diretório onde o arquivo de log será salvo.
        """
        # Cria o diretório se não existir
        path_log.mkdir(parents=True, exist_ok=True)

        log_file = self.get_log_file(path_log)

        # Formato
        formatter = log.Formatter(fmt=self.FORMAT, datefmt=self.DATE_FORMAT)

        # Handler → arquivo com rotação
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=self.MAX_BYTES,
            backupCount=self.BACKUP_COUNT,
            encoding=self.ENCODING,
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(self.LEVEL)

        # Handler → console
        console_handler = log.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(self.LEVEL)

        # Logger raiz
        root_logger = log.getLogger()
        root_logger.setLevel(self.LEVEL)
        root_logger.handlers.clear()  # Evita handlers duplicados
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        log.info("Sistema de logging configurado.")
        log.info(f"Arquivo de log: {log_file}")


cfg_log = LoggingConfig()
