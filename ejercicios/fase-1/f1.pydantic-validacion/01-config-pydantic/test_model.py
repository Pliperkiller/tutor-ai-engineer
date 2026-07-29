"""Especificación ejecutable de ModelConfig. NO modificar."""

import pytest
from pydantic import ValidationError

from model import ModelConfig


def test_construccion_valida():
    cfg = ModelConfig(modelo="claude-opus-5", temperatura=0.2, max_tokens=2048)
    assert cfg.modelo == "claude-opus-5"
    assert cfg.temperatura == 0.2
    assert cfg.max_tokens == 2048


def test_defaults():
    cfg = ModelConfig(modelo="claude-sonnet-5")
    assert cfg.temperatura == 0.7
    assert cfg.max_tokens == 1024


def test_coercion_desde_json():
    # Así llega un payload real: todo son strings
    crudo = {"modelo": "claude-sonnet-5", "temperatura": "0.2", "max_tokens": "2048"}
    cfg = ModelConfig.model_validate(crudo)
    assert isinstance(cfg.temperatura, float)
    assert isinstance(cfg.max_tokens, int)


def test_temperatura_fuera_de_rango():
    with pytest.raises(ValidationError):
        ModelConfig(modelo="claude-opus-5", temperatura=1.5)


def test_modelo_no_claude():
    with pytest.raises(ValidationError):
        ModelConfig(modelo="gpt-4")


def test_errores_multiples_de_una_vez():
    # Tres campos rotos -> UN solo ValidationError con los 3 reportados
    with pytest.raises(ValidationError) as exc_info:
        ModelConfig.model_validate(
            {"modelo": "gpt-4", "temperatura": 3.0, "max_tokens": -5}
        )
    assert exc_info.value.error_count() == 3
