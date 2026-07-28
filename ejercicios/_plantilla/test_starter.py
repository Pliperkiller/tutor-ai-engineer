"""El tutor ejecuta: pytest test_starter.py -q"""
from starter import funcion_objetivo


def test_caso_base():
    assert funcion_objetivo("<entrada>") == "<salida esperada>"
