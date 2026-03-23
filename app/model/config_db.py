import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# ─── Caminho corrigido: sobe 3 níveis (model → app → 7DayOfCode → Config) ────
_env_path: Path = (
    Path(__file__).resolve().parent.parent.parent / "Config" / ".env"
)
load_dotenv(dotenv_path=_env_path, override=True)


@dataclass(frozen=True)
class BancoConfig:
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: str


def _get_db_env(key: str, default: str = None, required: bool = True) -> str:
    """Lê variável de ambiente do banco com validação."""
    value = os.getenv(key, default)
    if required and value is None:
        raise EnvironmentError(
            f"[config_db.py] Variável obrigatória não encontrada: '{key}'\n"
            f"Verifique o arquivo: {_env_path}"
        )
    return value


db_cfg: BancoConfig = BancoConfig(
    DB_USER=_get_db_env("DB_USER"),
    DB_PASSWORD=_get_db_env("DB_PASSWORD"),
    DB_NAME=_get_db_env("DB_NAME"),
    DB_HOST=_get_db_env("DB_HOST", default="localhost"),
    DB_PORT=_get_db_env("DB_PORT", default="3306"),
)
