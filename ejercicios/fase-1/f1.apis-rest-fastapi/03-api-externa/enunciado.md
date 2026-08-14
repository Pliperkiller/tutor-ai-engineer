# Ejercicio 03 — Tu API consume una API pública externa (cierre de Fase 1)

**Tópico:** f1.apis-rest-fastapi (integración con f1.async-basico y f1.testing-pytest)
**Tipo:** script + predecir
**Tiempo estimado:** 20-25 min

## Contexto

Este es el criterio de dominio de toda la Fase 1: *"una API REST con FastAPI que consuma una API
pública externa, valide entradas/salidas con Pydantic, tenga suite de tests con pytest (incluyendo
mocks de la API externa)"*.

Hasta hoy tenías dos mitades separadas: tu API (que solo sirve datos propios) y tu cliente httpx
(que vive fuera de FastAPI). Hoy se juntan: **tu API pasa a ser cliente de otro servicio**. Ese es
exactamente el patrón del capstone, donde el "servicio externo" será la API de un LLM.

La API pública que vas a consumir es **Frankfurter** (tasas de cambio, sin credenciales):

```
GET https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR
-> {"amount":1.0,"base":"USD","date":"2026-08-13","rates":{"EUR":0.867}}
```

## Qué ya existe en esta carpeta

| Archivo | Qué es |
|---|---|
| `demo_upstream.py` | La demo ejecutable. **Léela y córrela antes de empezar.** Tiene toda la sintaxis nueva. |
| `main.py` | Copia de TU API (la de 01-registro-modelos con API key). Aquí escribes. |
| `conftest.py` | Copia de TU conftest. Vas a tener que tocar la fixture `client`. |
| `test_main.py` | Copia de TUS 5 tests. **No los toques**: deben seguir verdes al final. |
| `pyproject.toml` | Ya trae fastapi, httpx, pytest, respx, ruff, mypy. |

## Qué creas tú

| Archivo | Qué es |
|---|---|
| `test_upstream.py` | Los 5 tests nuevos del endpoint que llama al exterior. |

---

## Paso a paso

### 1. Preparar el entorno

```powershell
cd ejercicios\fase-1\f1.apis-rest-fastapi\03-api-externa
uv sync
```

### 2. Correr la demo y leerla

```powershell
uv run python demo_upstream.py
```

Debe imprimir un caso feliz (200), un 502 y un 504. Lee las 5 PARTES del archivo: ahí está
**toda** la sintaxis que necesitas hoy.

- PARTE 1: `lifespan` + `app.state` — un solo `AsyncClient` compartido por toda la app.
- PARTE 2: `get_client(request: Request)` — la dependencia que reparte ese cliente.
- PARTE 3: traducción de errores del upstream (`504` timeout / `502` status error).
- PARTE 4: `respx` + `TestClient`, y por qué respx no intercepta tus propias requests.
- PARTE 5: `return_value=httpx.Response(500)` vs `side_effect=httpx.ConnectTimeout(...)`.

### 3. Montar el cliente compartido en `main.py`

Añade el `lifespan` y la dependencia `get_client`, siguiendo PARTES 1 y 2 de la demo. El
`AsyncClient` va con `timeout=2.0`. Recuerda pasar `lifespan=` al construir el `FastAPI(...)`.

Verificación: `uv run fastapi dev main.py` arranca sin errores (necesitas la env var:
`$env:MODEL_REGISTRY_API_KEY="dev-secret-key"` antes de arrancar). Ctrl+C para bajarlo.

### 4. Escribir el endpoint `GET /models/{model_id}/cost` en `main.py`

Query param obligatorio `currency` (ej: `/models/1/cost?currency=EUR`).

Contrato:

1. Si `model_id` no está en `MODELS` → **404**. Esto se decide **antes** de llamar al exterior:
   no se gasta una llamada de red en una petición que ya sabes inválida.
2. Costo en dólares: `cost_usd = max_tokens / 1000 * USD_PER_1K_TOKENS`, con
   `USD_PER_1K_TOKENS = 3.0` como constante del módulo.
