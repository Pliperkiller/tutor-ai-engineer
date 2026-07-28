"""RunConfig: configuración tipada de una llamada a un modelo."""

from dataclasses import dataclass


class ConfigError(Exception):
    """Se lanza cuando una RunConfig tiene valores fuera de rango."""


@dataclass
class RunConfig:
    """Configuración de una llamada a un modelo."""

    modelo: str
    temperatura: float
    max_tokens: int = 1024
    stream: bool = False

    def __post_init__(self) -> None:
        if not (0.0 <= self.temperatura <= 2.0):
            raise ConfigError(f"temperatura fuera de rango [0, 2]: {self.temperatura}")
        if self.max_tokens <= 0:
            raise ConfigError(f"max_tokens debe ser > 0: {self.max_tokens}")
