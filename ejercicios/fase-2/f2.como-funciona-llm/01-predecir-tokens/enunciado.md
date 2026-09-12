# f2.como-funciona-llm · 01 — Predecir tokens y sampling

- Herramienta: `tiktoken` (tokenizador local, sin API key)
- Tipo: predecir
- Tiempo objetivo: 10-12 min
- Directorio de trabajo: `ejercicios/fase-2/f2.como-funciona-llm/01-predecir-tokens/`

## Por qué esta herramienta
Un LLM te cobra y te limita por tokens, y la única forma de dejar de adivinar cuántos son es mirar el tokenizador real. `tiktoken` es la tabla pública que corre en tu PC sin clave; Claude usa otra tabla, así que los números cambian pero el mecanismo (BPE) es el mismo. Antes de esto, la gente estimaba "una palabra = un token" y se equivocaba un 30-40 %.

## Objetivo
Escribes tus **predicciones** sobre cómo se tokenizan unos textos y sobre qué produce cada configuración de sampling, ANTES de ver la respuesta. Luego corres el script dado, comparas, y por cada predicción fallada escribes en una frase por qué el tokenizador hizo lo que hizo. Lo que se evalúa no es acertar: es que la explicación del fallo use el mecanismo (piezas de la tabla, espacio como parte de la pieza, corpus con más inglés, autoregresivo, dado por token).

**Pieza nueva de este ejercicio**: `encoding.encode` / `encoding.decode` de `tiktoken` (ya la viste corrida en `demo_tokens.py`). Todo lo demás es andamiaje dado.

## Paso a paso

0. **Preparación.** Qué ya existe aquí y su rol:
   - `pyproject.toml` y `uv.lock`: dependencias del ejercicio (andamiaje; no los toques).
   - `demo_tokens.py`: la demo de la lección (andamiaje; solo para leer y correr).
   - `count_tokens.py`: el script que imprime los conteos reales de la parte A (andamiaje; **no lo corras hasta el paso 3**).
   - `RESPUESTAS.md`: **lo llenas tú**. Es el único entregable.

   Abre una terminal en esta carpeta y prepara el entorno:
   ```powershell
   cd C:\Users\pipek\OneDrive\Documentos\dev\tutor-ai-engineer\ejercicios\fase-2\f2.como-funciona-llm\01-predecir-tokens
   uv sync
   ```
   (`uv sync` crea `.venv` e instala `tiktoken`; si ya lo hiciste para la demo, dirá `Audited ... packages` y no hará nada.)

   Si estás en Mac o Linux, el `cd` cambia a la ruta de tu clon y el resto es idéntico.

1. **Parte A.1 en `RESPUESTAS.md`**: abre el archivo y mira la lista de 6 textos. Ordénalos de **menos a más tokens** según tu predicción y escribe al lado de cada uno el número que crees. Si dos te parecen iguales, di cuál esperas que empate. No abras `count_tokens.py` todavía: la lista es la misma, pero verla ordenada te arruina el ejercicio.

2. **Parte A.2 en `RESPUESTAS.md`**: para cada uno de los 3 pares, escribe dos "sí/no": ¿mismo número de tokens?, ¿mismos ids? Y una frase de por qué, usando "pieza de la tabla".

3. **Verifica**: corre
   ```powershell
   uv run python count_tokens.py
   ```
   Qué hace: tokeniza los 6 textos, los imprime ordenados de menos a más tokens con sus piezas, y luego imprime los ids de cada par con `same count` / `same ids`. Salida esperada: dos bloques, `=== part A.1 ===` con 6 filas y `=== part A.2 ===` con 3 pares. Si ves `ModuleNotFoundError: tiktoken`, no corriste `uv sync` en esta carpeta o corriste `python` a pelo en vez de `uv run python`.

4. **Parte B en `RESPUESTAS.md`**: copia la salida real debajo de tus predicciones y, por cada predicción que falló, una frase con la causa (no "me equivoqué": qué hizo la tabla y por qué). Si acertaste todo, elige las dos que te parecieron menos obvias y explica igual.

5. **Parte B.3 (opcional, 2 min)**: añade a la lista `TEXTS` de `count_tokens.py` dos textos tuyos que crees que van a sorprender (una palabra larguísima, un texto con muchos emojis, un número de teléfono, una URL). Predice, corre otra vez, anota.

6. **Parte C en `RESPUESTAS.md`**: tres configuraciones de sampling sobre el mismo prompt. Para cada una escribe qué esperas que pase si la corres 5 veces (cuántas respuestas distintas, cuán coherentes) y por qué, con la tabla de la lección. **Estas predicciones NO se verifican hoy**: se verifican contra la API real en el tópico siguiente (`f2.llamadas-api`), cuando tengas la API key. Quedan escritas ahora precisamente para que no puedas ajustarlas después de ver el resultado.

7. **Avísame en el chat** cuando `RESPUESTAS.md` esté completo. No lo pegues en el chat: yo lo leo del archivo.

## Convención de código
Si añades textos en el paso 5, los nombres de variables y comentarios en `count_tokens.py` van en inglés (estándar del repo). `RESPUESTAS.md` va en español.

## Cómo se evalúa
El tutor lee `RESPUESTAS.md` y corre `uv run python count_tokens.py`. Criterio: (a) las predicciones están escritas ANTES de la salida real (se nota: la salida real va copiada debajo); (b) cada fallo tiene una explicación que usa el mecanismo, no "no sabía"; (c) la parte C tiene las tres predicciones con su porqué. Acertar los conteos no puntúa; explicar por qué fallaron, sí.

## Pistas
Pídelas al tutor: son escalonadas y no están escritas aquí a propósito.
