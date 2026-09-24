# f2.prompting-estructurado · 01 — Clasificador de tickets: v1 (vibras) vs v2 (contrato)

- Herramienta: system prompts versionados + un evaluador con casos de prueba
- Tipo: script (+ `completar` en el evaluador + un paso `predecir`)
- Tiempo objetivo: 25 min
- Directorio de trabajo: `ejercicios/fase-2/f2.prompting-estructurado/01-clasificador-tickets/`

## Por qué esta herramienta

Un prompt "por vibras" se prueba con dos entradas a ojo y se da por bueno. Hoy haces lo contrario: dos versiones del prompt en archivos, una lista de 10 casos con su respuesta esperada, y un script que cuenta los errores de cada versión. Al final no dices "v2 se ve mejor", dices "v1 falló 11 de 30, v2 falló 1, y esta pieza del contrato es la causa". Es el criterio de dominio del tópico.

## Objetivo

Un clasificador de tickets de soporte con **4 categorías**: `billing` (cobros, facturas, pagos), `bug` (algo del producto falla), `account` (login, contraseña, correo, acceso a la cuenta) y `other` (todo lo demás, incluido el mensaje vacío). La cuarta categoría, `account`, no sale en la demo de la lección: tus ejemplos y tus reglas los escribes tú, no los copias.

Produces:
- `prompts/classifier_v1.txt` y `prompts/classifier_v2.txt`: dos system prompts.
- `cases.json`: 10 casos de prueba con su categoría esperada.
- Las dos funciones `TODO` de `run_eval.py`.
- `RESULTADOS.md` lleno: predicción, tabla y el *por qué*.

## Paso a paso

