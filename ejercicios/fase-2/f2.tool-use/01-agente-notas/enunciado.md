# f2.tool-use · 01 — Agente de notas con tres herramientas

- Herramienta: Anthropic API (tool use / function calling)
- Tipo: completar + test
- Tiempo objetivo: 25 min
- Directorio de trabajo: `ejercicios/fase-2/f2.tool-use/01-agente-notas/`

## Por qué esta herramienta

Un modelo solo predice texto: no puede leer tus archivos ni escribir en ellos. *Tool use* es el protocolo por el que el modelo **pide** que ejecutes una función tuya y tú le devuelves el resultado para que siga razonando. Antes de esto se intentaba que el modelo "fingiera" el dato (se lo inventaba) o se le pedía que escupiera un comando que tú parseabas a mano con expresiones regulares — frágil y sin forma de reportar un fallo. La demo de la lección tenía **una** herramienta y un camino feliz; aquí van **tres** y un fallo real.

## Objetivo

Completar un asistente de notas que responde preguntas usando tres herramientas reales, y que **no se cae** cuando una de ellas falla.

- **Entrada**: una pregunta en lenguaje natural (`chat("Which notes do I have?", client=...)`).
- **Salida**: el texto final del modelo, ya con los datos reales de las notas.
- **Restricciones**:
  - El loop lo escribes tú a mano; no uses `client.beta.messages.tool_runner`.
  - Una herramienta que lanza excepción se convierte en un `tool_result` con `is_error: True`; nunca tumba el programa.
  - Si el modelo sigue pidiendo herramientas después de `max_turns` rondas, el loop lanza `RuntimeError` en vez de devolver algo a medias.
  - Todo el código en inglés (ver "Convención de código").

## Paso a paso

0. **Preparación.** Abre una terminal en esta carpeta:
   ```bash
   cd ejercicios/fase-2/f2.tool-use/01-agente-notas
   ```
   Archivos que **ya existen** aquí:
   - `note_tools.py` — andamiaje. Las tres funciones Python reales (`list_notes`, `read_note`, `append_to_note`), ya escritas y con type hints. **No las toques.** Léelas: necesitas sus nombres de parámetro exactos.
   - `notes/` — tres notas de ejemplo (`groceries.md`, `books.md`, `meeting-2026-09-20.md`). Son los datos sobre los que trabajan las herramientas.
   - `agent.py` — el esqueleto que vas a completar. Las partes marcadas `GIVEN` no se tocan; las marcadas `# TODO` son tuyas.
   - `test_agent.py` — andamiaje. 11 tests que ahora fallan y que deben pasar. **No los modifiques**: si un test te estorba, el problema está en tu código o en tu entendimiento, y eso lo discutimos.
   - `pyproject.toml` — declara las dependencias (`anthropic`, `pytest`).

   Archivos que debes **crear tú**:
   - `.env` en esta misma carpeta, con una sola línea:
     ```
     ANTHROPIC_API_KEY=sk-ant-api03-TU-KEY-AQUI
     ```
     (misma key que usaste en `f2.llamadas-api`). El repo ya ignora `.env`; confírmalo con `git status` cuando lo crees.

   Prepara el entorno:
   ```bash
   uv sync
   ```
   `uv sync` lee `pyproject.toml`, crea la carpeta `.venv` (el *entorno virtual*: una copia de Python con las librerías de este proyecto y de ningún otro) e instala `anthropic` y `pytest` dentro. Deberías ver un par de líneas tipo `Installed N packages`.

1. **Ve el suelo antes de construir.** Corre los tests ahora, con el esqueleto vacío:
   ```bash
   uv run pytest test_agent.py -q
   ```
   `uv run` ejecuta el comando dentro del `.venv` de este proyecto. `pytest` descubre las funciones que empiezan por `test_` y las corre; `-q` las resume en una línea. Debes ver **11 failed** (o errores de `NotImplementedError` / `AssertionError`). Sin key: estos tests no tocan la red. Ese "11 failed" es tu punto de partida y tu marcador.

2. **Lee los tests antes de escribir nada.** Ábrelos y responde para ti mismo: ¿qué forma exacta tiene que tener cada elemento de `TOOLS`? ¿Qué devuelve `run_tool`? ¿Qué compara `test_chat_sends_back_the_assistant_turn_and_the_tool_result` sobre el segundo mensaje? Los tests son la especificación; el enunciado solo la resume.

3. **Declara las tres herramientas** (`TOOLS` en `agent.py`). Una entrada por función de `note_tools.py`. Ojo con dos cosas que los tests verifican: los nombres de las `properties` tienen que coincidir con los nombres de los parámetros de la función real, y la `description` tiene que decir **cuándo** llamarla, no solo qué hace. Una función sin parámetros también necesita su `input_schema`.
   **Verifica** solo esta parte:
   ```bash
   uv run pytest test_agent.py -q -k "declared or schema or description"
   ```
   `-k` filtra por nombre de test. Deben pasar 3.

4. **Conecta el despachador** (`HANDLERS`) y **escribe `run_tool`**. `run_tool` ejecuta la función que pide el modelo y devuelve una tupla `(content, is_error)`: el texto que viaja de vuelta y si ese texto describe un fallo. El test exige que el nombre de la clase de la excepción aparezca en el texto — piensa por qué el modelo necesita eso y no solo el mensaje.
   **Verifica**:
   ```bash
   uv run pytest test_agent.py -q -k "run_tool"
   ```
   Deben pasar 2.

5. **Escribe el loop** (`chat`). Es el corazón del ejercicio: llamar a la API, decidir si el modelo terminó, guardar su turno en el historial, ejecutar cada petición de herramienta, devolver todos los resultados y repetir, con un tope de vueltas. Fíjate en que `client` llega como parámetro: usa **ese**, no uno global.
   **Verifica todo**:
   ```bash
   uv run pytest test_agent.py -q
   ```
   Objetivo: **11 passed**.

6. **La corrida real** (aceptación). Ahora sí con la API:
   ```bash
   uv run --env-file .env python agent.py
   ```
   `--env-file .env` carga tu key solo en este comando (no en toda la terminal). Son tres preguntas, ~6-8 llamadas, menos de un centavo. Qué debes ver:
   - Pregunta 1: el modelo lista tus tres notas reales.
   - Pregunta 2: pide la nota `shopping`, que **no existe** → una línea de tool con `error=True` y un `FileNotFoundError`, y aun así una respuesta final coherente (idealmente el modelo se recupera listando las notas de verdad). **La conversación no se cae: eso es lo que se está probando.**
   - Pregunta 3: añade la línea a `groceries` y te la lee de vuelta.

   Si añades `print` a tus llamadas de herramienta, verás qué pidió el modelo y con qué argumentos — sin eso el loop es una caja negra.

7. **Deja constancia.** Crea `RESULTADOS.md` en esta carpeta y pega la salida de la corrida del paso 6, y debajo dos o tres líneas: qué hizo el modelo tras el error de la nota inexistente, y si eso coincide con lo que esperabas.

## Convención de código

Variables, funciones, docstrings y comentarios en inglés (estándar del repo).

## Cómo se evalúa

```bash
uv run pytest test_agent.py -q
uv run --env-file .env python agent.py
```
Criterio: los 11 tests pasan, la corrida real ejecuta las tres herramientas, y el turno con la nota inexistente termina en respuesta final en vez de en excepción.

## Pistas

Pídelas al tutor: son escalonadas y no están escritas aquí a propósito.
