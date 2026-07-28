"""f1.python-profesional · 02 — RunConfig: dataclass tipada con validación.

Completa los TODO. No cambies los nombres de la clase, los campos ni la
excepción: el test los importa tal cual.
"""

from dataclasses import dataclass


class ConfigError(Exception):
    """Se lanza cuando una RunConfig tiene valores fuera de rango."""


@dataclass
class RunConfig:
    """Configuración de una llamada a un modelo.

    Campos:
    - modelo: str            (obligatorio)
    - temperatura: float     (obligatorio)
    - max_tokens: int        (default 1024)
    - stream: bool           (default False)

    Validación (en __post_init__):
    - 0.0 <= temperatura <= 2.0, si no -> ConfigError
    - max_tokens > 0,            si no -> ConfigError
    """

    # TODO 1: declara los 4 campos tipados, respetando el orden
    #         (los que tienen default van al final).

    modelo: str
    temperatura: float
    max_tokens: int = 1024
    stream: bool = False

    def __post_init__(self) -> None:
        # TODO 2: valida temperatura y max_tokens. Lanza ConfigError con un
        #         mensaje claro si algún valor está fuera de rango.
        if self.temperatura < 0.0 or self.temperatura > 2.0:
            raise ConfigError(f"El valor de temperatura es {self.temperatura} y esta fuera del rango 0.0 - 2.0")
       
        if self.max_tokens <= 0:
            raise ConfigError(f"El valor de max_tokens es menor a 0")

        
