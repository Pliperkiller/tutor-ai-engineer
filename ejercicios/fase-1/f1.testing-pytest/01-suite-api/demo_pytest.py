"""Demo de pytest — 3 ideas en un archivo ejecutable.

Corre estos tres comandos EN ESTE ORDEN, desde
`ejercicios/fase-1/f1.apis-rest-fastapi/01-registro-modelos/`:

    uv run pytest ../../f1.testing-pytest/01-suite-api/demo_pytest.py -v
    uv run pytest ../../f1.testing-pytest/01-suite-api/demo_pytest.py -v -k leaky_b
    uv run pytest ../../f1.testing-pytest/01-suite-api/demo_pytest.py -v -k clean_b

Lee los comentarios de cada PARTE antes de correr. El comando 2 debe fallar:
ese fallo es el punto de la demo.
"""

import pytest

# =====================================================================
# PARTE 1 — un test es una funcion `test_*` con un `assert` pelado.
# No hay clases obligatorias, no hay assertEqual, no hay API que memorizar.
# pytest reescribe el assert para mostrarte los dos lados cuando falla.
# =====================================================================


def add(a: int, b: int) -> int:
    return a + b


def test_add_returns_the_sum() -> None:
    assert add(2, 3) == 5


def test_add_raises_on_strings() -> None:
    # Un test tambien verifica el contrato de ERROR, no solo el camino feliz.
    with pytest.raises(TypeError):
        add(2, "3")  # type: ignore[arg-type]
    # OJO (esto ya te mordio en la sesion 7): cualquier linea que pongas
    # DENTRO del `with` despues de la que revienta NUNCA se ejecuta.
    # Los asserts sobre el resultado van FUERA del bloque.


# =====================================================================
# PARTE 2 — el problema que hace existir a las fixtures: estado compartido.
# STORE vive en el modulo, no en cada test. El primer test lo ensucia y el
# segundo pasa apoyado en esa suciedad, no por su propio merito.
# =====================================================================

STORE: dict[int, str] = {1: "a"}


def test_leaky_a_adds_an_item() -> None:
    STORE[2] = "b"
    assert len(STORE) == 2


def test_leaky_b_counts_items() -> None:
    # Verde si corres el archivo completo. ROJO si corres solo este test.
    # Un test que depende del orden no prueba tu codigo: prueba tu suerte.
    assert len(STORE) == 2


# =====================================================================
# PARTE 3 — la solucion: una fixture con `yield`.
# Lo que esta ARRIBA del yield corre antes de cada test; lo de ABAJO corre
# despues, pase o falle el test (es el teardown). `autouse=True` la aplica
# a todos los tests del archivo sin que ninguno tenga que pedirla.
# =====================================================================

CLEAN_STORE: dict[int, str] = {1: "a"}


@pytest.fixture(autouse=True)
def reset_clean_store():
    original = CLEAN_STORE.copy()
    yield
    CLEAN_STORE.clear()
    CLEAN_STORE.update(original)


def test_clean_a_adds_an_item() -> None:
    CLEAN_STORE[2] = "b"
    assert len(CLEAN_STORE) == 2


def test_clean_b_counts_items() -> None:
    # Verde solo o acompanado: la fixture le devolvio el estado inicial.
    assert len(CLEAN_STORE) == 1
