"""
Configurações gerais do projeto.

Responsabilidade: parâmetros de aplicação, arquivos, caminhos, URLs e Pandas.
Logging   → app/utils/config_log.py
Banco     → app/model/config_db.py
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

_env_path: Path = Path(__file__).resolve().parent.parent / "Config" / ".env"
load_dotenv(dotenv_path=_env_path, override=True)


@dataclass(frozen=True)
class AppConfig:
    """Parâmetros gerais da aplicação."""

    DEBUG: bool
    LOG_LEVEL: str


def _get_env(key: str, default: str = None, required: bool = True) -> str:
    """Lê variável de ambiente com validação."""
    value = os.getenv(key, default)
    if required and value is None:
        raise EnvironmentError(
            f"[config.py] Variável obrigatória não encontrada: '{key}'\n"
            f"Verifique o arquivo: {_env_path}"
        )
    return value


@dataclass(frozen=True)
class PandasConfig:
    """Configurações de exibição do Pandas."""

    MAX_ROWS: int = 10_000
    MAX_COLUMNS: int = 30
    DISPLAY_WIDTH: int | None = None
    FLOAT_FORMAT: str = "{:.2f}"

    def aplicar(self) -> None:
        """Aplica as configurações ao Pandas."""
        pd.set_option("display.max_rows", self.MAX_ROWS)
        pd.set_option("display.max_columns", self.MAX_COLUMNS)
        pd.set_option("display.width", self.DISPLAY_WIDTH)
        pd.set_option("display.float_format", self.FLOAT_FORMAT.format)
        pd.set_option("display.precision", 2)

    def resetar(self) -> None:
        """Reseta configurações para o padrão do Pandas."""
        pd.reset_option("display.max_rows")
        pd.reset_option("display.max_columns")
        pd.reset_option("display.width")
        pd.reset_option("display.float_format")


@dataclass(frozen=True)
class ArquivoConfig:
    """Configurações de formatos de arquivo."""

    SEP_CSV: str = ","
    EXT_CSV: str = "csv"
    EXT_EXCEL: str = "xlsx"
    EXT_JSON: str = "json"
    EXT_PARQUET: str = "parquet"
    PREFIXO_ARQ_CSV: str = "emprestimos-"


@dataclass(frozen=True)
class BancoDadosConfig:
    """Nomes das tabelas no padrão medalhão."""

    TB_EMPRESTIMOS_RAW: str = "tb_emprestimos_raw"
    DB_EMPR_BRONZE: str = "DB_Empr_Bronze"
    DB_EMPR_SILVER: str = "DB_Empr_Silver"
    DB_EMPR_SILVER_V2: str = "DB_Empr_Silver_V2"
    DB_EMPR_GOLD: str = "DB_Empr_Gold"
    DB_EMPR_DATA: str = "DB_Empr_Data"
    DB_EMPR_ANO: str = "DB_Empr_Ano"
    DB_EMPR_MES: str = "DB_Empr_Mes"
    DB_EMPR_HORA: str = "DB_Empr_Hora"
    DB_EMPR_DUPLICADOS: str = "DB_Empr_Duplicados"
    DB_EMPR_INCONSISTENTE: str = "DB_Empr_Inconsistente"
    DB_EMPR_PERDIDOS: str = "DB_Empr_Perdidos"



@dataclass(frozen=True)
class CaminhosConfig:
    """Configurações de caminhos locais e URLs externas."""

    PATH_DATA: Path = field(
        default_factory=lambda: Path(
            os.getenv(
                "DATA_PATH",
                "C:/Users/rtoni/OneDrive/Git-Dados/7DaysOfCode/data",
            )
        )
    )
    PATH_LOG: Path = field(
        default_factory=lambda: Path(
            os.getenv(
                "LOGS_PATH", "C:/Users/rtoni/OneDrive/Git-Dados/7DaysOfCode/log"
            )
        )
    )
    URL_CSV: str = (
        "https://github.com/FranciscoFoz/7_Days_of_Code_Alura-Python-Pandas/"
        "blob/main/Dia_1-Importando_dados/Datasets/dados_emprestimos/"
    )
    URL_PARQUET: str = (
        "https://github.com/FranciscoFoz/7_Days_of_Code_Alura-Python-Pandas/"
        "raw/main/Dia_1-Importando_dados/Datasets/dados_exemplares.parquet"
    )
    URL_EXCEL: str = (
        "https://github.com/FranciscoFoz/7_Days_of_Code_Alura-Python-Pandas/"
        "blob/raw/Dia_6-Novos_dados_novas_analises/Datasets/matricula_alunos.xlsx"
    )


@dataclass(frozen=True)
class ParametrosConfig:
    """Parâmetros de negócio do sistema."""

    ANO_INICIAL: int = 2010
    ANO_FINAL: int = 2021
    QTD_REG_LOTE: int = 1000


@dataclass(frozen=True)
class Config:
    """
    Configuração centralizada do projeto.

    Logging → app/utils/config_log.py
    Banco   → app/model/config_db.py
    """

    app: AppConfig = field(
        default_factory=lambda: AppConfig(
            DEBUG=_get_env("DEBUG", "False").lower() == "true",
            LOG_LEVEL=_get_env("LOG_LEVEL", "INFO", required=False),
        )
    )

    arquivo: ArquivoConfig = field(default_factory=ArquivoConfig)
    banco_tabelas: BancoDadosConfig = field(default_factory=BancoDadosConfig)
    caminhos: CaminhosConfig = field(default_factory=CaminhosConfig)
    parametros: ParametrosConfig = field(default_factory=ParametrosConfig)
    pandas_cfg: PandasConfig = field(default_factory=PandasConfig)


cfg_app = Config()
