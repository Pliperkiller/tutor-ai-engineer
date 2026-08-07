# f1.testing-pytest · 01 — Suite de tests para tu API

- Herramienta: `pytest` + `fastapi.testclient.TestClient`
- Tipo: script + predecir
- Tiempo objetivo: 12 min
- Directorio de trabajo: `ejercicios/fase-1/f1.apis-rest-fastapi/01-registro-modelos/`
  (¡tu proyecto de las sesiones 10 y 11, NO esta carpeta!)

## Por qué esta herramienta

Hasta ahora verificaste tu API corriendo 8 `curl` a mano. Eso tiene tres
problemas: no se repite solo, nadie más lo puede correr, y depende de que te
acuerdes de probar el caso raro. De hecho el 500 de la sesión 11 lo encontraste
de casualidad. Un test es ese mismo `curl` escrito una vez y ejecutado para
siempre por una máquina que no se cansa ni se olvida.

`TestClient` va un paso más allá: hace la request contra tu app **sin levantar
servidor ni tocar la red**. No hay puerto, no hay `fastapi dev` corriendo en
otra terminal, no hay latencia.

## Objetivo

Escribir una suite de pytest sobre tu `main.py` que cubra camino feliz y camino
de error, que corra sola (sin que nadie exporte variables a mano) y que **no
dependa del orden** en que se ejecuten los tests.

## Paso a paso

0. **Preparación** — trabajas en `01-registro-modelos/`. Ya existen ahí tu
   `main.py` y `pyproject.toml`. Vas a CREAR dos archivos nuevos, ambos en esa
   misma carpeta: `conftest.py` y `test_main.py`. Desde `01-registro-modelos/`:
   ```bash
   uv add --dev pytest
   ```

1. **La demo** — antes de escribir nada tuyo, corre los tres comandos que están
   en el docstring de `../../f1.testing-pytest/01-suite-api/demo_pytest.py` y lee
   los comentarios. El segundo comando **debe fallar**: ese fallo es el punto.

2. **Predicciones** — escríbelas como comentarios al inicio de `test_main.py`,
   ANTES de implementar:
   - `P1`: tu `test_main.py` va a hacer `from main import app`. La línea 42 de
     `main.py` lee `os.environ["MODEL_REGISTRY_API_KEY"]` al importar el módulo.
     Si corres `pytest` sin esa variable definida en la terminal, ¿qué pasa, en
     qué momento exacto, y cuántos de tus tests llegan siquiera a ejecutarse?
   - `P2`: imagina un **sexto** test, `test_list_models_returns_all`, que hace
     `GET /models` y afirma que hay exactamente 2 modelos (los que trae `MODELS`
     al arrancar). Recuerda que tu test 4 hace un POST (agrega uno) y tu test 5
     un DELETE (borra uno). Responde: ¿ese sexto test pasa si corre **primero**?
     ¿Y si corre **después del 4**? ¿Y **después del 5**? Luego escribe qué
     propiedad tiene que cumplir la suite para que la pregunta "¿en qué orden
     corren?" deje de importar.

3. **`conftest.py`** — es el archivo que pytest carga automáticamente antes de
   los tests; ahí van las fixtures compartidas. Escribe dos cosas:
   - Lo necesario para que la suite arranque sola pese a lo que predijiste en
     P1. Regla: una suite que exige que el humano exporte algo a mano antes de
     correrla está rota. Ojo al **orden**: importa lo que importe cuándo.
   - Una fixture `client` que devuelva un `TestClient(app)`
     (`from fastapi.testclient import TestClient`). Un test la usa poniéndola
     como parámetro: `def test_algo(client): ...`.
   - Una fixture **autouse** que garantice que cada test arranque con `MODELS`
     en su estado inicial (mira la PARTE 3 de la demo). Cuidado: `MODELS` es el
     mismo objeto que usa `main.py`; reasignarlo no sirve, hay que restaurar su
     contenido.

4. **`test_main.py`** — escribe estos cinco tests. Cada uno afirma sobre el
   `status_code` y, cuando haya body, sobre `response.json()`:
   1. `GET /health` responde 200 y `{"status": "ok"}`.
   2. `GET /models/999` responde 404.
   3. `POST /models` **sin** header `X-API-Key` responde 401.
   4. `POST /models` con la key correcta responde 201 y el body devuelto trae el
      `name` que enviaste.
   5. `DELETE /models/1` con key correcta responde 204 **y** un `GET /models/1`
      posterior responde 404. Los dos asserts: el 204 solo dice "no me quejé";
      el 404 es el que prueba que borró.

   Headers en TestClient: `client.post("/models", json={...}, headers={"X-API-Key": "..."})`.

5. **Verifica** — desde `01-registro-modelos/`:
   ```bash
   uv run pytest -v
   ```
   Los 5 en verde. Después córrelos aislados para probar que no dependen del
   orden:
   ```bash
   uv run pytest -v -k delete
   uv run pytest -v -k not_found
   ```

6. **Auditoría — el paso que más importa.** Un test verde no prueba nada hasta
   que lo ves ponerse rojo. Rompe `main.py` a propósito, una rotura a la vez, y
   confirma que la suite lo detecta:
   - cambia el `404` de `get_model` por `200` → ¿se cae el test 2?
   - borra `dependencies=[Depends(verify_api_key)]` del POST → ¿se cae el test 3?
   - en `delete_model`, borra la línea `del MODELS[model_id]` → ¿se cae el test 5?

   Si alguna rotura deja la suite en verde, ese test está probando otra cosa.
   **Deja `main.py` como estaba** cuando termines (`git diff main.py` debe salir
   vacío).

## Convención de código

Variables, funciones, docstrings y comentarios en inglés (estándar del repo).
Nombres de test descriptivos: `test_<qué>_<condición>_<resultado esperado>`.

## Cómo se evalúa

El tutor leerá `conftest.py` y `test_main.py`, correrá `uv run pytest -v` y los
comandos aislados del paso 5, y repetirá las 3 roturas del paso 6 verificando
que cada una pone la suite en rojo. P1 y P2 deben estar escritas con su veredicto
(conserva la versión original si fallaste: valen más que las acertadas).

## Pistas

Pídelas al tutor: son escalonadas y no están escritas aquí a propósito.
