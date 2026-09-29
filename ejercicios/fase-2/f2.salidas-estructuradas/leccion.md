# f2.salidas-estructuradas — Salidas estructuradas · Lección

*Lee este documento completo y responde las preguntas del final en el chat, una por una, para irlas desarrollando con el tutor.*

Archivos de esta carpeta que usa la lección:

| Archivo | Qué es | ¿Necesita API key? |
|---|---|---|
| `intake.py` | El modelo Pydantic `Intake`: el contrato que debe cumplir cada extracción. Lo comparten las tres demos. | No |
| `demo_parse_failures.py` | Demo 1: siete respuestas típicas de un modelo y qué capa las rechaza. | No (offline) |
| `demo_structured_parse.py` | Demo 2: una llamada real con *structured outputs* y `messages.parse`. | **Sí** (menos de un centavo) |
| `demo_manual_retry.py` | Demo 3: el camino manual con UN reintento con retroalimentación, contra un cliente falso. | No (offline) |

---

## Por qué existe

### El problema: tu código necesita datos, el modelo produce texto

En `f2.prompting-estructurado` tu clasificador devolvía **una palabra**: `billing`, `technical`, `account` u `other`. Aun así tuviste que escribir `is_valid_format` y tu tabla tenía una columna `format_err`, porque la v1 a veces contestaba con un párrafo en vez de una palabra. Con una sola palabra, detectar el problema era fácil: `output in CATEGORIES`.

Ahora el caso real del capstone (`docs/capstone.md`, sección 4.2). Llega el correo de un cliente potencial de la firma, en prosa:

> *"Hi, my name is Laura Gomez. On March 3rd a delivery truck rear-ended my car at a red light and my neck has hurt ever since. The trucking company's insurer keeps calling me for a recorded statement. Should I give it?"*

Y tu programa necesita, a partir de eso, **cinco datos con tipo**: el nombre de la clienta (texto), el tipo de caso (uno de una lista cerrada), la fecha del incidente (una fecha de verdad, no el texto "March 3rd"), un resumen corto y la urgencia (una de tres). ¿Para qué? Para lo que viene después en el sistema: crear el expediente con un `POST /matters`, calcular el plazo de prescripción a partir de la fecha, ordenar la bandeja por urgencia. Todo eso es **código**, y el código no lee prosa: lee un diccionario con claves fijas y valores del tipo correcto.

Una **salida estructurada** es exactamente eso: una respuesta del modelo que tu programa puede convertir, sin adivinar, en un objeto con campos y tipos conocidos.

### Qué se hacía antes, y por qué era peor

1. **Expresiones regulares sobre la prosa.** Pedirle al modelo "responde con el nombre, la fecha y el tipo" y buscar los datos con regex en el texto. Se rompe con cualquier variación de redacción, igual que el protocolo casero `NECESITO_HORA` que viste en la lección de tool use.
2. **"Responde en JSON" en el prompt, y `json.loads` rezando.** Mejor, pero el modelo no está *obligado* a nada: a veces envuelve el JSON en un bloque de código de Markdown, a veces antepone "Here is the extracted data:", a veces se le olvida un campo, a veces inventa una categoría que no existe. Tu programa revienta en el `json.loads` o, peor, acepta un dato torcido y lo guarda.
3. **Trucos para forzar el formato**: empezar tú la respuesta del asistente con `{` (el *prefill* que viste en el repaso de la S36) o declarar una herramienta falsa cuyo `input_schema` es la forma que quieres y obligar al modelo a "llamarla". Funcionaban, pero eran trucos: el primero está prohibido en los modelos nuevos (devuelven un 400) y el segundo usa tool use para algo que no es una herramienta.

### La solución, en tres capas

Este tópico no es una función de la API: es una **cadena de defensa** con tres capas, y el nombre del tópico cubre las tres:

1. **Structured outputs** (salidas estructuradas de la API): le mandas a la API la forma exacta que quieres (un JSON Schema) y la API **impide físicamente** que el modelo escriba algo que no la cumpla. Resuelve la sintaxis y la forma.
2. **Validación con Pydantic** en tu código: la última aduana. Comprueba lo que la API no puede comprobar (reglas de negocio, límites de longitud) y convierte el texto en un objeto Python con tipos de verdad.
3. **Estrategia de reintento**: cuando la validación falla igual, decides si vale la pena volver a pedir, cómo pedirlo y cuántas veces, y qué haces si se agotan los intentos.

La idea que lo une todo ya la conoces de la Fase 1: **se valida en la frontera**. En FastAPI, el cuerpo de un `POST` venía de afuera y lo validabas con Pydantic antes de tocarlo. La respuesta de un LLM es exactamente eso: **una entrada externa y poco confiable**. Que la haya escrito un modelo muy capaz no cambia nada; el contrato se hace cumplir en la frontera o no se cumple.

---

## Términos que vas a ver

