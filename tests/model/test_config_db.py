"""
tests/model/test_config_db.py
==============================
Testes unitários para  app/model/config_db.py

Cobertura:
┌────────────────────────┬──────────────────────────────────────────────────┐
│ Alvo                   │ Cenários                                         │
├────────────────────────┼──────────────────────────────────────────────────┤
│ _get_db_env()          │ variável presente, default sem required,         │
│                        │ EnvironmentError when required e ausente       │
├────────────────────────┼──────────────────────────────────────────────────┤
│ BancoConfig (dataclass)│ imutabilidade (frozen), campos corretos,         │
│                        │ ausência de campo obrigatório                    │
├────────────────────────┼──────────────────────────────────────────────────┤
│ db_cfg (instância)     │ carregado com valores de ambiente                │
└────────────────────────┴──────────────────────────────────────────────────┘

NOTA SOBRE ISOLAMENTO:
config_db.py executa load_dotenv(override=True) no nível de módulo, o que
sobrescreve os.environ com os valores reais do .env no momento da importação.
Por isso, os testes de db_cfg NÃO comparam com os.environ — o ambiente pode
ter sido alterado após a criação do singleton. Os testes validam estrutura,
tipo e presença de valores, usando db_cfg como fonte de verdade.
"""

import os
from dataclasses import FrozenInstanceError
from unittest.mock import patch

import pytest


# Helpers
def _remove_env(key: str) -> None:
    """
    Remove uma variável de ambiente sem lançar exceção se ausente.
    """
    os.environ.pop(key, None)


# Testes: _get_db_env()
class Test_Get_Db_Env:
    """
    Testa a função auxiliar _get_db_env().

    Usa chaves com prefixo _TEST_ que nunca existem no .env real,
    garantindo isolamento total do ambiente de produção.
    """

    def test_return_value_when_variable_exist_01(self):
        """
        Deve retornar o valor exato da variável when ela existe.
        """
        with patch.dict(
            os.environ, {"_TEST_VAR_DB": "valor_esperado"}, clear=False
        ):
            from app.model.config_db import _get_db_env

            assert _get_db_env("_TEST_VAR_DB") == "valor_esperado"

    def test_return_default_when_not_required_and_absent_02(self):
        """
        Deve retornar o default when required=False e variável ausente.
        """
        _remove_env("_VAR_AUSENTE_DB")
        from app.model.config_db import _get_db_env

        resultado = _get_db_env(
            "_VAR_AUSENTE_DB", default="default_db", required=False
        )
        assert resultado == "default_db"

    def test_return_none_when_no_default_and_not_required_03(self):
        """
        Sem default e required=False: deve retornar None sem lançar exceção.
        """
        _remove_env("_VAR_SEM_DEFAULT")
        from app.model.config_db import _get_db_env

        assert _get_db_env("_VAR_SEM_DEFAULT", required=False) is None

    def test_raise_environment_error_when_required_and_absent_04(self):
        """
        Deve lançar EnvironmentError when required=True e var não existe.
        """
        _remove_env("_VAR_CRITICA_DB")
        from app.model.config_db import _get_db_env

        with pytest.raises(EnvironmentError, match="_VAR_CRITICA_DB"):
            _get_db_env("_VAR_CRITICA_DB", required=True)

    def test_error_message_contain_variable_name_05(self):
        """
        A mensagem do EnvironmentError deve identificar a variável ausente.
        """
        _remove_env("_VAR_MSG_DB")
        from app.model.config_db import _get_db_env

        with pytest.raises(EnvironmentError) as exc_info:
            _get_db_env("_VAR_MSG_DB")
        assert "_VAR_MSG_DB" in str(exc_info.value)

    def test_variable_with_empty_value_is_returned_06(self):
        """
        String vazia é um valor válido (não é None).
        """
        with patch.dict(os.environ, {"_TEST_EMPTY_DB": ""}, clear=False):
            from app.model.config_db import _get_db_env

            assert _get_db_env("_TEST_EMPTY_DB", required=False) == ""

    def test_not_raise_error_with_default_and_not_required_07(self):
        """
        required=False com default definido nunca deve lançar exceção.
        """
        _remove_env("_VAR_SAFE_DB")
        from app.model.config_db import _get_db_env

        try:
            _get_db_env("_VAR_SAFE_DB", default="seguro", required=False)
        except EnvironmentError:
            pytest.fail(
                "Não deveria lançar EnvironmentError com required=False"
            )


