"""Demo: que ES una fixture y CUANDO corre cada linea.

Corre desde `ejercicios/fase-1/f1.apis-rest-fastapi/01-registro-modelos/`:

    uv run pytest ../../f1.testing-pytest/01-suite-api/demo_fixture_orden.py -v -s

El flag `-s` deja pasar los print (sin el, pytest los captura y no ves nada).
Lee la salida de arriba a abajo: ese orden ES la respuesta a tu pregunta.
"""

import pytest


@pytest.fixture
def toolbox():
    print("\n  [1] fixture: preparo la caja de herramientas")
    box = {"hammer": 1}

    yield box  # <-- la fixture se PAUSA aqui y corre el test, con box en la mano

    print("  [3] fixture: guardo y limpio la caja")
    box.clear()


def test_uses_the_box(toolbox):  # <-- pedir la fixture = ponerla de parametro
    print("  [2] test: recibi la caja y tiene", toolbox)
    assert toolbox["hammer"] == 1


def test_gets_a_fresh_box(toolbox):
    # El test anterior dejo la caja vacia (box.clear()). Y sin embargo esta
    # llega llena: la fixture no se reutiliza, corre COMPLETA otra vez.
    print("  [2] test: mi caja llego nueva:", toolbox)
    assert toolbox == {"hammer": 1}
