# f1.testing-pytest · 02 — Mocks de una API externa

- Herramientas: `respx` + `pytest-asyncio` + `pytest-cov`
- Tipo: script + predecir
- Tiempo objetivo: 12 min
- Directorio de trabajo: **esta misma carpeta**
  (`ejercicios/fase-1/f1.testing-pytest/02-mocks-cliente-http/`)

## Por qué esta herramienta

En la sesión 9 verificaste tu cliente robusto con tres experimentos manuales:
levantar `flaky_server.py`, apuntar a un puerto muerto, e inyectar un
`ValueError` a mano. Funcionó, pero: tuviste que levantar un servidor en otra
terminal, esperar ~1.1s reales por los timeouts, y editar el código fuente para
provocar el tercer caso. Nada de eso se repite solo.

El problema de fondo es que tu cliente habla con **algo que no controlas**. Un
test que depende de un servidor ajeno no prueba tu código: prueba la red. Y hay
casos que contra un servidor real son casi imposibles de provocar a voluntad —
un 500, un DNS caído, un timeout exacto.

`respx` reemplaza el **transporte** de httpx por uno falso. Tu código construye
la request igual, la `await`ea igual, `raise_for_status()` corre igual y el JSON
se parsea igual — pero la request nunca sale de tu máquina. Se mockea la
frontera (el servidor ajeno), **jamás tu propio código**.

Antes se hacía con `unittest.mock.patch` sobre el método del cliente: eso
sustituye TU código y deja de probar lo que te importa (el manejo de errores).
`respx` se mete un nivel más abajo, en la salida real.

## Objetivo

Una suite de pytest que cubra los caminos feliz y de error de tu cliente HTTP
sin levantar ningún servidor, con una fixture, `parametrize`, y un reporte de
cobertura que sepas interpretar.

## Paso a paso

0. **Preparación** — todo ocurre en esta carpeta. Desde aquí:

   ```bash
   uv init --bare
   uv add httpx
   uv add --dev pytest respx pytest-asyncio pytest-cov
   ```

   Copia tu cliente de la sesión 9 a esta carpeta:

   ```bash
   # bash
   cp ../../f1.async-basico/02-cliente-robusto/robust_client.py .
   ```
   ```powershell
   # PowerShell
   Copy-Item ..\..\f1.async-basico\02-cliente-robusto\robust_client.py .
   ```

   Y añade esto **al final** de `pyproject.toml`:

   ```toml
   [tool.pytest.ini_options]
   asyncio_mode = "auto"
   ```

   Por qué: tus tests van a ser `async def`. pytest solo, por su cuenta, no
   sabe correr una corrutina — necesita alguien que abra un event loop (te
   suena de la S8: `asyncio.run`). Eso lo hace `pytest-asyncio`, y
   `asyncio_mode = "auto"` le dice "toda función `async def test_*` es mía",
   para no tener que marcar cada test a mano.

1. **La demo** — corre los seis comandos del docstring de `demo_respx.py`,
   en orden, leyendo los comentarios de cada PARTE antes de cada uno. El
   primero **debe fallar**: ese fallo es el punto.

   Las tres herramientas nuevas de hoy están ahí en versión ejecutable:
   respx (PARTES 1-4), `parametrize` (PARTE 5) y la fixture async (PARTE 6).
   Este ejercicio no te pide ninguna sintaxis que no esté en ese archivo: si
   no sabes cómo se escribe algo, está demostrado ahí. Si aun así no lo
   encuentras, es un fallo del enunciado — dímelo y lo arreglo.

2. **Predicciones** — escríbelas como comentarios al inicio de
   `test_robust_client.py`, ANTES de implementar:

   - `P1`: al final vas a correr cobertura sobre `robust_client.py` con una
     suite que cubre camino feliz, errores HTTP y timeouts. ¿Qué porcentaje
     esperas y **qué líneas concretas** van a salir sin cubrir? Justifica.
   - `P2`: imagina que en `fetch_all_robust` cambias `return_exceptions=True`
     por `False`. Tu test 4 (el mixto) ¿falla en un `assert`, pasa igual, o
     revienta antes de llegar a los asserts? Di **qué** sale y **de dónde**.

