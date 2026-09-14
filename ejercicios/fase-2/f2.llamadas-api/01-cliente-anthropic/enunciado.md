# f2.llamadas-api · 01 — Cliente Anthropic con costos y reintentos

- Herramienta: SDK de Anthropic (`anthropic`)
- Tipo: completar (+ un paso `predecir`)
- Tiempo objetivo: 25 min
- Directorio de trabajo: `ejercicios/fase-2/f2.llamadas-api/01-cliente-anthropic/`

## Por qué esta herramienta

Ya sabes hablar con APIs REST usando httpx a pelo (F1). El SDK de Anthropic hace eso mismo por dentro, pero te ahorra armar headers, parsear SSE y clasificar errores: expone la Messages API como funciones de Python con excepciones tipadas (`RateLimitError`, `AuthenticationError`...). Lo que el SDK NO trae hecho a tu medida: la contabilidad de costos y la política de reintentos — eso lo construyes tú hoy.

## Objetivo

Un módulo `llm_client.py` con tres funciones: `cost_usd` (cuánto costó una request, en dólares), `ask` (una llamada completa que devuelve texto y costo) y `ask_with_retries` (backoff exponencial a mano, solo ante errores transitorios). Con tu `ask` funcionando, un script de andamiaje verifica contra la API real las 3 predicciones de sampling que dejaste escritas en la S26.

## Paso a paso

0. **Preparación.** Archivos que YA existen aquí:
   - `llm_client.py` — esqueleto con 3 `TODO`. Cada función lleva su contrato en el docstring. **Aquí trabajas tú.**
   - `sampling_check.py` — ANDAMIAJE del tutor, completo: léelo, no lo modifiques. Usa tu `ask` cuando esté lista.
   - `RESULTADOS.md` — lo llenas tú en los pasos 7 y 8.
   - Un nivel arriba (`../`): `demo_basic_call.py` y `demo_streaming.py`, las demos de la lección.

   Abre la terminal EN esta carpeta y corre:
   ```bash
   uv init --bare
   ```
   Crea solo un `pyproject.toml` (el manifiesto del proyecto: qué dependencias pide). `--bare` evita los archivos de ejemplo. Salida esperada: `Initialized project ...`.
   ```bash
   uv add anthropic
   ```
   Resuelve e instala el SDK en un `.venv` propio de esta carpeta y apunta la versión en `uv.lock` (lo pedido vs lo resuelto, como en S10). Salida esperada: `Installed N packages` con `anthropic` en la lista.

   **La API key va en un archivo de este proyecto, NO en el shell.** Crea aquí un archivo llamado `.env` con una sola línea:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-TU-KEY-AQUI
   ```
   Un *archivo `.env`* es un archivo de texto con pares `VARIABLE=valor` que una herramienta carga como variables de entorno justo antes de ejecutar un programa. Por qué aquí y no en `~/.zshrc`: una variable exportada en el perfil del shell la ve **todo** programa que corras en esa terminal — incluidas herramientas como Claude Code, que si encuentran `ANTHROPIC_API_KEY` facturan contra los créditos de tu API en vez de tu suscripción. El `.env` solo lo lee el comando que tú le digas. El repo ya ignora `.env` y `.env.*` en `.gitignore`, así que no puede terminar en un commit — verifícalo tú con `git status` y confirma que `.env` no aparece.

1. **Corre las demos de la lección** (por fin hay key). Desde esta carpeta:
   ```bash
   uv run --env-file .env python ../demo_basic_call.py
   ```
   `uv run` ejecuta usando el `.venv` de ESTE proyecto aunque el archivo esté un nivel arriba; `--env-file .env` carga tu key en el entorno de ESE comando y de ningún otro. Debes ver: una frase sobre el cielo, `stop_reason: end_turn`, los dos conteos de tokens y un costo de fracciones de centavo. Si ves `AuthenticationError`, la key no está llegando: revisa que el `.env` esté en esta carpeta y sin comillas ni espacios alrededor del `=`.
   ```bash
   uv run --env-file .env python ../demo_streaming.py
   ```
   Debes ver el poema aparecer **a pedazos**, no de golpe — eso es el streaming de la lección. Al final, los tokens de salida.

2. **`TODO(1)` — `cost_usd`** en `llm_client.py`. Contrato en el docstring. Verifica sin tocar la red:
   ```bash
   uv run python -c "from llm_client import cost_usd; print(cost_usd('claude-opus-5', 1000, 200))"
   ```
   Sin `--env-file`: esta función es aritmética pura, no toca la red y no necesita la key.
   Este comando importa tu función y la ejecuta con 1000 tokens de entrada y 200 de salida en Opus. Haz TÚ la cuenta en papel antes de correrlo y compara. (Si da `NotImplementedError`, sigue el esqueleto en pie; si da `KeyError`, revisa el nombre del modelo.)

3. **`TODO(2)` — `ask`.** La demo 1 es tu mapa: es la misma llamada, empaquetada en una función con parámetros. Ojo al contrato: `temperature` y `top_p` solo viajan a la API si no son `None`.

4. **`TODO(3)` — `ask_with_retries`.** La pieza nueva de hoy. El contrato del docstring es la política que discutiste en la Q3 de la lección (transitorio se reintenta esperando 1-2-4-8-16s + jitter; permanente muere ya). Nada de la red cambia aquí: es un bucle alrededor de `ask`.

5. **Verifica el camino feliz:**
   ```bash
   uv run --env-file .env python llm_client.py
   ```
   Ejecuta el bloque `if __name__ == "__main__"` del módulo. Debes ver los nombres de las dos lunas de Marte y el costo. Sin reintentos visibles: no hubo error.

6. **Ruff antes de decir "listo"** (el hábito de S14-S15):
   ```bash
   uvx ruff check .
   ```
   `uvx` ejecuta ruff sin instalarlo en el proyecto. Salida esperada: `All checks passed!`.

7. **Predice y rompe (parte `predecir`).** Crea un segundo archivo, `.env.broken`, con una key falsa:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-esto-no-es-una-key
   ```
   ABRE `RESULTADOS.md` y escribe tu predicción ANTES de correr esto:
   ```bash
   uv run --env-file .env.broken python llm_client.py
   ```
   Mismo programa, otro archivo de entorno: tu key real ni se toca. Córrelo, y anota qué pasó de verdad y si coincide con lo que predijiste.

8. **Verifica tus predicciones de la S26:**
   ```bash
   uv run --env-file .env python sampling_check.py
   ```
   Corre 15 requests (3 configuraciones × 5) con tu `ask`. Tarda ~20-30s y cuesta menos de un centavo. Copia los conteos a la tabla de `RESULTADOS.md` y escribe la causa de cada fila — la frase, no el dato.

## Convención de código

Variables, funciones, docstrings y comentarios en inglés (estándar del repo).

## Cómo se evalúa

El tutor ejecuta los pasos 5, 6, 7 y 8 y lee `llm_client.py` y `RESULTADOS.md`. Criterio: las 3 funciones cumplen su contrato, el error permanente NO se reintenta, ruff limpio, y la tabla de la parte C llena con causas.

## Pistas

Pídelas al tutor: son escalonadas y no están escritas aquí a propósito.
