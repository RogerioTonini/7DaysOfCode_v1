"""
Configurações e esquemas das tabelas de empréstimos.

Responsabilidade: definir constantes de colunas e nomes de tabelas
para todas as camadas do padrão medalhão.

Localização: app/model/config_emprestimos.py

Camadas:
    RAW    → dados brutos sem tratamento
    Bronze → dados com tipagem e limpeza básica
    Silver → dados normalizados e enriquecidos
    Gold   → dados agregados para análise
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class NomesTabelasConfig:
    """Nomes das tabelas por camada medalhão."""

    # RAW
    RAW: str = "tb_emprestimos_raw"
    RAW_BKP_PREFIX: str = "tb_emprestimos_raw_bkp_"  # + {YYYYMMDD_HHMMSS}
    BRONZE: str = "tb_emprestimos_bronze"
    SILVER: str = "tb_emprestimos_silver"
    GOLD: str = "tb_emprestimos_gold"


@dataclass(frozen=True)
class EsquemaRAWConfig:
    """
    Esquema de colunas da tabela RAW.
    Todas as colunas são VARCHAR(255) — dados brutos sem tratamento.
    """

    COLUNAS: tuple = (
        "id_emprestimo",
        "codigo_barras",
        "data_renovacao",
        "data_emprestimo",
        "data_devolucao",
        "matricula_ou_siape",
        "tipo_vinculo_usuario",
        # "id_exemplar",
        # "colecao",
        # "biblioteca",
        # "status_material",
        # "Nome_Faixa_CDU",
    )

    TIPO_COLUNA: str = "VARCHAR(255)"

    def as_dict(self) -> dict:
        """
        Retorna o esquema como dicionário {coluna: tipo}.
        """
        return {col: self.TIPO_COLUNA for col in self.COLUNAS}


# ─── Esquema Bronze (próximas etapas) ─────────────────────────────────────────
# @dataclass(frozen=True)
# class EsquemaBronzeConfig:
#     ...


# ─── Esquema Silver (próximas etapas) ─────────────────────────────────────────
# @dataclass(frozen=True)
# class EsquemaSilverConfig:
#     ...


# ─── Esquema Gold (próximas etapas) ───────────────────────────────────────────
# @dataclass(frozen=True)
# class EsquemaGoldConfig:
#     ...


@dataclass(frozen=True)
class EmprestimosConfig:
    """
    Configuração centralizada de todas as camadas de empréstimos.
    """

    tabelas: NomesTabelasConfig = NomesTabelasConfig()
    esquema_raw: EsquemaRAWConfig = EsquemaRAWConfig()

    # Próximas etapas:
    # esquema_bronze: EsquemaBronzeConfig = EsquemaBronzeConfig()
    # esquema_silver: EsquemaSilverConfig = EsquemaSilverConfig()
    # esquema_gold:   EsquemaGoldConfig   = EsquemaGoldConfig()


cfg_emprestimos = EmprestimosConfig()
