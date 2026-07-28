"""Paquete aiconfig — utilidades de configuración tipada.

TODO: exporta la API pública del paquete para que ESTE import funcione desde
fuera del paquete (es justo lo que hace el test):

    from aiconfig import parse_tags, TagError, RunConfig, ConfigError

Pista 1: usa imports RELATIVOS desde los módulos internos (tags.py, config.py).
Pista 2: cuando corras ruff, verás que se queja de esos imports. Investiga qué
         es `__all__` y por qué silencia esa queja en un __init__.py.
"""
# TODO: tus imports (y __all__) aquí.

from .config import ConfigError, RunConfig
from .tags import TagError, parse_tags

__all__ = ["ConfigError", "RunConfig", "TagError", "parse_tags"]
