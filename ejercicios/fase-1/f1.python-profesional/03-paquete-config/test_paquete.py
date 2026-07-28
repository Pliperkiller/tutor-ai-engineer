"""El tutor ejecuta: pytest test_paquete.py -q"""
import pytest

from aiconfig import ConfigError, RunConfig, TagError, parse_tags


def test_parse_tags_feliz():
    assert parse_tags("modelo=opus, temp=0.7") == {"modelo": "opus", "temp": "0.7"}


def test_parse_tags_error():
    with pytest.raises(TagError):
        parse_tags("modelo")


def test_runconfig_valida():
    c = RunConfig(modelo="opus", temperatura=0.7)
    assert c.max_tokens == 1024
    assert c.stream is False


def test_runconfig_error():
    with pytest.raises(ConfigError):
        RunConfig(modelo="opus", temperatura=5.0)