3. **`conftest.py`** — una sola fixture: `client`, que entregue un
   `httpx.AsyncClient` (con `timeout=1.0`) ya abierto y lo cierre al terminar
   el test. Es `async` (el cliente se abre con `async with`) y usa `yield`,
   igual que la fixture de ayer. Tipo de retorno:
   `AsyncIterator[httpx.AsyncClient]`.

   La PARTE 6 de la demo tiene exactamente esta fixture funcionando. Lo tuyo
   es moverla a `conftest.py` con el nombre `client` — y fijarte en **qué va
   después del `yield`**, que es lo que el test recibe.

4. **`test_robust_client.py`** — cinco tests. Todos importan de tu módulo:
   `from robust_client import BASE_URL, MODEL_IDS, fetch_all_robust, fetch_model`.
   Todos los que mocken llevan el decorador `@respx.mock`.

   1. **Camino feliz** — mockea `GET {BASE_URL}/models/1` con un 200 y un JSON
      cualquiera; afirma que `fetch_model` devuelve ese diccionario.
   2. **Errores HTTP, con `parametrize`** — un solo test que se ejecuta tres
      veces, con status `400`, `404` y `500`, y afirma que `fetch_model` lanza
      `httpx.HTTPStatusError`. La sintaxis:
      ```python
      @pytest.mark.parametrize("status", [400, 404, 500])
      ```
      y `status` entra como parámetro de la función, junto con la fixture:
      `async def test_...(status: int, client) -> None:`. El decorador
      `@respx.mock` va **arriba** del `@pytest.mark.parametrize`.
      Todo esto está corriendo en la PARTE 5 de la demo.
      Por qué existe `parametrize`: tres
      tests copiados y pegados que solo cambian en un número son un test con
      tres datos; si mañana agregas el 503, quieres tocar una lista, no crear
      otra función.
   3. **Timeout** — mockea la misma URL con `side_effect=httpx.ReadTimeout(...)`
      y afirma que sale `httpx.TimeoutException`. Fíjate en qué tarda el test.
   4. **El escenario mixto de la S9, ahora automático** — mockea las 10 URLs de
      `MODEL_IDS`: la 3 devuelve 500, la 7 lanza `ReadTimeout`, las otras ocho
      un 200 con JSON. Llama a `fetch_all_robust()` y afirma sobre el
      **resultado por índice**: que `results[3]` es un `HTTPStatusError`, que
      `results[7]` es un `TimeoutException`, y que hay exactamente 8 dicts.
      Este test solo es el que reemplaza tus tres experimentos manuales.
   5. **El mock como espía** — guarda la ruta en una variable
      (`route = respx.get(...).mock(...)`), llama a `fetch_model` una vez y
      afirma `route.called` y `route.call_count == 1`. Afirmar sobre lo que tu
      código **hizo**, no solo sobre lo que devolvió.

5. **Verifica**:
   ```bash
   uv run pytest -v
   uv run ruff check .
   ```
   Siete casos en verde (los tres del `parametrize` cuentan por separado) y
   ruff limpio.

6. **Cobertura** — ahora sí, contra tu P1:
   ```bash
   uv run pytest --cov=robust_client --cov-report=term-missing
   ```
   Lee la columna `Missing`. Contesta por escrito: ¿el número que salió
   significa que tus tests son malos? ¿Qué le falta exactamente a ese módulo
   para subirlo, y vale la pena?

7. **Auditoría de mutación — la corres tú.** Un test verde no prueba nada hasta
   que lo ves ponerse rojo. Rompe `robust_client.py`, una rotura a la vez, corre
   la suite y anota qué cae:
   - borra `response.raise_for_status()` de `fetch_model`
   - cambia `return_exceptions=True` por `False` (contrasta con tu P2)
   - haz que `fetch_model` devuelva `response.text` en vez de `response.json()`

   Si alguna rotura deja la suite en verde, ese test está probando otra cosa.
   **Deja `robust_client.py` como estaba** al terminar.

## Convención de código

Variables, funciones, docstrings y comentarios en inglés. Nombres de test:
`test_<qué>_<condición>_<resultado esperado>`.

## Cómo se evalúa

El tutor leerá `conftest.py` y `test_robust_client.py`, correrá `uv run pytest -v`,
`ruff check .` y el reporte de cobertura, y repetirá las tres roturas del paso 7
verificando que cada una pone la suite en rojo. P1 y P2 deben estar escritas con
su veredicto — **conserva la versión original si fallaste**: valen más que las
acertadas.

## Pistas

Pídelas al tutor: son escalonadas y no están escritas aquí a propósito.