- **JSON**: formato de texto para datos (objetos con `{}`, listas con `[]`, strings entre comillas dobles, números, `true`/`false`/`null`). Es texto: hasta que lo conviertes, para Python es un `str`.
- **Parsear**: convertir texto con un formato (aquí JSON) en una estructura de datos del lenguaje (aquí un `dict` o un objeto). `json.loads` parsea.
- **JSON Schema**: un estándar para describir la *forma* de un JSON: qué campos tiene, de qué tipo es cada uno, cuáles son obligatorios, qué valores se permiten. Ya lo usaste como `input_schema` en tool use.
- **Contrato**: en esta lección, el conjunto de condiciones que una respuesta debe cumplir para que tu código la acepte. Aquí el contrato es el modelo Pydantic `Intake`.
- **JSON mode**: una opción de algunas APIs (OpenAI la tiene con ese nombre) que garantiza que la respuesta es JSON **sintácticamente válido**, pero NO que tenga los campos que quieres.
- **Structured outputs**: la opción de la API que garantiza que la respuesta cumple **un JSON Schema concreto** (sintaxis + forma). En la API de Anthropic se activa con el parámetro `output_config={"format": {...}}`.
- **Decodificación restringida** (*constrained decoding*): el mecanismo con el que la API cumple esa garantía: mientras el modelo genera token a token, se le prohíben los tokens que romperían el schema.
- **Gramática**: aquí, un conjunto de reglas derivado del schema que, dado lo que ya se escribió, dice qué caracteres pueden venir a continuación.
- **`messages.parse`**: método del SDK de Anthropic que hace la llamada con structured outputs a partir de una clase Pydantic y te devuelve la respuesta ya validada.
- **`parsed_output`**: el atributo de la respuesta de `messages.parse` donde queda el objeto Pydantic ya construido.
- **`model_json_schema()`**: método de clase de Pydantic que genera el JSON Schema de un modelo.
- **`anthropic.transform_schema`**: función del SDK que adapta un JSON Schema a lo que la API acepta (quita lo no soportado y lo mueve a la descripción).
- **`model_validate_json`**: método de clase de Pydantic que parsea un string JSON y valida el contrato en un solo paso. Ya lo usaste en `02-asistente-anidado`.
- **`JSONDecodeError`**: la excepción de `json.loads` cuando el texto no es JSON válido. Es un fallo de **sintaxis**.
- **`ValidationError`**: la excepción de Pydantic cuando los datos no cumplen el modelo. Puede ser por sintaxis (Pydantic también parsea) o por **contrato** (falta un campo, tipo equivocado, regla violada).
- **`stop_reason: "refusal"`**: valor de `stop_reason` que indica que el modelo se negó a responder por motivos de seguridad. Se suma a los que ya conoces (`end_turn`, `max_tokens`, `tool_use`).
- **Reintento ciego**: volver a mandar exactamente la misma request esperando que esta vez salga bien.
- **Reintento con retroalimentación** (*feedback*): volver a pedir, pero añadiendo a la conversación la respuesta mala y el error concreto, para que el modelo la corrija.
- **Tasa de parseo**: de N textos procesados, qué porcentaje terminó en un objeto válido. Es el número que pide el criterio de dominio de este tópico.
- **Strict tool use**: la misma garantía de structured outputs, pero aplicada a los **argumentos** de una herramienta (`strict: True` en la declaración de la tool).
- **`uv run --with`**: forma de ejecutar un script en un entorno temporal con paquetes que no están en ningún `pyproject.toml`. Lo usarás para correr las demos.

---

## Concepto

### 1. Dos capas de "válido": sintaxis y contrato

Antes de ver ninguna API hay que separar dos preguntas que un principiante mezcla:

1. **¿Es JSON?** — pregunta de **sintaxis**. `{"a": 1}` sí; `{"a": 1` (le falta la llave) no; `Here is it: {"a": 1}` tampoco (hay texto antes de la llave). La responde `json.loads`: o te da un `dict`, o lanza `JSONDecodeError`.
2. **¿Es el JSON que yo necesito?** — pregunta de **contrato**. `{"color": "red"}` es JSON perfecto, pero si esperabas un `Intake`, no le sirve a nadie. La responde Pydantic: o te da un `Intake`, o lanza `ValidationError`.

Analogía: una carta. La sintaxis es que llegue en un sobre cerrado, con estampilla y dirección legible: el correo la puede entregar. El contrato es que adentro venga lo que pediste: el formulario firmado, con todas las casillas llenas. Un sobre impecable con una servilleta adentro pasa la primera revisión y falla la segunda. *Dónde se rompe la analogía:* con una carta, abrir el sobre y leer el contenido son dos pasos que haces tú por separado. Con Pydantic, `model_validate_json` hace **los dos de una vez**: si el texto ni siquiera es JSON, también lanza `ValidationError` (con tipo `json_invalid`), no `JSONDecodeError`. La demo 1 te lo muestra.

La demo 1 recorre siete respuestas "típicas" de un modelo y te dice, para cada una, qué capa la acepta y cuál la rechaza. **No la corras todavía**: la pregunta 1 del final te pide predecirlo primero.

### 2. Nivel 0 — pedir JSON en el prompt

Es lo que haría cualquiera la primera vez: *"Extract the data and answer in JSON with the keys client_name, case_type..."*. Funciona muchas veces. Falla de estas formas, todas reales:

| Falla | Ejemplo | Por qué ocurre |
|---|---|---|
| Bloque de código | ` ```json\n{...}\n``` ` | El modelo aprendió de millones de chats donde el JSON se muestra así, y predice el patrón más probable (lo que viste en `f2.como-funciona-llm`). |
| Preámbulo | `Here is the extracted data:\n{...}` | Mismo motivo: en el entrenamiento, las respuestas amables llevan frase de entrada. |
| Truncado | `{"client_name": "Laura", "case` | Se alcanzó `max_tokens` a mitad de la respuesta. |
| Categoría inventada | `"case_type": "car accident"` | El modelo describió el caso con sus palabras en vez de elegir de tu lista. |
| Campo faltante | falta `urgency` | Nada lo obligaba a incluirlo. |
| Dato imposible | `"incident_date": "2031-01-15"` | Ningún formato lo impide: es una fecha válida... en el futuro. |

Las tres primeras son fallos de **sintaxis**. Las tres últimas pasan `json.loads` sin problema y son fallos de **contrato**. Con un buen prompt (lo que hiciste en `f2.prompting-estructurado`) bajan mucho, pero no llegan a cero, y un sistema que procesa cientos de correos al día con un 2% de fallo rompe varios expedientes diarios.

### 3. Nivel 1 — JSON mode

Algunas APIs ofrecen un interruptor que garantiza **solo la sintaxis**: la respuesta será JSON que `json.loads` acepta. Eso elimina las tres primeras filas de la tabla, pero no las tres últimas: el JSON puede traer cualquier clave con cualquier valor. En OpenAI se llama literalmente *JSON mode* (`response_format={"type": "json_object"}`). La API de Anthropic no tiene un interruptor con ese nombre: la gente usaba los dos trucos de "Por qué existe" (prefill con `{` o la herramienta falsa). Hoy, en ambas APIs, JSON mode es la opción vieja; lo que se usa es el nivel 2.

### 4. Nivel 2 — structured outputs: la API impide escribir lo que no cumple el schema

Aquí está la idea central del tópico, y se entiende con lo que ya sabes de `f2.como-funciona-llm`.

Recuerda cómo genera un modelo: en cada paso calcula una **probabilidad para cada token posible** del vocabulario (decenas de miles) y elige uno. Luego repite con ese token añadido. Nada en ese proceso "sabe" de JSON: si el token más probable es "Here", sale "Here".

Con structured outputs pasa esto:

1. Tú mandas el JSON Schema en la request.
2. La API lo **compila a una gramática**: un autómata que, dado lo que ya se escribió, sabe qué caracteres son legales a continuación. Por ejemplo: al principio, lo único legal es `{`. Después de `{"case_type": "`, lo único legal es el comienzo de `personal_injury`, `contract_dispute`, `employment` u `other`.
3. En cada paso de generación, **antes de elegir el token**, la API pone en cero la probabilidad de todos los tokens que la gramática prohíbe, y el modelo elige entre los que quedan.

