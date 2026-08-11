"""Demo de respx — 6 ideas en un archivo ejecutable.

Corre estos seis comandos EN ESTE ORDEN, desde
`ejercicios/fase-1/f1.testing-pytest/02-mocks-cliente-http/`:

    uv run pytest demo_respx.py -v -k no_mock
    uv run pytest demo_respx.py -v -k with_mock
    uv run pytest demo_respx.py -v -k timeout
    uv run pytest demo_respx.py -v -k spy
    uv run pytest demo_respx.py -v -k param
    uv run pytest demo_respx.py -v -k fixture

Lee los comentarios de cada PARTE antes de correr.
El comando 1 DEBE fallar: ese fallo es el punto de la demo.

Cada herramienta nueva del ejercicio tiene aqui su version ejecutable:
respx (PARTES 1-4), parametrize (PARTE 5) y fixture async (PARTE 6).
Nada del ejercicio te pide sintaxis que no este demostrada en este archivo.

(El archivo no se llama `test_*.py` a proposito: asi `uv run pytest` no lo
recoge junto con tu suite. Solo corre cuando le pasas la ruta explicita.)
"""

from collections.abc import AsyncIterator

import httpx
import pytest
import respx

WEATHER_API = "https://api.example.com"


async def get_temperature(client: httpx.AsyncClient, city: str) -> float:
    """Tiny external-API client: the unit under test."""
    response = await client.get(f"{WEATHER_API}/weather/{city}")
    response.raise_for_status()
    return response.json()["temp_c"]


# =====================================================================
# PARTE 1 — el problema. Este test hace una request DE VERDAD.
# Depende de: que exista internet, que api.example.com este vivo, que hoy
# haga 21 grados. Tres cosas que no controlas. Un test que depende de algo
# que no controlas no es un test: es un reporte del clima.
# Ademas tarda lo que tarde la red, y en CI probablemente ni haya salida.
# =====================================================================


async def test_no_mock_hits_the_real_network() -> None:
    async with httpx.AsyncClient() as client:
        temp = await get_temperature(client, "bogota")
    assert temp == 21.0


# =====================================================================
# PARTE 2 — la solucion. `@respx.mock` instala un transporte falso dentro
# de httpx: la request se construye igual, viaja igual y tu codigo no se
# entera de nada... pero nunca sale de tu maquina.
#
# `respx.get(url).mock(return_value=httpx.Response(...))` dice:
#     "si alguien pide ESTA url, devuelvele ESTA respuesta".
#
# Lo que se mockea es la FRONTERA (el servidor ajeno), nunca tu codigo:
# `get_temperature` corre completa y de verdad, incluido el
# `raise_for_status()` y el parseo del JSON.
# =====================================================================


@respx.mock
async def test_with_mock_returns_the_parsed_temperature() -> None:
    respx.get(f"{WEATHER_API}/weather/bogota").mock(
        return_value=httpx.Response(200, json={"city": "bogota", "temp_c": 21.0})
    )

    async with httpx.AsyncClient() as client:
        temp = await get_temperature(client, "bogota")

    assert temp == 21.0


@respx.mock
async def test_with_mock_raises_on_server_error() -> None:
    # El camino de error es igual de barato de montar que el feliz.
    # Contra un servidor real, provocar un 500 a voluntad es casi imposible.
    respx.get(f"{WEATHER_API}/weather/bogota").mock(
        return_value=httpx.Response(500)
    )

    async with httpx.AsyncClient() as client:
        with pytest.raises(httpx.HTTPStatusError):
            await get_temperature(client, "bogota")


# =====================================================================
# PARTE 3 — `side_effect`: en vez de devolver una respuesta, LANZA.
# Asi simulas lo que ni con un servidor real puedes provocar a voluntad:
# timeouts, conexion caida, DNS roto. Y el test tarda 0 segundos, no 1.0.
#
# `return_value=` -> el servidor contesto (aunque sea con 500).
# `side_effect=`  -> nunca hubo respuesta.
# Esa es exactamente la distincion que te costo dos iteraciones en la S9.
# =====================================================================