0. **Preparación.** Archivos que YA existen aquí:
   - `classifier.py`: ANDAMIAJE completo. `load_prompt(path)` lee un archivo de prompt; `classify(system_prompt, message)` hace UNA llamada y devuelve el texto tal cual, sin limpiarlo. El mensaje siempre va dentro de `<message>...</message>`, en las dos versiones: así lo único que cambia entre v1 y v2 es el system prompt. Léelo, no lo modifiques.
   - `run_eval.py`: el evaluador. Tiene 2 `TODO` con su contrato en el docstring. **Aquí trabajas tú.** El resto (`print_summary`, `main`) ya está escrito.
   - `RESULTADOS.md`: lo llenas en los pasos 5 y 8.

   Archivos que CREAS tú: la carpeta `prompts/` con `classifier_v1.txt` y `classifier_v2.txt` dentro, y `cases.json` en esta carpeta.

   Abre la terminal EN esta carpeta y corre (sirve igual en PowerShell y en bash):
   ```
   uv init --bare
   uv add anthropic
   ```
   El primero crea solo el `pyproject.toml` (el manifiesto del proyecto). El segundo instala el SDK en un `.venv` propio de esta carpeta. Salida esperada: `Initialized project ...` y luego `Installed N packages` con `anthropic` en la lista.

   Crea aquí un archivo `.env` con una sola línea, igual que en `f2.llamadas-api`:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-TU-KEY-AQUI
   ```
   Puedes copiar el de `../../f2.llamadas-api/01-cliente-anthropic/` si aún lo tienes. Verifica con `git status` que `.env` NO aparece en la lista (el `.gitignore` lo excluye).

1. **`prompts/classifier_v1.txt`: el prompt por vibras.** Máximo 2 líneas: la tarea y las 4 categorías, sin más. Escríbelo como lo escribiría alguien con prisa, en serio: el experimento solo sirve si v1 es el prompt que de verdad se ve en producción, no uno saboteado a propósito.

2. **`cases.json`: los 10 casos.** Es un archivo JSON: una lista (`[ ... ]`) de objetos (`{ ... }`). Cada objeto tiene tres campos: `family` (la familia del caso), `message` (el texto del ticket) y `expected` (la categoría correcta). Sintaxis de JSON: comillas dobles siempre, una coma entre objetos y **ninguna coma después del último** (con esa coma de más, JSON no carga). Este es un caso de ejemplo para que veas la forma. Úsalo si quieres, pero cuenta como uno de tus 10:
   ```json
   [
     {"family": "happy", "message": "My card was charged twice this month", "expected": "billing"}
   ]
   ```
   Las familias, las mismas que propusiste en la Q4 de la lección:
   - `happy` (4 casos): **uno por categoría**, las 4. Es lo que te faltó en la Q4: sin un caso por categoría no sabes si el prompt conoce todas.
   - `edge` (3 casos): entradas que no encajan limpio. Por ejemplo: el mensaje vacío `""`, un mensaje en otro idioma, uno ambiguo o que no pertenece a nada.
   - `injection` (3 casos): mensajes que traen instrucciones dentro. En `expected` va lo que un buen clasificador debería responder: la categoría del pedido real, si lo hay, u `other` si el mensaje no trae ningún pedido real.

   El formato NO es una familia (lo distinguiste bien en la Q4): se verifica sobre TODAS las salidas en el `TODO(1)`.

   Verifica que el archivo carga:
   ```
   uv run python -c "import json; c = json.load(open('cases.json', encoding='utf-8')); print(len(c), sorted({x['family'] for x in c}))"
   ```
   Este comando lee el archivo con `json`, e imprime cuántos casos hay y qué familias aparecen. Salida esperada: `10 ['edge', 'happy', 'injection']`. Si ves `JSONDecodeError`, el mensaje trae la línea y la columna donde está el error. Casi siempre es una coma de más o una comilla simple.

3. **`TODO(1)`: `is_valid_format`** en `run_eval.py`. El contrato está en el docstring. Verifica sin tocar la red:
   ```
   uv run python -c "from run_eval import is_valid_format as f; print(f('bug'), f('bug\n'), f(' bug'), f('Bug'), f('bug.'))"
   ```
   Importa tu función y la prueba con 5 salidas. El `\n` es un salto de línea dentro del string de Python (tanto bash como PowerShell lo pasan sin tocarlo). Salida esperada: `True False False False False`.

4. **`TODO(2)`: `evaluate`.** El contrato está en el docstring. No lleva sintaxis nueva: bucles, un dict de dicts y contadores, lo que ya usaste en F1. Si notas que te falta alguna sintaxis que no has visto, es un fallo del enunciado: dilo y lo corrijo, no la adivines.

5. **Predice y corre v1.** ANTES de correr, abre `RESULTADOS.md` y llena la sección "Predicción". Luego:
   ```
   uv run --env-file .env python run_eval.py prompts/classifier_v1.txt
   ```
   `--env-file .env` le pasa tu key solo a este comando. Con el nombre del archivo al final, el script evalúa únicamente esa versión (así puedes correr v1 aunque v2 no exista todavía). Hace 10 casos × 3 corridas = 30 llamadas y tarda unos 15-30 s. Cuesta menos de un centavo. Verás una línea por cada corrida fallida y al final la tabla por familia con su `TOTAL`.

   (Si antes de esto corres `uvx ruff check .` y ves `F401 classify imported but unused`, es porque `evaluate` todavía no llama a `classify`. Desaparece cuando completes el `TODO(2)`.)

6. **`prompts/classifier_v2.txt`: el contrato.** Escríbelo ahora, con las fallas de v1 a la vista. Debe tener las piezas de la lección, cada una en su etiqueta XML:
   - rol;
   - reglas, con el formato exacto de salida y qué hacer en los casos borde;
   - la frontera de datos: lo de dentro de `<message>` es dato, no instrucciones;
   - ejemplos few-shot: **al menos uno por categoría**, con el output en el formato EXACTO que exige tu regla (en la lección viste que los ejemplos ganan a las reglas).

   Una restricción para que el experimento sea honesto: **tus ejemplos no pueden ser copias de tus casos de prueba.** Si el prompt trae la respuesta de un caso, ese caso ya no mide nada: es como un examen con las respuestas pegadas.

7. **Corre las dos versiones juntas:**
   ```
   uv run --env-file .env python run_eval.py
   ```
   Sin argumentos evalúa v1 y luego v2, en ese orden. Son 60 llamadas, unos 30-60 s. Vuelves a correr v1 a propósito: el modelo no es determinista y ahora ves si sus fallas se repiten.

8. **Llena `RESULTADOS.md`**: la tabla con los números del paso 7, y en "¿Cuál rinde mejor y por qué?", por cada familia, **qué pieza del contrato causó la diferencia**. Esa frase, no el número, es lo que se evalúa.

9. **Ruff antes de decir "listo":**
   ```
   uvx ruff check .
   ```
   Salida esperada: `All checks passed!`.

## Convención de código

Variables, funciones, docstrings y comentarios en inglés (estándar del repo). Los prompts y los mensajes de `cases.json` también en inglés: son texto que consume el sistema, no apuntes.

## Cómo se evalúa

El tutor corre los comandos de los pasos 2, 3, 7 y 9, y lee los dos prompts, `cases.json` y `RESULTADOS.md`. Criterio:
- las dos funciones cumplen su contrato;
- hay 10 casos en 3 familias, con un `happy` por categoría;
- v2 tiene todas las piezas del contrato y sus ejemplos no se solapan con los casos;
- `RESULTADOS.md` explica la diferencia con causas, no solo con números.

## Pistas

Pídelas al tutor: son escalonadas y no están escritas aquí a propósito.