Resultado: el modelo **no puede** escribir "Here", ni `car accident` en `case_type`, ni cerrar el objeto sin `urgency`. No es que se le pida con más fuerza: es que esos tokens dejan de existir para él en ese momento.

Analogía: un tren sobre rieles frente a un auto. El auto (nivel 0) puede ir a cualquier parte; le dices "ve a la estación" y casi siempre llega, pero a veces se desvía. El tren (nivel 2) solo puede ir por donde hay riel: en cada cruce, las vías que no llevan a la estación están cortadas. *Dónde se rompe la analogía:* los rieles garantizan **por dónde** va el tren, no **qué lleva adentro**. El schema garantiza que `case_type` sea una de cuatro palabras; no garantiza que sea la **correcta**. Un accidente de tránsito clasificado como `employment` cumple el schema perfectamente.

**Qué garantiza y qué no.** Esta lista es lo más importante de la lección:

| Garantiza | NO garantiza |
|---|---|
| JSON sintácticamente válido | Que los valores sean **correctos** (semántica) |
| Todos los campos de `required`, sin campos extra | Reglas que el schema de la API no puede expresar (ver abajo) |
| Tipos correctos (`string`, `integer`, `null`...) | Nada si la respuesta se **trunca** por `max_tokens` |
| Valores de `enum` dentro de la lista | Nada si el modelo **se niega** (`stop_reason: "refusal"`) |

**Lo que el schema de la API no puede expresar.** La gramática soporta tipos, `enum`, `anyOf`, objetos anidados y algunos formatos de string (`date`, `email`, `uuid`...). **No soporta** límites numéricos (`minimum`, `maximum`), límites de longitud (`minLength`, `maxLength`) ni schemas recursivos, y exige `additionalProperties: false` en cada objeto. Y, por supuesto, no puede ejecutar tus `field_validator` de Python: la regla "la fecha no puede estar en el futuro" vive en tu código, no en el schema. ¿Qué hace el SDK con tu `Field(max_length=160)`? Lo **saca** del schema que viaja a la API y lo pega como texto en la descripción del campo (`{maxLength: 160}`), para que el modelo al menos lo lea, y luego valida la longitud en tu lado. Lo verás impreso en la demo 2. Consecuencia directa: **aunque uses structured outputs, la validación puede fallar**. Por eso existe el nivel 3.

**Un efecto secundario peligroso: la gramática obliga a inventar.** Si un campo es obligatorio y no admite `null`, la gramática **exige** que el modelo escriba un valor. Si el correo no menciona ninguna fecha y declaraste `incident_date: date`, el modelo no tiene salida: tiene que escribir *alguna* fecha. Es una alucinación **causada por tu schema**. La pregunta 2 va de esto.

**Detalles prácticos:**
- La primera request con un schema nuevo tarda un poco más (la API compila la gramática); después queda en caché 24 horas.
- Funciona en los modelos actuales, incluido `claude-haiku-4-5`, que es el que usas.
- No se combina con prefill (la API lo rechaza), y de todos modos los modelos nuevos ya no aceptan prefill: structured outputs es la forma actual de controlar el formato.

*Pausa para predecir:* si el schema garantiza la forma, ¿por qué `intake.py` declara `case_type` como `Literal[...]` en Pydantic además de como `enum` en el schema? Piénsalo antes de seguir. (Respuesta: el `enum` del schema **sale** del `Literal`: Pydantic lo genera a partir de él. No lo escribes dos veces; escribes la clase y el schema se deriva. Y el `Literal` sigue validando en tu lado, que es lo que te protege si mañana alguien quita `output_config` de la llamada.)

### 5. Nivel 3 — Pydantic como última aduana, y los dos caminos del SDK

El SDK de Anthropic te da dos formas de usar structured outputs. Las dos terminan en Pydantic; cambian en cuánto control tienes.

**Camino cómodo: `client.messages.parse(..., output_format=Intake)`.** Le pasas la **clase**. El SDK genera el schema (`Intake.model_json_schema()`), lo adapta (`transform_schema`), lo manda en `output_config`, recibe la respuesta, la valida con Pydantic y te deja el objeto en `response.parsed_output`. Es la demo 2.

Su trampa, comprobada por el tutor ejecutándolo: si la validación falla, `parse` **lanza `ValidationError`**... y lo hace igual en tres situaciones muy distintas:
- la respuesta rompió una regla (por ejemplo, un `summary` de 230 caracteres),
- la respuesta se **truncó** por `max_tokens` (error `json_invalid`: el JSON está cortado),
- el modelo **se negó** (`refusal`) y escribió una frase en vez de JSON (también `json_invalid`).

Como la excepción sale de dentro de `parse`, **nunca recibes el objeto respuesta**: no puedes mirar su `stop_reason` para saber cuál de las tres pasó. Y la decisión correcta es distinta en cada caso (sección 6).

**Camino manual: `client.messages.create(..., output_config=...)` + tu propia validación.** Construyes tú el `output_config`:

```python
OUTPUT_CONFIG = {
    "format": {
        "type": "json_schema",
        "schema": anthropic.transform_schema(Intake.model_json_schema()),
    }
}
```

Llamas a `create` con él, **miras `stop_reason` primero**, y solo si es `"end_turn"` validas el texto con `Intake.model_validate_json(...)`. Es más código, pero cada fallo llega por un camino distinto y puedes reaccionar distinto. Es la demo 3.

| | `messages.parse` | `create` + `output_config` + `model_validate_json` |
|---|---|---|
| Código | Mínimo | Más |
| Schema | Lo genera el SDK desde la clase | Lo generas tú (dos llamadas) |
| Resultado | `response.parsed_output` (ya es `Intake`) | Tú llamas a `model_validate_json` |
| Truncado / refusal | `ValidationError`, sin acceso a la respuesta | Lo ves en `stop_reason` antes de validar |
| Cuándo usarlo | Prototipos, casos donde cualquier fallo se trata igual | Cuando necesitas una estrategia de reintento que distinga causas |

### 6. Reintentos: dos capas que no hay que confundir

En `f2.llamadas-api` escribiste reintentos con backoff exponencial. Esos siguen existiendo, pero son **otra capa**:

- **Capa de transporte** (la de `01-cliente-anthropic`): la request **no obtuvo respuesta útil** de la API: 429, 5xx, timeout, conexión caída. La respuesta correcta es esperar y repetir **la misma** request. El modelo nunca llegó a contestar, así que no hay nada que corregir.
- **Capa de contenido** (la nueva): la API **sí respondió**, con un 200, pero lo que escribió el modelo no sirve. Repetir a ciegas la misma request es tirar una moneda otra vez; tiene más sentido **decirle al modelo qué estuvo mal**.