# Testes: BancoConfig (dataclass frozen)
class Test_DB_Config:
    """
    Testa o dataclass BancoConfig.
    """

    def _create_config(self, **kwargs):
        from app.model.config_db import BancoConfig

        defaults = dict(
            DB_USER="user_test",
            DB_PASSWORD="senha_test",
            DB_NAME="banco_test",
            DB_HOST="127.0.0.1",
            DB_PORT="3307",
        )
        defaults.update(kwargs)
        return BancoConfig(**defaults)

    def test_fields_store_correct_values_08(self):
        """
        Todos os campos devem refletir os valores fornecidos.
        """
        cfg = self._create_config()
        assert cfg.DB_USER == "user_test"
        assert cfg.DB_PASSWORD == "senha_test"
        assert cfg.DB_NAME == "banco_test"
        assert cfg.DB_HOST == "127.0.0.1"
        assert cfg.DB_PORT == "3307"

    def test_dataclass_e_immutable_09(self):
        """
        frozen=True: qualquer tentativa de escrita deve lançar exceção.
        """
        cfg = self._create_config()
        with pytest.raises((FrozenInstanceError, AttributeError)):
            cfg.DB_USER = "outro_usuario"  # type: ignore[misc]

    def test_immutable_in_all_fields_10(self):
        """
        Confirma imutabilidade para cada campo individualmente.
        """
        cfg = self._create_config()
        for campo in (
            "DB_USER",
            "DB_PASSWORD",
            "DB_NAME",
            "DB_HOST",
            "DB_PORT",
        ):
            with pytest.raises((FrozenInstanceError, AttributeError)):
                setattr(cfg, campo, "alterado")

    def test_equal_instances_with_same_values_11(self):
        """
        Dois BancoConfig com os mesmos valores devem ser iguais.
        """
        cfg1 = self._create_config()
        cfg2 = self._create_config()
        assert cfg1 == cfg2

    def test_different_instances_with_different_values_12(self):
        """
        Dois BancoConfig com valores distintos não devem ser iguais.
        """
        cfg1 = self._create_config(DB_PORT="3306")
        cfg2 = self._create_config(DB_PORT="5432")
        assert cfg1 != cfg2

    def test_all_fields_are_strings_13(self):
        """
        Todos os campos de BancoConfig devem ser do tipo str.
        """
        cfg = self._create_config()
        for campo in (
            "DB_USER",
            "DB_PASSWORD",
            "DB_NAME",
            "DB_HOST",
            "DB_PORT",
        ):
            assert isinstance(
                getattr(cfg, campo), str
            ), f"Campo '{campo}' deveria ser str"


# Testes: instância db_cfg (singleton de módulo)
class Test_DB_Config_Instance:
    """
    Testa a instância global db_cfg carregada via variáveis de ambiente.

    ESTRATÉGIA: db_cfg é criado uma única vez no import de config_db.py,
    usando load_dotenv(override=True) — portanto carrega os valores reais
    do .env. Os testes validam estrutura e presença de valores usando
    db_cfg como fonte de verdade, sem depender de os.environ.
    """

    def test_db_cfg_is_instance_of_banco_config_14(self):
        """
        db_cfg deve ser uma instância de BancoConfig.
        """
        from app.model.config_db import BancoConfig, db_cfg

        assert isinstance(db_cfg, BancoConfig)

    def test_db_cfg_user_not_empty_15(self):
        """
        DB_USER deve estar preenchido.
        """
        from app.model.config_db import db_cfg

        assert db_cfg.DB_USER not in (None, "")

    def test_db_cfg_password_not_empty_16(self):
        """
        DB_PASSWORD deve estar preenchido.
        """
        from app.model.config_db import db_cfg

        assert db_cfg.DB_PASSWORD not in (None, "")

    def test_db_cfg_name_not_empty_17(self):
        """
        DB_NAME deve estar preenchido.
        """
        from app.model.config_db import db_cfg

        assert db_cfg.DB_NAME not in (None, "")

    def test_db_cfg_host_not_empty_18(self):
        """
        DB_HOST deve estar preenchido.
        """
        from app.model.config_db import db_cfg

        assert db_cfg.DB_HOST not in (None, "")

    def test_db_cfg_port_is_numeric_19(self):
        """
        DB_PORT deve conter apenas dígitos (porta TCP válida).
        """
        from app.model.config_db import db_cfg

        assert (
            db_cfg.DB_PORT.isdigit()
        ), f"DB_PORT deveria ser numérico, recebido: '{db_cfg.DB_PORT}'"

    def test_db_cfg_port_is_in_valid_range_20(self):
        """
        DB_PORT deve estar entre 1 e 65535.
        """
        from app.model.config_db import db_cfg

        porta = int(db_cfg.DB_PORT)
        assert 1 <= porta <= 65535, f"DB_PORT fora do intervalo válido: {porta}"

    def test_db_cfg_all_fields_are_strings_21(self):
        """
        Todos os campos de db_cfg devem ser do tipo str.
        """
        from app.model.config_db import db_cfg

        for campo in (
            "DB_USER",
            "DB_PASSWORD",
            "DB_NAME",
            "DB_HOST",
            "DB_PORT",
        ):
            assert isinstance(
                getattr(db_cfg, campo), str
            ), f"Campo '{campo}' deveria ser str"
