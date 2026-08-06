# f1.apis-rest-fastapi · 02 — API key y endpoint DELETE

- Herramienta: FastAPI (`fastapi.security.APIKeyHeader` + `Depends`) y mypy
- Tipo: script + predecir
- Tiempo objetivo: 12 min
- Directorio de trabajo: `ejercicios/fase-1/f1.apis-rest-fastapi/01-registro-modelos/` (¡el proyecto de la sesión 10, NO esta carpeta!)

## Por qué esta herramienta
Tu API acepta escrituras de cualquiera. Una API key en el header `X-API-Key` es
el esquema estándar de autenticación máquina-a-máquina (OpenAI, Anthropic,
Stripe). En FastAPI se implementa con una dependencia (`Depends`): una función
que corre antes del handler y lo bloquea con 401 si la key falta o es incorrecta.

## Objetivo
Sobre tu `main.py` existente:
1. Los GET siguen públicos. `POST /models` y un **nuevo** `DELETE /models/{model_id}` quedan protegidos por API key.
2. La key esperada NO va escrita en el código: se lee de la variable de entorno `MODEL_REGISTRY_API_KEY`.
3. `uv run mypy main.py` pasa sin errores (deuda pendiente de python-profesional).

## Paso a paso

0. **Preparación** — trabajas en `01-registro-modelos/main.py` (ya existe, con
   tus 4 endpoints). No creas archivos nuevos. Instala mypy como dependencia de
   desarrollo (desde `01-registro-modelos/`):
   ```bash
   uv add --dev mypy
   ```

1. **Predicciones** — escribe como comentarios al inicio de `main.py`, ANTES de
   implementar nada:
   - `P1`: harás `POST /models` sin header `X-API-Key`. ¿Qué status code
     esperas y QUIÉN lo decide (¿Pydantic? ¿tu código? ¿FastAPI solo?)?
   - `P2`: borras el modelo de id más alto con DELETE y luego haces un POST.
     ¿Qué id recibe el nuevo modelo y qué problema puede causarle a un cliente
     que guardó una referencia al modelo borrado?

2. **La key desde el entorno** — en `main.py`, lee la key esperada con `os.environ`
   al inicio del módulo (si la variable no existe, que el arranque falle: eso es
   correcto, una API sin key configurada no debe levantar). Antes de arrancar el
   servidor, define la variable en tu terminal:
   ```bash
   export MODEL_REGISTRY_API_KEY="dev-secret-key"       # bash/zsh
   ```
   ```powershell
   $env:MODEL_REGISTRY_API_KEY = "dev-secret-key"       # PowerShell
   ```

3. **La dependencia** — crea una función `verify_api_key` usando
   `APIKeyHeader(name="X-API-Key", auto_error=False)` (import desde
   `fastapi.security`). Si la key llega ausente o no coincide con la esperada
   (compara con `secrets.compare_digest`), lanza `HTTPException` 401 con un
   `detail` claro. Si coincide, no devuelve nada.

4. **Proteger POST** — añade la dependencia al decorador de `create_model` con
   `dependencies=[Depends(verify_api_key)]`. La firma de la función no cambia.

5. **DELETE** — implementa `DELETE /models/{model_id}`, también protegido:
   - id inexistente → 404 (mismo criterio que tu GET).
   - id existente → bórralo de `MODELS` y responde `status_code=204` (declarado
     en el decorador). Un 204 no lleva body: la función devuelve `None`.

6. **Verifica a mano** — levanta el servidor (`uv run fastapi dev main.py`) y
   corre, en otra terminal.

   **PowerShell** (ojo: `curl` a secas es un alias de `Invoke-WebRequest`, hay
   que invocar `curl.exe`; y las comillas del JSON van escapadas como `\"`):
   ```powershell
   # sin key -> ¿P1?
   curl.exe -i -X POST http://127.0.0.1:8000/models -H "Content-Type: application/json" -d '{\"name\": \"m\", \"provider\": \"p\", \"max_tokens\": 100}'
   # key incorrecta -> 401
   curl.exe -i -X POST http://127.0.0.1:8000/models -H "X-API-Key: wrong" -H "Content-Type: application/json" -d '{\"name\": \"m\", \"provider\": \"p\", \"max_tokens\": 100}'
   # key correcta -> 201
   curl.exe -i -X POST http://127.0.0.1:8000/models -H "X-API-Key: dev-secret-key" -H "Content-Type: application/json" -d '{\"name\": \"m\", \"provider\": \"p\", \"max_tokens\": 100}'
   # GET sigue publico -> 200
   curl.exe -i http://127.0.0.1:8000/models
   # DELETE del id mas alto y POST de nuevo -> comprueba tu P2
   curl.exe -i -X DELETE http://127.0.0.1:8000/models/3 -H "X-API-Key: dev-secret-key"
   curl.exe -i -X POST http://127.0.0.1:8000/models -H "X-API-Key: dev-secret-key" -H "Content-Type: application/json" -d '{\"name\": \"m2\", \"provider\": \"p\", \"max_tokens\": 100}'
   ```

   **bash/zsh** (por si trabajas desde Linux/macOS):
   ```bash
   curl -i -X POST http://127.0.0.1:8000/models -H "Content-Type: application/json" -d '{"name": "m", "provider": "p", "max_tokens": 100}'
   curl -i -X POST http://127.0.0.1:8000/models -H "X-API-Key: wrong" -H "Content-Type: application/json" -d '{"name": "m", "provider": "p", "max_tokens": 100}'
   curl -i -X POST http://127.0.0.1:8000/models -H "X-API-Key: dev-secret-key" -H "Content-Type: application/json" -d '{"name": "m", "provider": "p", "max_tokens": 100}'
   curl -i http://127.0.0.1:8000/models
   curl -i -X DELETE http://127.0.0.1:8000/models/3 -H "X-API-Key: dev-secret-key"
   curl -i -X POST http://127.0.0.1:8000/models -H "X-API-Key: dev-secret-key" -H "Content-Type: application/json" -d '{"name": "m2", "provider": "p", "max_tokens": 100}'
   ```
   Anota junto a cada predicción si acertaste (conserva la versión original si
   no: las predicciones falladas valen más que las acertadas).

7. **Docs** — abre http://127.0.0.1:8000/docs y busca el candado/botón
   *Authorize*. Pruébalo: autorízate con la key y ejecuta el POST desde ahí.

8. **mypy** — corre:
   ```bash
   uv run mypy main.py
   ```
   y arregla lo que reporte hasta que salga `Success: no issues found`.

## Convención de código
Variables, funciones, docstrings y comentarios en inglés (estándar del repo).
Cuidado con nombres que sombreen builtins.

## Cómo se evalúa
El tutor leerá `main.py`, levantará el servidor y repetirá los curls del paso 6
(401 sin key y con key mala, 201 con key, 204/404 en DELETE, GET público) +
`uv run mypy main.py` limpio. Las predicciones P1/P2 deben estar escritas con su
veredicto.