Es el mismo límite que te costó ver con `is_error` en la S35: no todo fallo es del mismo tipo, y cada tipo tiene su dueño.

**Reintento con retroalimentación**, paso a paso (es lo que hace la demo 3):
1. Llamas al modelo; la respuesta no pasa la validación.
2. Añades a `messages` la respuesta mala como turno `assistant` (para que el modelo vea qué escribió).
3. Añades un turno `user` con el error concreto de Pydantic y la instrucción de corregir.
4. Llamas otra vez, con el schema, y validas de nuevo.

Por qué funciona mejor que el reintento ciego: el error de Pydantic es muy específico (`incident_date: Value error, incident_date cannot be in the future`). Con él, el modelo sabe **qué** campo arreglar y **por qué**; sin él, repite el mismo razonamiento que lo llevó a equivocarse. Su costo: la request crece (recuerda de `f2.llamadas-api` que la API es *stateless*: cada llamada reenvía la conversación entera), así que cada reintento cuesta más que el anterior.

**Reglas de una estrategia de reintento sana:**
- **Tope de intentos**. Sin tope, un caso imposible (un correo en blanco, un texto en otro idioma que el modelo rechaza) te deja en un bucle infinito que además cuesta dinero.
- **Al agotar los intentos, se lanza una excepción**. Nunca se devuelve `None` en silencio: es exactamente el bug de tu `ask_with_retries` en la S29 y del `for` sin `raise` de la S36.
- **Cada causa, su reacción.** No todo fallo merece reintento (la pregunta 3 te pide clasificarlas).

### 7. Tasa de parseo: qué mide y qué no

El criterio de dominio de este tópico pide *"extraer datos de 20 textos libres hacia un modelo Pydantic con tasa de parseo del 100%, incluyendo estrategia de reintento"*. Tasa de parseo = textos que terminaron en un `Intake` válido ÷ textos procesados. El 100% significa que **ninguno se pierde**: algunos pueden necesitar un segundo intento, y eso se registra (cuántos, por qué), pero todos terminan validados.

Lo que la tasa de parseo **no** mide: si los datos son **correctos**. Un `Intake` con `case_type="employment"` para un choque de tránsito parsea perfecto. Medir corrección es otra cosa (comparar contra respuestas esperadas, como hiciste con `cases.json`), y la harás en serio en la Fase 4 con evals. Aquí, igual que en tu `RESULTADOS.md` de la S34: no atribuyas a una métrica más de lo que mide.

### 8. Lo mismo en herramientas y en OpenAI (solo para ubicarte)

- **Strict tool use.** Si en tool use añades `"strict": True` a la declaración de una herramienta (con `additionalProperties: False` en su `input_schema`), la API aplica la misma gramática a los **argumentos** que el modelo pone en el bloque `tool_use`. Es la versión de structured outputs para herramientas; te servirá en el capstone.
- **OpenAI**: *JSON mode* es `response_format={"type": "json_object"}` (solo sintaxis); structured outputs es `response_format={"type": "json_schema", ...}` con `"strict": true`, y su SDK también tiene un `parse` que recibe una clase Pydantic. Mismas ideas, otros nombres; lo tocarás en `f2.multi-proveedor`.

---

## Demo mínima

### Cómo correr las demos

Las demos no tienen `pyproject.toml` propio. Se corren con `uv run --with`, desde **esta carpeta** (`ejercicios/fase-2/f2.salidas-estructuradas/`):

```bash
cd ejercicios/fase-2/f2.salidas-estructuradas
uv run --with pydantic python demo_parse_failures.py
```

Qué hace `uv run --with pydantic python demo_parse_failures.py`, pieza a pieza:
- `uv run` ejecuta un comando dentro de un entorno de Python gestionado por uv.
- `--with pydantic` le dice: "ese entorno debe tener `pydantic`". Como aquí no hay proyecto, uv arma un **entorno temporal** con ese paquete (la primera vez lo descarga y verás líneas como `Installed 14 packages in 492ms`; las siguientes lo toma de su caché y no imprime nada de eso). No modifica ningún archivo de la carpeta.
- `python demo_parse_failures.py` es el comando que corre dentro de ese entorno.

El comando es idéntico en zsh (tu Mac) y en PowerShell (Windows).

¿Por qué no un `uv init` como en los ejercicios? Porque estas demos son para leer y correr, no un proyecto que vaya a crecer; `--with` evita crear un `pyproject.toml` y un `.venv` que no sirven para nada después. En la sesión de ejercicio sí harás `uv init`.

Las demos importan `intake.py` con `from intake import Intake`. Eso funciona porque Python busca módulos en la carpeta del script que ejecutas; si corres el comando **desde otra carpeta** (`python ejercicios/.../demo_parse_failures.py`), también funciona, porque lo que cuenta es la carpeta del script, no la tuya. Lo que sí rompe el import es copiar una demo sola a otro lado sin `intake.py`.

---

### Pieza 0 — `intake.py`: el contrato

```python
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator

CaseType = Literal["personal_injury", "contract_dispute", "employment", "other"]
Urgency = Literal["low", "medium", "high"]


class Intake(BaseModel):
    """Structured data extracted from a prospective client's free-text message."""

    client_name: str = Field(description="Full name of the person writing, as they wrote it.")
    case_type: CaseType = Field(description="Legal area of the problem. Use 'other' if none fits.")
    incident_date: date | None = Field(
        description="Date of the incident (YYYY-MM-DD), or null if the message gives no date."
    )
    summary: str = Field(
        max_length=160, description="One English sentence describing what happened."
    )
    urgency: Urgency = Field(
        description="high if a deadline or ongoing harm is mentioned, low if purely informational, else medium."
    )

    @field_validator("incident_date")
    @classmethod
    def reject_future_dates(cls, value: date | None) -> date | None:
        """An incident cannot have happened after today."""
        if value is not None and value > date.today():
            raise ValueError("incident_date cannot be in the future")
        return value
```

