"""Tests de los modelos anidados.

Mecanica de pytest (lo minimo que necesitas hoy):
- Un test es una funcion cuyo nombre empieza con `test_`. pytest las
  encuentra y las corre todas.
- Dentro, `assert <condicion>` — si la condicion es False, el test falla.
- Para verificar que algo LANZA un error se usa el bloque
  `with pytest.raises(TipoDeError):` — el test PASA si el error ocurre,
  y FALLA si no ocurre.

Corre con:  python3 -m pytest test_model.py -v
"""

from pathlib import Path

import pytest
from pydantic import ValidationError

from model import AsistenteConfig, Herramienta, ModelConfig

# Ruta al datos.json (relativa a ESTE archivo, no al directorio donde corras pytest)
DATOS = Path(__file__).parent / "datos.json"


# ---------- EJEMPLO RESUELTO 1: caso valido ----------
def test_carga_datos_json():
    """Test 1: datos.json completo se valida y coerciona bien."""
    config = AsistenteConfig.model_validate_json(DATOS.read_text())

    assert config.nombre == "asistente-docs"
    # OJO: en el JSON temperatura venia como string "0.3" — ¿que es aqui?
    assert config.modelo.temperatura == 0.3
    # La herramienta leer_archivo no traia timeout_s → default
    assert config.herramientas[1].timeout_s == 30.0


# ---------- EJEMPLO RESUELTO 2: caso invalido ----------
def test_timeout_fuera_de_rango():
    """Test 3: timeout_s > 120 debe ser rechazado."""
    with pytest.raises(ValidationError):
        Herramienta(
            nombre="lenta",
            descripcion="una herramienta demasiado lenta",
            timeout_s=999,
        )


# ---------- TU TRABAJO: completa los 6 que faltan ----------

def test_roundtrip_dump_y_validate():
    """Test 2: construir un AsistenteConfig valido, hacer model_dump_json(),
    volver a validar ese string con model_validate_json, y assert de que
    el resultado == el original."""

    original = AsistenteConfig(
        nombre="asistente-x",
        modelo=ModelConfig(modelo="claude-opus"),
    )

    texto = original.model_dump_json()


    reconstruido = AsistenteConfig.model_validate_json(texto)

    assert reconstruido == original



def test_herramientas_duplicadas():
    """Test 4: dos herramientas con el mismo nombre → ValidationError.
    Extra: verifica que el mensaje menciona el nombre duplicado.
    Pista: `with pytest.raises(ValidationError, match="buscar_docs"):`"""
    with pytest.raises(ValidationError, match="tool1"):
        herramienta1 = Herramienta(nombre='tool1',descripcion="test de herramienta1")
        herramienta2 = Herramienta(nombre='tool1',descripcion="test de herramienta2")

        AsistenteConfig(
            nombre="agente-duplicadas",
            modelo=ModelConfig(modelo="claude-opus"),
            herramientas=[herramienta1, herramienta2]
        )




def test_loc_de_error_anidado():
    """Test 5 — EL VEREDICTO DE TU P1: temperatura invalida DENTRO de
    modelo → verifica el loc del error.
    Estructura:
        with pytest.raises(ValidationError) as exc_info:
            ...construir AsistenteConfig con modelo.temperatura mala...
        assert exc_info.value.errors()[0]["loc"] == (TU_PREDICCION)
    """
    with pytest.raises(ValidationError) as exc_info:
        AsistenteConfig(
            nombre="asistente-x",
            modelo={"modelo": "claude-opus", "temperatura": 3.0},
        )


    assert exc_info.value.errors()[0]["loc"] == ("modelo","temperatura")


def test_descripcion_corta():
    """Test 6: descripcion de menos de 10 caracteres → ValidationError."""
    with pytest.raises(ValidationError):
        Herramienta(
            nombre="descripcion-corta",
            descripcion="corta",
            timeout_s=2
        )



def test_dos_errores_a_la_vez():
    """Test 7: dos campos malos en el MISMO intento → UN ValidationError
    con 2 errores dentro. Pista: exc_info.value.error_count()"""
    with pytest.raises(ValidationError) as exc_info:
        Herramienta(
            nombre="corta-lenta",
            descripcion="corta",
            timeout_s=999,
        )

    assert exc_info.value.error_count() == 2


def test_agente_sin_herramientas():
    """Test 8: nombre "agente-..." con herramientas vacia → ValidationError
    (tu Regla 2)."""
    with pytest.raises(ValidationError):
        AsistenteConfig(
            nombre="agente-sinherramientas",
            modelo=ModelConfig(modelo="claude-opus")
        )