3. Llama al upstream con el cliente compartido:
   `GET https://api.frankfurter.dev/v1/latest` con `params={"base": "USD", "symbols": currency}`.
4. Traducción de fallos:
   - el upstream no responde a tiempo → **504**
   - el upstream responde con status de error → **502**
   - el upstream responde 200 pero `currency` **no viene** dentro de `rates` → **502**
     (no confíes en la forma del payload ajeno)
5. Respuesta: un modelo Pydantic `CostOut` como tipo de retorno del endpoint, con los campos
   `id: int`, `name: str`, `currency: str`, `rate: float`, `cost: float`.
   `cost = round(cost_usd * rate, 2)`.

Restricciones: todo en inglés; sin sombrear builtins; sin código muerto comentado.

### 5. Ajustar la fixture `client` en `conftest.py`

**P1 — escríbela como comentario en `test_upstream.py` ANTES de correr nada:** si dejas la fixture
tal cual está hoy (`return TestClient(app)`), ¿qué pasa al correr un test del endpoint nuevo?
No respondas "falla el test": di **en qué momento exacto** revienta el código (qué línea se ejecuta
primero y qué excepción sale) y **qué reporta pytest**.

Después ajusta la fixture para que el lifespan corra (PARTE 4 de la demo).

### 6. Escribir `test_upstream.py`

Cinco tests, todos con el upstream mockeado (cero red):

1. **Camino feliz**: upstream 200 con `{"amount":1.0,"base":"USD","date":"2026-08-13","rates":{"EUR":0.5}}`
   → tu endpoint responde 200, y afirmas el `cost` y el `rate` exactos que salen de esa tasa.
   Además, usa la ruta como espía: verifica que el upstream se llamó **una** vez y que los params
   enviados fueron `base=USD` y `symbols=EUR`.
2. **Modelo inexistente**: `/models/999/cost?currency=EUR` → 404 **y** el upstream **no** fue
   llamado (`route.called`).
3. **Upstream con status de error** → 502. Usa `@pytest.mark.parametrize` con al menos 3 status
   distintos (por ejemplo 404, 500, 503).
4. **Upstream lento** (`side_effect=httpx.ConnectTimeout(...)`) → 504.
5. **Upstream 200 pero sin la moneda pedida** en `rates` → 502.

**P2 — escríbela como comentario antes de correr el test 3:** el upstream responde 404 porque la
moneda no existe. ¿Qué status recibe *tu* cliente y por qué **no** es un 404?

### 7. Verificar

```powershell
uv run pytest -v
uv run ruff check .
uv run mypy main.py
```

Los 5 tests viejos de `test_main.py` deben seguir verdes: 10 verdes en total (12 si parametrizaste
con 3 status).

### 8. Prueba contra la API real (con red)

```powershell
$env:MODEL_REGISTRY_API_KEY="dev-secret-key"
uv run fastapi dev main.py
```

En otra terminal:

```powershell
curl.exe -s "http://127.0.0.1:8000/models/1/cost?currency=EUR"
curl.exe -s -w "`nHTTP %{http_code}`n" "http://127.0.0.1:8000/models/1/cost?currency=XXX"
curl.exe -s -w "`nHTTP %{http_code}`n" "http://127.0.0.1:8000/models/999/cost?currency=EUR"
```

Avísame cuando tengas los tests en verde y los tres curls corridos.

---

## Criterio de evaluación

- [ ] El endpoint decide el 404 **antes** de tocar la red.
- [ ] Cliente httpx compartido vía lifespan + `app.state`, no uno por request.
- [ ] 502 y 504 diferenciados, y el payload ajeno validado antes de usarlo.
- [ ] Salida tipada con un modelo Pydantic.
- [ ] 5 tests nuevos, todos sin red, con assert sobre valores concretos (no solo status).
- [ ] P1 y P2 escritas **antes** de ejecutar.
- [ ] `ruff` y `mypy` limpios.