Línea por línea:
- `from datetime import date` — el tipo `date` de Python: una fecha sin hora. Declarar un campo como `date` hace que Pydantic convierta el string `"2026-03-03"` en un objeto `date(2026, 3, 3)` con el que se puede operar (restar fechas, compararlas). Sin él, tendrías un `str` y la comparación con "hoy" sería entre textos.
- `from typing import Literal` — `Literal[...]` restringe un campo a una lista cerrada de valores exactos. Lo usaste en la Fase 1.
- `from pydantic import BaseModel, Field, field_validator` — la clase base de todos los modelos, la función para añadir metadatos a un campo y el decorador de validación por campo. Los tres los conoces de `f1.pydantic-validacion`.
- `CaseType = Literal[...]` y `Urgency = Literal[...]` — un **alias de tipo**: le das nombre a un tipo para reutilizarlo y leerlo mejor. `case_type: CaseType` significa exactamente lo mismo que escribir el `Literal` completo en la línea del campo. Si mañana añades `"immigration"`, se cambia en un solo lugar.
- `class Intake(BaseModel):` — el contrato.
- La **docstring de la clase** (`"""Structured data extracted..."""`) no es solo documentación: Pydantic la copia al JSON Schema como `description` del objeto. O sea, **el modelo la lee**. Lo mismo pasa con cada `Field(description=...)`. En structured outputs, las descripciones son parte del prompt: una descripción vaga produce valores vagos.
- `client_name: str = Field(description=...)` — un campo de texto obligatorio. Ojo con un detalle de Pydantic: `Field(description=...)` **sin** `default` sigue siendo obligatorio. Solo sería opcional si le dieras un valor por defecto.
- `case_type: CaseType = Field(...)` — de aquí sale el `"enum": ["personal_injury", ...]` del schema. La descripción le da al modelo la salida de emergencia: `other` si no encaja nada.
- `incident_date: date | None = Field(...)` — obligatorio **pero** puede ser `null`. Son dos cosas distintas: "obligatorio" es que la clave tiene que estar; "admite `None`" es qué valores puede tener. En el schema queda como `anyOf: [{"type": "string", "format": "date"}, {"type": "null"}]`. Esa `| None` es la que le permite al modelo decir "no sé" sin inventar (sección 4).
- `summary: str = Field(max_length=160, ...)` — límite de longitud. Recuerda: la API **no** puede hacer cumplir este límite; el SDK lo mueve a la descripción y lo valida en tu lado.
- `urgency: Urgency = Field(...)` — la descripción da un criterio para cada valor. Sin criterio, "urgencia" es una opinión y cada llamada opinaría distinto.
- `@field_validator("incident_date")` + `@classmethod` — la regla de negocio que ningún schema puede expresar. Se ejecuta **después** de que Pydantic convirtió el string en `date` (el modo por defecto es `after`), por eso `value` ya es un `date` o `None`.
- `if value is not None and value > date.today():` — el `is not None` va primero porque comparar `None > date` lanzaría `TypeError`. Gracias a que `and` se detiene en cuanto encuentra un `False` (evaluación en cortocircuito), la segunda parte nunca se evalúa con `None`.
- `raise ValueError(...)` — dentro de un validador, lanzar `ValueError` es la forma de decir "no cumple". Pydantic la captura y la convierte en un error dentro de un `ValidationError`.
- `return value` — un validador **debe** devolver el valor. Si lo olvidas, el campo queda en `None` sin ningún error (el mismo tipo de fallo silencioso que un `return` olvidado en cualquier función).

---

### Demo 1 — `demo_parse_failures.py`: qué capa rechaza qué (offline)

```python
import json

from pydantic import ValidationError

from intake import Intake

BASE = {
    "client_name": "Laura Gomez",
    "case_type": "personal_injury",
    "incident_date": "2026-03-03",
    "summary": "Rear-ended by a delivery truck at a red light.",
    "urgency": "high",
}
CLEAN = json.dumps(BASE)

RAW_OUTPUTS = {
    "clean": CLEAN,
    "code fence": f"```json\n{CLEAN}\n```",
    "preamble": f"Here is the extracted data:\n{CLEAN}",
    "truncated": CLEAN[:60],
    "wrong category": json.dumps({**BASE, "case_type": "car accident"}),
    "missing field": json.dumps({k: v for k, v in BASE.items() if k != "urgency"}),
    "future date": json.dumps({**BASE, "incident_date": "2031-01-15"}),
}

for label, raw in RAW_OUTPUTS.items():
    print(f"--- {label}")

    # Layer 1 — syntax: is this text JSON at all?
    try:
        json.loads(raw)
        print("  json.loads -> OK")
    except json.JSONDecodeError as exc:
        print(f"  json.loads -> JSONDecodeError: {exc.msg}")

    # Layer 2 — contract: does it have the fields, types and rules of Intake?
    try:
        intake = Intake.model_validate_json(raw)
        print(f"  Intake     -> OK: {intake.case_type}, {intake.incident_date}")
    except ValidationError as exc:
        first = exc.errors()[0]
        print(f"  Intake     -> ValidationError [{first['type']}] {first['loc']}: {first['msg']}")
```

Línea por línea:
- `import json` — el módulo estándar para JSON. Lo usamos para dos cosas: `json.dumps` (dict → texto JSON) para **fabricar** las respuestas falsas, y `json.loads` (texto → dict) para la capa 1.
- `from pydantic import ValidationError` — la excepción que vamos a capturar en la capa 2.
- `from intake import Intake` — el contrato de la pieza 0.
- `BASE = {...}` — una extracción correcta, como diccionario de Python. Es el punto de partida de todas las variantes.
- `CLEAN = json.dumps(BASE)` — la misma extracción como **texto JSON**. Esto es lo que devuelve un modelo: siempre texto, nunca un dict.
- `RAW_OUTPUTS = {...}` — un diccionario `etiqueta -> texto crudo`. Cada entrada simula una de las fallas de la tabla de la sección 2. Las construcciones nuevas:
  - `f"```json\n{CLEAN}\n```"` — envuelve el JSON en un bloque de código de Markdown, como hacen los modelos en un chat.
  - `CLEAN[:60]` — *slicing*: los primeros 60 caracteres del string. Simula una respuesta cortada por `max_tokens`.
  - `{**BASE, "case_type": "car accident"}` — **desempaquetado de diccionario**: `**BASE` copia todas las claves de `BASE` en un dict nuevo, y la clave que escribes después **pisa** la copiada. Resultado: un dict nuevo igual a `BASE` salvo `case_type`. `BASE` no se modifica (y eso importa: si hicieras `BASE["case_type"] = ...`, cambiarías la base de todas las variantes siguientes — la familia del *aliasing* de la S33).
  - `{k: v for k, v in BASE.items() if k != "urgency"}` — **comprensión de diccionario**: recorre los pares clave/valor de `BASE` y se queda con todos menos `urgency`. Es un `for` con `if` que construye un dict en una expresión.