@respx.mock
async def test_timeout_is_simulated_without_waiting() -> None:
    respx.get(f"{WEATHER_API}/weather/bogota").mock(
        side_effect=httpx.ReadTimeout("too slow")
    )

    async with httpx.AsyncClient(timeout=1.0) as client:
        with pytest.raises(httpx.TimeoutException):
            await get_temperature(client, "bogota")


# =====================================================================
# PARTE 4 — el mock tambien es un ESPIA. La ruta recuerda si la llamaron,
# cuantas veces y con que. Sirve para afirmar sobre lo que tu codigo HIZO,
# no solo sobre lo que devolvio (p. ej. "no repitio la llamada", "mando el
# header de auth"). Si nadie la llama, `route.called` es False y ahi ves
# que tu codigo ni siquiera fue a donde creias.
# =====================================================================


@respx.mock
async def test_spy_records_the_outgoing_request() -> None:
    route = respx.get(f"{WEATHER_API}/weather/bogota").mock(
        return_value=httpx.Response(200, json={"temp_c": 21.0})
    )

    async with httpx.AsyncClient() as client:
        await get_temperature(client, "bogota")

    assert route.called
    assert route.call_count == 1
    assert route.calls.last.request.url.path == "/weather/bogota"


# =====================================================================
# PARTE 5 — `parametrize`: UN test, varios juegos de datos.
# Tres tests copiados y pegados que solo cambian en un numero no son tres
# tests: son uno con tres datos. Y si manana hay que cubrir un cuarto caso,
# quieres tocar una lista, no crear otra funcion.
#
# Las tres piezas:
#   1. el string nombra los parametros            -> "value, expected"
#   2. la lista trae una entrada por ejecucion    -> [(2, 4), (3, 9)]
#      (con UN solo parametro va la lista pelada  -> [400, 404, 500])
#   3. esos nombres entran en la FIRMA de la funcion, igual que una fixture
#
# pytest reporta un caso por entrada: test_param_square[2-4], [3-9], [4-16].
# =====================================================================


@pytest.mark.parametrize("value, expected", [(2, 4), (3, 9), (4, 16)])
def test_param_square(value: int, expected: int) -> None:
    assert value**2 == expected


# Combinado con respx. ORDEN DE DECORADORES: `@respx.mock` va ARRIBA de
# `@pytest.mark.parametrize`. Y la firma lleva las dos cosas: el parametro
# del parametrize Y (mas abajo, en la PARTE 6) las fixtures que pidas.
# Lo unico que cambia entre las tres corridas es el `status`.


@respx.mock
@pytest.mark.parametrize("status", [401, 403, 500])
async def test_param_raises_on_every_error_status(status: int) -> None:
    respx.get(f"{WEATHER_API}/weather/bogota").mock(
        return_value=httpx.Response(status)
    )

    async with httpx.AsyncClient() as client:
        with pytest.raises(httpx.HTTPStatusError):
            await get_temperature(client, "bogota")


# =====================================================================
# PARTE 6 — fixture ASYNC. Igual que la de ayer (yield = setup/teardown),
# con dos diferencias:
#   - es `async def`, porque adentro hay un `async with` (y `async with` es
#     una forma de await: solo existe dentro de una corrutina).
#   - el tipo de retorno es `AsyncIterator[...]`, no el objeto: la funcion
#     no DEVUELVE un cliente, lo PRODUCE y luego sigue.
#
# OJO al `yield`: la fixture entrega al test *lo que va despues del yield*.
# Un `yield` pelado entrega None, igual que un `return` pelado. El teardown
# aqui es implicito: al salir del `async with`, el cliente se cierra solo.
#
# (En tu ejercicio esta fixture va en `conftest.py`, no en el archivo de
# tests; aqui esta en el mismo archivo solo para que la demo sea autonoma.)
# =====================================================================


@pytest.fixture
async def demo_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(timeout=1.0) as http_client:
        yield http_client


@respx.mock
async def test_fixture_client_is_injected_by_name(
    demo_client: httpx.AsyncClient,
) -> None:
    # El test PIDE la fixture declarandola como parametro con su mismo nombre.
    # No es una variable global: si no la pones en la firma -> NameError.
    respx.get(f"{WEATHER_API}/weather/bogota").mock(
        return_value=httpx.Response(200, json={"temp_c": 21.0})
    )

    assert await get_temperature(demo_client, "bogota") == 21.0
