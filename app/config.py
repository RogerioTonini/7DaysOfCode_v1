"""
Configurações do projeto usando dataclass
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Final


@dataclass(frozen=True)
class ArquivoConfig:
    """Configurações de formatos de arquivo"""
    SEP_CSV: str = ','
    EXT_CSV: str = 'csv'
    EXT_EXCEL: str = 'xlsx'
    EXT_JSON: str = 'json'
    EXT_PARQUET: str = 'parquet'
    PREFIXO_ARQ_CSV: str = 'emprestimos-'


@dataclass(frozen=True)
class BancoDadosConfig:
    """Configurações de bancos de dados"""
    DB_EMPR_BRONZE: str = 'DB_Empr_Bronze'
    DB_EMPR_SILVER: str = 'DB_Empr_Silver'
    DB_EMPR_SILVER_V2: str = 'DB_Empr_Silver_V2'
    DB_EMPR_GOLD: str = 'DB_Empr_Gold'
    DB_EMPR_DATA: str = 'DB_Empr_Data'
    DB_EMPR_ANO: str = 'DB_Empr_Ano'
    DB_EMPR_MES: str = 'DB_Empr_Mes'
    DB_EMPR_HORA: str = 'DB_Empr_Hora'
    DB_EMPR_DUPLICADOS: str = 'DB_Empr_Duplicados'
    DB_EMPR_INCONSISTENTE: str = 'DB_Empr_Inconsistente'
    DB_EMPR_PERDIDOS: str = 'DB_Empr_Perdidos'


@dataclass(frozen=True)
class CaminhosConfig:
    """Configurações de caminhos e URLs"""
    PATH_BASE: Path = Path('C:/Users/[Usuario]/OneDrive/Git-Dados/7DaysOfCode')
    URL_CSV: str = 'https://github.com/FranciscoFoz/7_Days_of_Code_Alura-Python-Pandas/...'
    URL_PARQUET: str = 'https://github.com/FranciscoFoz/7_Days_of_Code_Alura-Python-Pandas/...'
    URL_EXCEL: str = 'https://github.com/FranciscoFoz/7_Days_of_Code_Alura-Python-Pandas/...'


@dataclass(frozen=True)
class ParametrosConfig:
    """Parâmetros gerais do sistema"""
    ANO_INICIAL: int = 2010
    ANO_FINAL: int = 2021
    ANOS_POR_ANO: int = 2


@dataclass(frozen=True)
class Config:
    """
    Configuração centralizada do projeto

    Attributes:
        arquivo: Configurações de arquivos
        banco: Configurações de banco de dados
        caminhos: Configurações de caminhos
        parametros: Parâmetros do sistema
    """
    arquivo: ArquivoConfig = ArquivoConfig()
    banco: BancoDadosConfig = BancoDadosConfig()
    caminhos: CaminhosConfig = CaminhosConfig()
    parametros: ParametrosConfig = ParametrosConfig()


# Instância global (singleton pattern)
config = Config()