- `for label, raw in RAW_OUTPUTS.items():` — recorre las siete variantes; `.items()` entrega pares `(etiqueta, texto)`.
- **Capa 1**: `json.loads(raw)` intenta parsear. Si puede, imprime `OK` (el dict resultante se descarta: solo nos interesa si fue posible). Si no, lanza `json.JSONDecodeError`, y `exc.msg` es la descripción corta del problema (por ejemplo `Expecting value`: "esperaba un valor JSON y encontré otra cosa").
- **Capa 2**: `Intake.model_validate_json(raw)` parsea **y** valida. Si todo cumple, devuelve un `Intake` y se imprimen dos de sus campos (fíjate que `intake.incident_date` se imprimirá como fecha, porque ya es un `date`).
- `exc.errors()` — un `ValidationError` puede traer **varios** errores a la vez (por ejemplo, dos campos mal). `.errors()` los devuelve como lista de diccionarios; tomamos el primero con `[0]`. Cada error tiene:
  - `type`: el código del error (`missing`, `literal_error`, `json_invalid`, `value_error`...). Es lo que conviene usar en código para decidir qué hacer.
  - `loc`: *location*, una **tupla** con la ruta al campo que falló, por ejemplo `('urgency',)`. Si el error es de todo el texto (no de un campo), `loc` es la tupla vacía `()`.
  - `msg`: el mensaje legible para humanos.

**Qué verás al correrla:** siete bloques de tres líneas, uno por variante: la etiqueta (`--- clean`, `--- code fence`...), el veredicto de `json.loads` y el veredicto de `Intake`. Cada veredicto es `OK` o una excepción con su detalle. **Qué bloque dice qué es la pregunta 1**: predícelo antes de correrla.

---

### Demo 2 — `demo_structured_parse.py`: structured outputs con `messages.parse` (necesita API key)

```python
import json
from datetime import date

import anthropic

from intake import Intake

MESSAGE = (
    "Hi, my name is Laura Gomez. On March 3rd a delivery truck rear-ended my car "
    "at a red light and my neck has hurt ever since. The trucking company's insurer "
    "keeps calling me for a recorded statement. Should I give it?"
)

# What travels to the API: Pydantic writes the JSON Schema, the SDK adapts it.
schema = anthropic.transform_schema(Intake.model_json_schema())
print("summary, as the API sees it:")
print(json.dumps(schema["properties"]["summary"], indent=2))

client = anthropic.Anthropic()

# parse() = create() + schema from the class + validation of the answer.
# If the answer breaks the contract it raises pydantic.ValidationError.
response = client.messages.parse(
    model="claude-haiku-4-5",
    max_tokens=1024,
    system=f"You extract intake data for a law firm. Today is {date.today().isoformat()}.",
    messages=[{"role": "user", "content": f"<message>\n{MESSAGE}\n</message>"}],
    output_format=Intake,
)

intake = response.parsed_output
print(f"\nraw text:   {response.content[0].text}")
print(f"parsed:     {intake!r}")
print(f"date type:  {type(intake.incident_date).__name__}")
print(f"stop_reason={response.stop_reason}  in={response.usage.input_tokens}  out={response.usage.output_tokens}")
```

Línea por línea:
- `MESSAGE = (...)` — el correo de la clienta. Los paréntesis con varios strings seguidos son **concatenación implícita**: Python une strings literales adyacentes en uno solo. Sirve para partir un texto largo en varias líneas sin `+`. Fíjate en el espacio al final de cada trozo: sin él, las palabras quedarían pegadas (`carat`).
- `Intake.model_json_schema()` — Pydantic genera el JSON Schema de la clase, como `dict`.
- `anthropic.transform_schema(...)` — el SDK lo adapta a lo que acepta la API: añade `additionalProperties: false` a cada objeto y quita lo no soportado (como `maxLength`), moviéndolo a la descripción. `messages.parse` hace exactamente esto por dentro; aquí lo llamamos a mano **solo para imprimirlo** y que veas qué recibe la API.
- `print(json.dumps(schema["properties"]["summary"], indent=2))` — imprime el schema del campo `summary` con sangría de 2 espacios. Verás que ya no hay `maxLength` y que la descripción termina en `{maxLength: 160}`.
- `client = anthropic.Anthropic()` — el cliente, que lee la key de la variable de entorno `ANTHROPIC_API_KEY` (como en `f2.llamadas-api`).
- `client.messages.parse(...)` — como `messages.create`, con una diferencia: el parámetro `output_format=Intake`. Recibe la **clase** (no una instancia, no un dict). El SDK construye el `output_config` con el schema, hace la llamada y valida la respuesta.
- `system=f"... Today is {date.today().isoformat()}."` — el mensaje dice "March 3rd" **sin año**. El modelo no tiene reloj (lección de tool use), así que sin la fecha de hoy no sabría qué año suponer. `.isoformat()` convierte la fecha a texto `YYYY-MM-DD`.
- `f"<message>\n{MESSAGE}\n</message>"` — el mensaje del usuario va entre etiquetas, como hiciste en la v2 del clasificador: delimita qué es entrada y qué es instrucción (defensa contra inyección de `f2.prompting-estructurado`).
- `max_tokens=1024` — holgado a propósito: si fuera muy bajo, el JSON se truncaría y `parse` lanzaría `ValidationError` (sección 5).
- `response.parsed_output` — el `Intake` ya construido y validado.
- `response.content[0].text` — el texto crudo que escribió el modelo: el JSON como string. Se imprime para que veas que, por debajo, el modelo sigue escribiendo **texto**; lo nuevo es que ese texto está garantizado. (Aquí `[0]` es seguro porque sin herramientas ni *thinking* la respuesta trae un único bloque de texto; en general se filtra por `type`, como aprendiste.)
- `{intake!r}` — `!r` usa `repr()`: muestra el objeto con su clase y campos, `Intake(client_name='Laura Gomez', ...)`.
- `type(intake.incident_date).__name__` — imprime `date`: la prueba de que Pydantic convirtió el string en un objeto fecha.
- La última línea: `stop_reason` y los tokens de entrada y salida, como en tus demos de `f2.llamadas-api`. El schema viaja en **cada** llamada; si quieres ver cuánto suma a la entrada, compara el `in=` con el de una llamada igual sin `output_format`.

**Cómo correrla.** Necesita tu API key. Tienes dos formas:
- Si en tu Mac la key está exportada en `~/.zshrc` (lo que se acordó en la S27), basta con:
  ```bash
  uv run --with anthropic --with pydantic python demo_structured_parse.py
  ```
