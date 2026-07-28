"""El tutor ejecuta: pytest test_starter.py -q"""
import pytest

from starter import ConfigError, RunConfig


def test_construccion_valida():
    c = RunConfig(modelo="opus", temperatura=0.7)
    assert c.modelo == "opus"
    assert c.temperatura == 0.7


def test_defaults():
    c = RunConfig(modelo="opus", temperatura=0.7)
    assert c.max_tokens == 1024
    assert c.stream is False


def test_igualdad_por_valor():
    a = RunConfig(modelo="opus", temperatura=0.7)
    b = RunConfig(modelo="opus", temperatura=0.7)
    assert a == b


def test_temperatura_fuera_de_rango_lanza():
    with pytest.raises(ConfigError):
        RunConfig(modelo="opus", temperatura=3.0)


def test_max_tokens_no_positivo_lanza():
    with pytest.raises(ConfigError):
        RunConfig(modelo="opus", temperatura=0.7, max_tokens=0)
