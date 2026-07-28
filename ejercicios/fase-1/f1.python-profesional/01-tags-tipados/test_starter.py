"""El tutor ejecuta: pytest test_starter.py -q"""
import pytest

from starter import TagError, parse_tags


def test_caso_feliz():
    assert parse_tags("modelo=opus, temp=0.7") == {"modelo": "opus", "temp": "0.7"}


def test_ignora_espacios():
    assert parse_tags("  modelo =  opus ,  stream= true ") == {
        "modelo": "opus",
        "stream": "true",
    }


def test_ignora_par_vacio_final():
    assert parse_tags("a=1,") == {"a": "1"}


def test_par_sin_igual_lanza_tagerror():
    with pytest.raises(TagError):
        parse_tags("modelo=opus, temperatura")