- Si la tienes en el `.env` del clasificador, apúntale con `--env-file` (la ruta es relativa a esta carpeta):
  ```bash
  uv run --with anthropic --with pydantic --env-file ../f2.prompting-estructurado/01-clasificador-tickets/.env python demo_structured_parse.py
  ```
  Recuerda lo que descubriste en la S30: si la variable **ya está exportada** en tu terminal, esa gana sobre la del `--env-file`.

**Qué salida esperar** (la forma es fija; el texto exacto de `summary` y la urgencia los decide el modelo en cada corrida):

```
summary, as the API sees it:
{
  "type": "string",
  "description": "One English sentence describing what happened.\n\n{maxLength: 160}",
  "title": "Summary"
}

raw text:   {"client_name": "Laura Gomez", "case_type": "personal_injury", "incident_date": "2026-03-03", "summary": "...", "urgency": "high"}
parsed:     Intake(client_name='Laura Gomez', case_type='personal_injury', incident_date=datetime.date(2026, 3, 3), summary='...', urgency='high')
date type:  date
stop_reason=end_turn  in=...  out=...
```

Si ves `anthropic.AuthenticationError: Error code: 401`, la key no está llegando o no es válida (es el error permanente de tu `.env.broken` de la S30). Si ves `ValidationError`, léelo con lo de la sección 5: ¿se truncó, se negó o rompió una regla?

---

### Demo 3 — `demo_manual_retry.py`: el camino manual con un reintento con retroalimentación (offline)

```python
import json
from types import SimpleNamespace
from typing import Any

import anthropic
from pydantic import ValidationError

from intake import Intake

OUTPUT_CONFIG = {
    "format": {
        "type": "json_schema",
        "schema": anthropic.transform_schema(Intake.model_json_schema()),
    }
}

GOOD = {
    "client_name": "Laura Gomez",
    "case_type": "personal_injury",
    "incident_date": "2026-03-03",
    "summary": "Rear-ended by a delivery truck at a red light.",
    "urgency": "high",
}
BAD = {**GOOD, "incident_date": "2031-03-03"}


def fake_response(text: str, stop_reason: str = "end_turn") -> SimpleNamespace:
    """Build one fake API response, shaped like the SDK's Message."""
    return SimpleNamespace(stop_reason=stop_reason, content=[SimpleNamespace(type="text", text=text)])


class FakeClient:
    """Replays scripted responses and records a snapshot of each request."""

    def __init__(self, responses: list[SimpleNamespace]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs: Any) -> SimpleNamespace:
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        return self._responses.pop(0)


client = FakeClient([fake_response(json.dumps(BAD)), fake_response(json.dumps(GOOD))])
messages: list[dict[str, Any]] = [
    {"role": "user", "content": "<message>\nHi, my name is Laura Gomez...\n</message>"}
]


def ask() -> str:
    """One call with the schema attached; returns the raw text or raises."""
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        messages=messages,
        output_config=OUTPUT_CONFIG,
    )
    if response.stop_reason != "end_turn":
        raise RuntimeError(f"no usable answer, stop_reason={response.stop_reason}")
    return response.content[0].text


raw = ask()
try:
    intake = Intake.model_validate_json(raw)
except ValidationError as exc:
    print(f"attempt 1 rejected: {exc.errors()[0]['msg']}")
    messages.append({"role": "assistant", "content": raw})
    messages.append(
        {
            "role": "user",
            "content": f"Your JSON failed validation:\n{exc}\nReturn the corrected JSON.",
        }
    )
    raw = ask()
    intake = Intake.model_validate_json(raw)

print(f"accepted:   {intake!r}")
print(f"API calls:  {len(client.calls)}")
print(f"messages sent in each call: {[len(call['messages']) for call in client.calls]}")
```

Por qué es offline: un reintento real solo ocurre cuando el modelo se equivoca, y eso no se puede provocar a voluntad. Un cliente falso que devuelve primero una respuesta mala y después una buena hace que el camino del reintento se ejecute **siempre**, gratis y sin red. Es el mismo patrón `FakeClient` de los tests de `01-agente-notas`.

Línea por línea:
- `OUTPUT_CONFIG = {"format": {"type": "json_schema", "schema": ...}}` — lo que `messages.parse` construía por ti, ahora escrito a mano. `"type": "json_schema"` le dice a la API qué tipo de formato es; `"schema"` es el schema ya adaptado. Se calcula **una vez** a nivel de módulo, no en cada llamada: el schema no cambia.
- `GOOD` y `BAD` — dos extracciones. `BAD` es `GOOD` con una fecha en el futuro (mismo `{**...}` de la demo 1). Fíjate que `BAD` **cumpliría el schema de la API** (es una fecha con formato válido): solo la rechaza tu `field_validator`. Es el caso realista de fallo con structured outputs.
- `fake_response(...)` — fabrica un objeto con la misma forma que la respuesta del SDK (`stop_reason` y `content` como lista de bloques con `type` y `text`). `SimpleNamespace` es un objeto al que le pones los atributos que quieras; ya lo usaste en los tests de tool use.
- `class FakeClient` — igual al de `01-agente-notas`: `self.messages = SimpleNamespace(create=self._create)` hace que `client.messages.create(...)` funcione exactamente como con el SDK real, así que `ask()` no sabe que es falso.
- `self.calls.append({**kwargs, "messages": list(kwargs["messages"])})` — guarda lo que se envió en cada llamada. La parte `"messages": list(...)` guarda una **copia** de la lista de mensajes en ese instante. Piensa por qué hace falta antes de leer la pregunta 4.
- `self._responses.pop(0)` — saca y devuelve la primera respuesta guionada: la primera llamada recibe `BAD`, la segunda `GOOD`.
- `messages: list[dict[str, Any]] = [...]` — la conversación. Empieza con un solo mensaje `user` (acortado con `...`: en el falso da igual lo que diga).
- `def ask() -> str:` — una llamada con el schema. Los pasos, en este orden a propósito:
  1. `client.messages.create(..., output_config=OUTPUT_CONFIG)` — la llamada normal, con el formato como parámetro.
  2. `if response.stop_reason != "end_turn": raise RuntimeError(...)` — **antes de mirar el texto**, se comprueba por qué terminó. Si fue `max_tokens` o `refusal`, el texto no sirve y no tiene sentido validarlo; se lanza una excepción con la causa en el mensaje. Esto es justo lo que `messages.parse` no te deja hacer.
  3. `return response.content[0].text` — solo si terminó bien, devuelve el texto crudo.
