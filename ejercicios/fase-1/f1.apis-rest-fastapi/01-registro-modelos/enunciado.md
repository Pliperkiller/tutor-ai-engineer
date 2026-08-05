# f1.apis-rest-fastapi · 01 — Registro de modelos: tu primera API

- Herramienta: FastAPI + uv (proyecto real: pyproject, lockfile, uv run)
- Tipo: completar (+ predicción escrita antes de ejecutar)
- Tiempo objetivo: 12 min
- Directorio de trabajo: `ejercicios/fase-1/f1.apis-rest-fastapi/01-registro-modelos/`

## Por qué esta herramienta
Recibir HTTP crudo es parsear texto de un socket a mano. Flask (2010) mejoró
el enrutamiento pero dejó la validación y la documentación como trabajo manual.
FastAPI (2018) junta lo que ya dominas — type hints + Pydantic + async — y te
da validación automática (422 con `loc`/`msg`), serialización a JSON y docs
interactivas en `/docs` generadas del código real.

## Objetivo
Una API "Model Registry" con **4 endpoints** sobre un store en memoria:

| Verbo | Ruta | Respuesta |
|---|---|---|
| GET | `/health` | `{"status": "ok"}` |
| GET | `/models` | lista de todos los modelos registrados |
| GET | `/models/{model_id}` | el modelo pedido, o **404** si no existe |
| POST | `/models` | registra un modelo nuevo (body validado), responde **201** |

Restricciones:
- El body del POST se valida con un modelo Pydantic (`ModelIn`): `name` (str),
  `provider` (str), `max_tokens` (int **> 0** — usa Field, lo conoces de S6).
- El 404 se lanza con `HTTPException(status_code=404, detail="...")` — la
  forma FastAPI de convertir una excepción en respuesta HTTP.
- El POST asigna el siguiente id entero libre y devuelve el modelo creado
  incluyendo su `id`.

## Paso a paso
0. **Preparación** — En esta carpeta ya existen: `enunciado.md` (esto) y
   `main.py` (esqueleto con TODOs que tú completas). El proyecto lo creas TÚ
   con uv, dentro de ESTA carpeta:
   ```bash
   cd ejercicios/fase-1/f1.apis-rest-fastapi/01-registro-modelos
   uv init --bare
   uv add "fastapi[standard]"
   ```
   `--bare` crea solo `pyproject.toml` (sin main.py de ejemplo, que ya existe).
   Mira lo que apareció: `pyproject.toml`, `uv.lock`, `.venv/`. Abre el
   `pyproject.toml` y localiza dónde quedó declarado fastapi.
1. **Predicciones primero** — como comentario inicial de `main.py` (en inglés):
   - P1: cuando abras `/docs` sin haber escrito documentación, ¿qué esperas
     ver listado y de dónde sale esa información?
   - P2: si haces POST con `{"name": "x", "provider": "y", "max_tokens": -5}`,
     ¿qué status code responde la API y quién lo decide (tu código o FastAPI)?
2. **Completa los TODOs de `main.py`** en orden (1 → 4). Levanta el servidor
   desde ya y déjalo corriendo — se recarga solo al guardar:
   ```bash
   uv run fastapi dev main.py
   ```
3. **Verifica con `/docs`** — abre `http://127.0.0.1:8000/docs` en el
   navegador. Prueba desde ahí ("Try it out"):
   - GET `/models/1` → 200 con claude-fable-5.
   - GET `/models/99` → 404 con tu detail.
   - POST `/models` válido → 201 y luego GET `/models` lo incluye.
   - POST con `max_tokens: -5` → compara contra tu P2.
4. **Cierra las predicciones** — vuelve al comentario de P1/P2 y anota si
   acertaste y qué te sorprendió.

## Convención de código
Variables, funciones, docstrings y comentarios en inglés (estándar del repo).
Nada de nombres que sombreen builtins (`id` como variable suelta — usa
`model_id`). Tercera vez que se te marca: esta vez cuenta en la evaluación.

## Cómo se evalúa
El tutor corre `uv run fastapi dev main.py` y prueba los 4 endpoints (incluye
404, 201, y el 422 del body inválido). Criterio: los 4 endpoints correctos,
ModelIn con constraint, predicciones escritas y comentadas, identificadores
en inglés sin sombras de builtins.

## Pistas
Pídelas al tutor: son escalonadas y no están escritas aquí a propósito.
