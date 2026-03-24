"""
Configurações e esquema da tabela tb_CDU.

Localização: app/model/cdu/config_cdu.py
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class NomesTabelaCDUConfig:
    """
    Nomes da tabela CDU e prefixo de backup.
    """

    TABELA: str = "tb_CDU"
    BKP_PREFIX: str = "tb_CDU_bkp_"  # + {YYYYMMDD_HHMMSS}


@dataclass(frozen=True)
class EsquemaCDUConfig:
    """
    Esquema de colunas da tabela tb_CDU.

    Colunas:
        num_index      → INT AUTO_INCREMENT PRIMARY KEY (gerado pelo banco)
        id_faixa_cdu   → INT (inicia em 1)
        inicio_faixa   → INT
        fim_faixa      → INT
        nome_faixa_cdu → VARCHAR(70)

    Chave de comparação : id_faixa_cdu + inicio_faixa + fim_faixa
    Campo atualizável   : nome_faixa_cdu
    """

    ARQUIVO_CSV: str = "DB_CDU"

    COLUNAS: tuple = (
        "id_faixa_cdu",
        "inicio_faixa",
        "fim_faixa",
        "nome_faixa_cdu",
    )

    TIPOS_COLUNA: tuple = (
        ("id_faixa_cdu", "INT"),
        ("inicio_faixa", "INT"),
        ("fim_faixa", "INT"),
        ("nome_faixa_cdu", "VARCHAR(70)"),
    )

    CHAVE_COMPARACAO: tuple = (
        "id_faixa_cdu",
        "inicio_faixa",
        "fim_faixa",
    )

    CAMPO_ATUALIZAVEL: str = "nome_faixa_cdu"

    def as_dict(self) -> dict:
        """
        Retorna esquema como dicionário {coluna: tipo}.
        """
        return dict(self.TIPOS_COLUNA)


@dataclass(frozen=True)
class CDUConfig:
    """
    Configuração centralizada da tabela CDU.
    """

    tabela: NomesTabelaCDUConfig = field(default_factory=NomesTabelaCDUConfig)
    esquema: EsquemaCDUConfig = field(default_factory=EsquemaCDUConfig)


cfg_cdu = CDUConfig()