- `raw = ask()` — primer intento.
- `try: intake = Intake.model_validate_json(raw)` — la aduana. Con `BAD`, el validador de fecha lanza.
- `except ValidationError as exc:` — el camino del reintento:
  - `print(...)` — informa qué falló (útil para medir después cuántos textos necesitaron reintento y por qué).
  - `messages.append({"role": "assistant", "content": raw})` — la respuesta mala entra a la conversación **como turno del asistente**: el modelo tiene que ver qué escribió para corregirlo.
  - `messages.append({"role": "user", "content": f"Your JSON failed validation:\n{exc}\n..."})` — el turno del usuario con el error. `{exc}` inserta el texto completo del `ValidationError`, que incluye el campo, el valor recibido y el motivo. Es la retroalimentación.
  - `raw = ask()` y `intake = Intake.model_validate_json(raw)` — segundo intento. Fíjate que este segundo `model_validate_json` **no** está dentro de un `try`: si también falla, la excepción sube y el programa se detiene. En una demo está bien; en tu ejercicio tendrás que decidir qué pasa con N intentos y qué se hace al agotarlos.
- Las tres últimas líneas imprimen el `Intake` aceptado, cuántas llamadas se hicieron y cuántos mensajes llevaba cada una.

**Cómo correrla:**

```bash
uv run --with anthropic --with pydantic python demo_manual_retry.py
```

(Necesita `anthropic` instalado solo por `transform_schema`; no se conecta a nada.)

**Salida exacta** (verificada por el tutor ejecutándola):

```
attempt 1 rejected: Value error, incident_date cannot be in the future
accepted:   Intake(client_name='Laura Gomez', case_type='personal_injury', incident_date=datetime.date(2026, 3, 3), summary='Rear-ended by a delivery truck at a red light.', urgency='high')
API calls:  2
messages sent in each call: [1, 3]
```

`[1, 3]`: la primera llamada llevó 1 mensaje; la segunda, 3 (el original + la respuesta mala + el error). Eso es el crecimiento de costo del reintento, en números.

---

## Errores típicos

1. **Mirar `stop_reason` después de `messages.parse`.** Parece prudente, pero llega tarde: si la respuesta se truncó o fue un rechazo, `parse` ya lanzó `ValidationError` con `json_invalid` y la línea del `if` nunca se ejecuta. El síntoma es un `ValidationError` que dice `EOF while parsing` (truncado) o `expected value at line 1 column 1` (el modelo escribió una frase). Si necesitas distinguir esas causas, usa el camino manual.

2. **Campo obligatorio sin `| None` para un dato que puede no estar.** No produce **ningún error**: el modelo, obligado por la gramática, inventa un valor plausible, Pydantic lo acepta y el dato falso entra a tu sistema. Es el error más caro de esta lista precisamente porque es silencioso. Regla: todo dato que el texto de entrada puede no traer se declara como `X | None`, y la descripción dice cuándo usar `null`.

3. **Creer que la API hace cumplir `max_length`, `ge`, `le` o tus validadores.** No puede (sección 4). Síntoma: un `ValidationError` con `string_too_long` o `value_error` aunque "estabas usando structured outputs". No es un bug del SDK: es la capa 3 haciendo su trabajo.

4. **Reintentar sin tope, o terminar devolviendo `None`.** Un bucle `while True` de reintentos con un texto que el modelo no puede resolver gasta tokens hasta que alguien lo mata; un `for` que termina sin `raise` devuelve `None` y el error aparece lejos, como `AttributeError: 'NoneType' object has no attribute 'case_type'`. Te pasó las dos veces en su versión de reintentos de API (S29 y S36).

5. **Reintentar un truncado con el mismo `max_tokens`.** Si la respuesta no cupo en 100 tokens, la siguiente, que además lleva más contexto, tampoco va a caber. Repetirlo es pagar el mismo fallo dos veces.

6. **Tratar el error de contenido con el backoff de la API.** Esperar 1, 2, 4 segundos antes de repetir una respuesta que rompió el contrato no mejora nada: el modelo no estaba saturado, se equivocó. El backoff es para la capa de transporte.

---

## Preguntas — respóndelas en el chat

1. **Predicción (antes de correr la demo 1).** Para cada una de las siete variantes de `RAW_OUTPUTS` (`clean`, `code fence`, `preamble`, `truncated`, `wrong category`, `missing field`, `future date`), escribe qué crees que dirá la capa 1 (`json.loads`: OK o error) y la capa 2 (`Intake`: OK o error, y si puedes, de qué `type`). Después corre `uv run --with pydantic python demo_parse_failures.py`, compara y explica en qué te equivocaste, si en algo. Termina con esto: ¿cuáles de las siete filas habrían desaparecido si esas respuestas hubieran venido de una llamada con structured outputs, y cuáles no? Justifica cada una de las que no.

2. **Diseño.** Tu compañero declara `incident_date: date` (sin `| None`) y le llega este correo: *"Hello, I was fired last month without any explanation. Do I have a case?"*. Usa structured outputs. (a) ¿Qué pasa exactamente: error de la API, `ValidationError`, u otra cosa? Explica el mecanismo con lo de la sección 4. (b) ¿Por qué ese resultado es peor que un error? (c) ¿Qué cambias en el modelo y en la descripción del campo? Y fíjate en el correo: "last month" sí es una pista de fecha. ¿Qué debería hacer el modelo con ella, y cómo se lo dirías en la descripción?

3. **Clasificar fallos.** Para cada situación, di (i) en qué capa está (transporte o contenido), (ii) si reintentas o no, y (iii) si reintentas, de qué forma (backoff, retroalimentación, otra cosa):
   - a. `ValidationError`: `summary` con 230 caracteres.
   - b. `stop_reason == "max_tokens"` con `max_tokens=100`.
   - c. `stop_reason == "refusal"`.
   - d. `anthropic.RateLimitError` (429).
   - e. El `Intake` valida perfecto pero `case_type="employment"` para un choque de tránsito.

4. **Retroalimentación y memoria.** (a) En la demo 3, ¿por qué el reintento añade la respuesta mala como turno `assistant` y el error como turno `user`, en vez de repetir exactamente la misma request? Da la razón a favor y el costo en contra (con el `[1, 3]` de la salida). (b) En `FakeClient._create`, cambia mentalmente `"messages": list(kwargs["messages"])` por `"messages": kwargs["messages"]`. ¿Qué imprimiría la última línea y por qué? (Pista de familia: S33.)
