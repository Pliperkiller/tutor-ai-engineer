# f2.tool-use — Tool use / function calling · Lección

*Lee este documento completo y responde las preguntas del final en el chat, una por una, para irlas desarrollando con el tutor.*

---

## Por qué existe

Hasta ahora, en `f2.llamadas-api` y `f2.prompting-estructurado`, tu programa y el modelo hablan así:

1. Tu código manda texto (system prompt + mensaje del usuario).
2. El modelo devuelve texto.
3. Fin.

Eso alcanza para clasificar, resumir o extraer: tareas donde **toda la información necesaria ya viaja dentro del prompt**. Pero hay una familia entera de preguntas que ese tubo no puede responder, y conviene ver exactamente por qué.

Pregúntale a un modelo "¿qué hora es en Bogotá?". Va a responder algo — y va a estar inventado. No porque sea tonto: es que **el modelo no tiene reloj**. Recuerda de `f2.como-funciona-llm` qué es realmente: una función que recibe tokens y predice el token siguiente a partir de patrones aprendidos en su entrenamiento. No tiene acceso a tu disco, ni a internet, ni a la base de datos de tu empresa, ni al reloj del sistema. Lo único que "sabe" es lo que quedó congelado en sus pesos al entrenarse, más lo que tú le pongas en el prompt de esa llamada.

Lo mismo pasa con "¿cuánto cuesta el pedido 4471 del cliente X?" (está en tu base de datos), "¿cuál es la tasa del dólar hoy?" (cambia cada minuto) o "manda este correo" (eso ni siquiera es información: es una **acción** sobre el mundo).

**Qué se hacía antes.** Dos caminos, los dos malos:

- **Meterlo todo en el prompt.** Antes de llamar al modelo, tu código adivina qué datos va a necesitar y los pega en el prompt: el catálogo entero de productos, los últimos 500 pedidos, la hora actual. Falla por dos lados: se paga como tokens de entrada en **cada** llamada (recuerda tu `cost_usd`: cada token de entrada cuesta), y además hay que adivinar de antemano qué hará falta. Si el usuario pregunta por el pedido 9999 y tú cargaste los últimos 500, el modelo no tiene el dato y — peor — lo inventa.
- **Parsear la respuesta con expresiones regulares.** Se instruía al modelo con "si necesitas la hora, responde exactamente `NECESITO_HORA`", y tu código buscaba ese string en el texto para entonces actuar. Funciona el 80% de las veces y se rompe el 20 restante: el modelo escribe `Necesito la hora.` con mayúsculas distintas, o lo mete en medio de un párrafo, o pide dos cosas a la vez y tu regex solo ve una. Es un protocolo casero, sin tipos, sin validación y sin identificadores. Exactamente el mundo que dejaste atrás cuando pasaste de strings sueltos a Pydantic en la Fase 1.

**La solución: tool use** (también llamado *function calling*). Es un protocolo **formal, con tipos y con identificadores**, integrado en la API, que funciona así: tú le declaras al modelo qué funciones existen y qué parámetros aceptan; el modelo, cuando le hace falta una, no la ejecuta ni la inventa — devuelve un **bloque estructurado** diciendo "llama a `get_current_time` con `{"timezone": "America/Bogota"}`"; tu código la ejecuta y le devuelve el resultado en otro bloque estructurado; el modelo continúa con ese dato en mano.

La frase clave, y la que más cuesta interiorizar: **el modelo nunca ejecuta nada**. Pide. Quien ejecuta siempre eres tú, en tu máquina, con tu código. El modelo es un cerebro sin manos; tool use son las manos, y las manos son tuyas.

Este tópico es la puerta de entrada a los agentes: un agente no es más que este ciclo, repetido hasta que el modelo deja de pedir herramientas.

---

## Términos que vas a ver

- **Herramienta** (*tool*): una función de tu programa que le declaras al modelo para que pueda pedir que la ejecutes. En el código es una función Python normal y corriente; lo que la hace "herramienta" es que además existe una **declaración** que el modelo ve.
- **Function calling**: otro nombre para lo mismo (el que usa la industria en general). "Tool use" es el nombre de Anthropic. Son sinónimos.
- **Declaración de herramienta** (*tool definition*): un diccionario con tres campos — `name`, `description` e `input_schema` — que le dice al modelo cómo se llama la función, cuándo usarla y qué parámetros acepta. Viaja en el parámetro `tools` de la llamada a la API.
- **JSON Schema**: un formato estándar para describir la forma de un dato JSON: qué campos tiene, de qué tipo es cada uno, cuáles son obligatorios. Es lo que va dentro de `input_schema`. Es, conceptualmente, lo mismo que hace un modelo de Pydantic (`class Order(BaseModel): id: int`), pero escrito como diccionario en vez de como clase. De hecho Pydantic sabe generar JSON Schema desde un modelo — lo usaremos más adelante.
- **Bloque de contenido** (*content block*): la respuesta del modelo no es un string, es una **lista** de bloques, y cada bloque tiene un `type`. Ya lo viste en `f2.llamadas-api`, cuando escribiste `for block in response.content if block.type == "text"`. Ahí solo había bloques `text`; ahora aparece un segundo tipo.
- **`tool_use`** (bloque): el bloque que el modelo devuelve cuando quiere que ejecutes una herramienta. Trae tres campos: `id` (un identificador único de ESA petición, tipo `toolu_01A2...`), `name` (qué herramienta) e `input` (un diccionario ya parseado con los argumentos).
- **`tool_result`** (bloque): el bloque que TÚ construyes con el resultado de haber ejecutado la herramienta. Trae `tool_use_id` (el mismo `id` de la petición que estás respondiendo), `content` (el resultado, como texto) y opcionalmente `is_error`.
- **`stop_reason`**: un campo de la respuesta que dice POR QUÉ el modelo dejó de generar. Los valores que nos importan hoy: `"end_turn"` (terminó de contestar, no quiere nada más) y `"tool_use"` (paró porque necesita que ejecutes algo). También existe `"max_tokens"` (lo cortó el límite que pusiste).
- **Loop agéntico** (*agentic loop*): el bucle `while` que repite "llamar al modelo → ¿pidió herramientas? → ejecutarlas → devolver resultados" hasta que el `stop_reason` deja de ser `"tool_use"`. Es el corazón de este tópico.
- **`tool_choice`**: parámetro opcional que controla si el modelo puede, debe o no debe usar herramientas (`auto`, `any`, `tool`, `none`).
- **Llamadas paralelas** (*parallel tool use*): el modelo puede pedir VARIAS herramientas en un mismo turno — o sea, devolver varios bloques `tool_use` en la misma respuesta.
- **Despachador** (*dispatcher*): en tu código, la función o el diccionario que traduce el `name` que pidió el modelo a la función Python que hay que ejecutar.

---

## Concepto

### 1. Una herramienta son dos cosas separadas

Esto es lo primero que hay que tener claro, porque el error clásico es confundirlas. Una herramienta vive en dos sitios:

1. **La función real**, en tu código Python. Un `def` normal. El modelo nunca la ve ni la ejecuta.
2. **La declaración**, un diccionario que viaja a la API. Esto sí lo ve el modelo, y es lo ÚNICO que ve.

Analogía: es el menú de un restaurante. El cliente (el modelo) lee el menú y pide "una sopa del día"; el cliente no entra a la cocina ni toca una olla. La cocina (tu código) es la que cocina. El menú describe lo que se puede pedir; la cocina es lo que realmente ocurre. *Dónde se rompe la analogía:* en un restaurante, si el menú miente, el cliente se queja y se arregla. Aquí, si la declaración dice algo distinto de lo que hace la función, nadie se queja: el modelo pedirá cosas que tu código no sabe atender, y el error aparecerá en producción, torcido. La declaración y la función tienen que mantenerse sincronizadas a mano — o generarse la una de la otra.

Una declaración se ve así:

```python
{
    "name": "get_current_time",
    "description": "Get the current local time in a given IANA timezone. Call this whenever the user asks about the current time, date or day of the week.",
    "input_schema": {
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "description": "IANA timezone name, e.g. America/Bogota or Europe/Madrid.",
            }
        },
        "required": ["timezone"],
    },
}
```

Los tres campos, uno por uno:

- **`name`**: el identificador. Es el string que el modelo te va a devolver cuando pida la herramienta, y con el que tu despachador decidirá qué función correr. En inglés, en `snake_case`, un verbo y un objeto: `get_current_time`, `search_orders`, `send_email`.
- **`description`**: aquí es donde se gana o se pierde. **No es documentación para humanos: es prompt.** El modelo decide si llamar la herramienta leyendo ESTA frase. Una descripción que dice solo QUÉ hace ("Gets the time") deja la decisión al azar; una que dice **CUÁNDO llamarla** ("Call this whenever the user asks about the current time, date or day of the week") sube muchísimo la tasa de acierto. Todo lo que aprendiste en `f2.prompting-estructurado` sobre contratos explícitos aplica aquí, letra por letra.
- **`input_schema`**: la forma de los argumentos, en JSON Schema. `"type": "object"` significa "los argumentos son un diccionario" (siempre es así en el nivel de arriba). `properties` lista cada parámetro con su tipo y su descripción — y sí, **cada parámetro también lleva descripción**: es el modelo quien debe rellenar ese valor, y necesita saber qué formato espera (`America/Bogota`, no `Colombia`). `required` es la lista de los obligatorios; lo que no esté ahí, el modelo puede omitirlo.

Detalle que evita horas de confusión: cuando el schema tiene un conjunto cerrado de valores válidos, se declara con `enum`:

```python
"unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
```

Así el modelo no puede inventarse `"centigrados"`. Es el mismo razonamiento que un `Literal["celsius", "fahrenheit"]` en Pydantic: cerrar el espacio de valores en vez de confiar en que el que responde adivine bien.

### 2. El ciclo llamada–resultado, paso a paso

Este es el mecanismo completo. Cinco pasos, y ninguno es opcional.

**Paso 1 — tú llamas, declarando las herramientas.**
```python
messages = [{"role": "user", "content": "What time is it in Bogota?"}]
response = client.messages.create(model=..., max_tokens=..., tools=TOOLS, messages=messages)
```
`tools` es la lista de declaraciones. Ojo: declarar herramientas **no obliga** al modelo a usarlas. Si le preguntas "¿cuánto es 2+2?", responderá `4` y `stop_reason` será `"end_turn"` — cero llamadas a herramientas. Declarar es ofrecer, no imponer.

**Paso 2 — el modelo pide.** Si decide que necesita una, la respuesta trae `stop_reason == "tool_use"` y su `content` contiene un bloque así:
```python
ToolUseBlock(type="tool_use", id="toolu_01A2b3...", name="get_current_time", input={"timezone": "America/Bogota"})
```
Dos cosas que conviene notar. Primera: `input` ya viene **parseado como diccionario** de Python — el SDK hizo el `json.loads` por ti; no hagas string matching sobre él. Segunda: ese `id` no es decorativo. Es la pieza que empareja pregunta con respuesta, y en un momento se ve por qué hace falta.

Además, el `content` puede traer un bloque `text` ANTES del `tool_use` ("Let me check that for you"). Por eso nunca se hace `response.content[0]`: se **filtra por `type`**, exactamente como ya haces con los bloques de texto en tu `ask()`.

**Paso 3 — tú ejecutas.** En tu máquina, con tu código. Tomas `block.name`, buscas la función en tu despachador, la llamas con `**block.input`. Aquí es donde pasa lo que tenga que pasar: se consulta la base de datos, se lee el archivo, se manda el correo.

**Paso 4 — tú devuelves el resultado, y el historial crece con DOS mensajes.** Este paso es el que más se equivoca, así que despacio.

Recuerda de `f2.llamadas-api` que la API es **stateless**: no recuerda nada entre llamadas. Tú vuelves a mandar la conversación entera cada vez. Entonces, para que el modelo sepa qué pidió y qué le contestaste, `messages` tiene que crecer con dos entradas:

```python
messages.append({"role": "assistant", "content": response.content})   # lo que el modelo pidió
messages.append({"role": "user", "content": tool_results})            # lo que tú respondiste
```

- La primera es el turno del **asistente**, y va `response.content` **completo, tal cual**: la lista de bloques entera, incluido el `tool_use`. Si guardas solo el texto, el bloque `tool_use` desaparece del historial, y en la siguiente llamada el modelo ve un resultado de herramienta que responde a una petición que no existe. La API lo rechaza con un 400.
- La segunda va con `role: "user"`. Esto choca al principio — el resultado no lo escribió ningún usuario humano, lo produjo tu programa — pero la API solo tiene dos roles de conversación, y todo lo que no genera el modelo entra como `user`. Piensa en `user` como "el lado de afuera del modelo", no como "la persona".

Y `tool_results` es una lista de bloques de este estilo:
```python
{"type": "tool_result", "tool_use_id": "toolu_01A2b3...", "content": "2026-09-26 09:14:22-05:00"}
```
El `tool_use_id` es el `id` que vino en el `tool_use`, copiado literalmente. Analogía: es el número de ticket de la lavandería. Si dejas tres prendas y te dan tres tickets, al recogerlas devuelves cada ticket con su prenda; sin tickets nadie sabe qué es de quién. *Dónde se rompe:* en la lavandería tú podrías reconocer tu camisa a ojo; aquí no hay "a ojo" — el `id` es el único vínculo, y uno mal copiado es un 400, no un malentendido.

**Paso 5 — vuelta a empezar.** Llamas otra vez con el `messages` ya crecido. Ahora el modelo tiene el dato y normalmente responde en texto con `stop_reason == "end_turn"`... o pide OTRA herramienta, porque el resultado de la primera lo llevó a necesitar una segunda. Por eso esto es un **bucle**, no una secuencia de dos pasos: no puedes saber de antemano cuántas vueltas hará.

### 3. Llamadas paralelas: todos los resultados en UN mensaje

El modelo puede pedir varias herramientas de una sola vez. Si le preguntas "¿qué hora es en Bogotá y en Madrid?", un mismo `response.content` puede traer dos bloques `tool_use`, con dos `id` distintos.

La regla de oro: ejecutas las dos y devuelves **los dos `tool_result` dentro de un único mensaje `user`**, como dos elementos de la misma lista `content`. No dos mensajes seguidos. Dos motivos, uno duro y uno blando:

- Duro: la API exige que **cada** `tool_use` del turno anterior tenga su `tool_result` en el mensaje inmediatamente siguiente. Si respondes uno solo, es un 400.
- Blando: partir los resultados en mensajes separados le enseña al modelo, turno a turno, a no volver a pedir cosas en paralelo — y pierdes la ventaja de hacer dos consultas de una vez.

### 4. Errores de herramienta: `is_error`, no una excepción que se escapa

Tu herramienta va a fallar. El archivo no existe, la base de datos no responde, el modelo mandó `"Colombia"` donde el schema pedía `"America/Bogota"`. La pregunta de diseño es: ¿qué haces con ese fallo?

La respuesta ingenua es dejar que la excepción de Python suba y reviente el programa. Pero mira lo que eso significa para el usuario: escribió una pregunta, el modelo pidió un archivo que no existe y **toda la conversación se cae**, incluidos los tres datos que ya se habían conseguido bien.

El protocolo tiene una salida mejor: devuelves un `tool_result` normal, pero marcado como error.

```python
{"type": "tool_result", "tool_use_id": "toolu_01...", "content": "FileNotFoundError: note 'roadmap' does not exist. Available notes: intro, pricing.", "is_error": True}
```

Con eso, el modelo **recibe el error como información** y reacciona: reintenta con otro argumento, prueba otra herramienta, o le dice al usuario que ese dato no está. La conversación sigue viva. Esto es lo que pide el criterio de dominio del tópico: *manejo de errores de herramienta sin romper la conversación*.

Y fíjate en el contenido del mensaje del ejemplo: no dice `"error"` a secas. Dice qué falló y **qué alternativas hay**. Ese texto es, otra vez, prompt: es lo único que el modelo tendrá para decidir su siguiente paso. Un error mudo produce un reintento a ciegas.

Cuidado con el otro extremo, que conecta con tu debilidad registrada de S9 (*"dejar caer errores en silencio"*): `is_error` es para fallos **de la herramienta** — el archivo que no está, el argumento inválido, el timeout del servicio. No es un sitio donde esconder un bug tuyo. Un `TypeError` porque tu despachador llamó mal a la función no es un error de herramienta: es código roto, y debe reventar ruidosamente en tu cara mientras desarrollas.

### 5. `tool_choice`: quién decide si se usa una herramienta

Por defecto es `{"type": "auto"}`: el modelo decide. Las otras opciones:

| Valor | Qué hace |
|---|---|
| `{"type": "auto"}` | El modelo decide si usa herramientas o no. Es el default. |
| `{"type": "any"}` | Obliga a usar **alguna** herramienta (no puede responder solo texto). |
| `{"type": "tool", "name": "x"}` | Obliga a usar exactamente esa herramienta. |
| `{"type": "none"}` | Prohíbe usar herramientas en ese turno. |

Para un asistente conversacional, `auto`. `any` y `tool` sirven cuando la herramienta ES la tarea (por ejemplo, forzar una herramienta de extracción para sacar JSON). Hoy trabajamos con `auto`, que es donde está el aprendizaje: si el modelo NO llama la herramienta cuando debería, casi siempre el problema está en tu `description`, no en el modelo.

### 6. Por qué escribimos el loop a mano

El SDK de Anthropic trae un ayudante (`client.beta.messages.tool_runner`) que hace este bucle por ti: le pasas funciones decoradas con `@beta_tool` y él genera el schema, llama, ejecuta y repite. En producción es lo razonable.

Aquí lo escribimos a mano, por la misma razón por la que escribiste tus reintentos a mano en `f2.llamadas-api` teniendo el SDK uno incorporado: mientras la máquina sea una caja negra, no puedes depurarla. Cuando el `tool_runner` se comporte raro — y se comportará —, la diferencia entre arreglarlo en diez minutos y quedarte atascado es saber exactamente qué mensajes viajan y en qué orden.

---

## Demo mínima

Este archivo NO es la solución de tu ejercicio: es un ejemplo para leer. Tiene UNA herramienta; tu ejercicio pedirá tres y con errores de verdad.

```python
"""Minimal tool-use loop: one tool, one conversation."""

from datetime import datetime
from zoneinfo import ZoneInfo

import anthropic

client = anthropic.Anthropic()
MODEL = "claude-haiku-4-5"

# --- 1. The real function ---------------------------------------------------
def get_current_time(timezone: str) -> str:
    """Return the current time in an IANA timezone, as ISO text."""
    return datetime.now(ZoneInfo(timezone)).isoformat(timespec="seconds")


# --- 2. The declaration the model sees --------------------------------------
TOOLS = [
    {
        "name": "get_current_time",
        "description": (
            "Get the current local time in a given IANA timezone. "
            "Call this whenever the user asks about the current time or date."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "IANA timezone name, e.g. America/Bogota.",
                }
            },
            "required": ["timezone"],
        },
    }
]

# --- 3. The dispatcher ------------------------------------------------------
HANDLERS = {"get_current_time": get_current_time}


def run_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """Execute one tool call. Returns (content, is_error)."""
    try:
        return HANDLERS[name](**tool_input), False
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}", True


# --- 4. The agentic loop ----------------------------------------------------
def chat(user_input: str, *, max_turns: int = 5) -> str:
    messages = [{"role": "user", "content": user_input}]

    for _ in range(max_turns):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            return " ".join(b.text for b in response.content if b.type == "text")

        messages.append({"role": "assistant", "content": response.content})

        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            content, is_error = run_tool(block.name, block.input)
            print(f"  [tool] {block.name}({block.input}) -> {content!r} error={is_error}")
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": content,
                    "is_error": is_error,
                }
            )

        messages.append({"role": "user", "content": results})

    raise RuntimeError(f"tool loop did not finish in {max_turns} turns")


if __name__ == "__main__":
    print(chat("What time is it in Bogota right now?"))
```

### Qué hace cada parte

**`from zoneinfo import ZoneInfo`** — `zoneinfo` es el módulo estándar de Python (desde 3.9) que conoce la base de datos de zonas horarias del sistema. `ZoneInfo("America/Bogota")` construye un objeto de zona horaria. Sin él, `datetime.now()` devolvería la hora local de tu máquina, que no es lo que se pidió. Si le pasas una zona que no existe, lanza `ZoneInfoNotFoundError` — y eso es justo lo que queremos que pase, porque es el camino que ejercita `is_error`.

**`def get_current_time(timezone: str) -> str`** — una función Python del todo normal, con type hints como cualquier otra de tu Fase 1. Nada en ella sabe que existe un LLM. Esa independencia es deliberada: la herramienta se puede testear con pytest sin gastar un solo token.

**`.isoformat(timespec="seconds")`** — convierte el `datetime` a texto (`'2026-09-26T09:14:22-05:00'`). Es obligatorio: el `content` de un `tool_result` viaja como **texto**, no como objeto Python. `timespec="seconds"` corta los microsegundos, que solo serían ruido para el modelo (y tokens que pagas).

**`TOOLS = [...]`** — la declaración de la sección 1. Nótese que la `description` dice cuándo llamarla, no solo qué hace, y que el parámetro trae su propio `description` con un ejemplo del formato. Sin ese ejemplo, el modelo manda `"Bogota"` a secas y la función falla.

**`HANDLERS = {"get_current_time": get_current_time}`** — el despachador: un diccionario de `name` (lo que dice el modelo) → función real. La clave del diccionario tiene que ser **idéntica** al `name` de la declaración; si se separan, el modelo pide un nombre que el diccionario no tiene y salta `KeyError`. La alternativa sería una cadena de `if name == "...": elif ...`, que crece mal y se olvida de actualizar; el diccionario centraliza el mapa en un sitio.

**`return HANDLERS[name](**tool_input), False`** — dos cosas en una línea. `HANDLERS[name]` saca la función; `(**tool_input)` la llama **desempaquetando** el diccionario en argumentos con nombre: si `tool_input` es `{"timezone": "America/Bogota"}`, esto es `get_current_time(timezone="America/Bogota")`. Por eso los nombres de las `properties` del schema deben coincidir con los nombres de los parámetros de la función: ese `**` los empareja por nombre.

**`except Exception as exc: return f"{type(exc).__name__}: {exc}", True`** — el `except` ancho aquí es deliberado (no como en tus reintentos de `f2.llamadas-api`, donde era deliberadamente estrecho): cualquier fallo de la herramienta se convierte en un resultado de error legible en vez de matar la conversación. `type(exc).__name__` da el nombre de la clase (`ZoneInfoNotFoundError`) y `{exc}` el mensaje; el modelo necesita ambos para decidir qué hacer. Sin este `try`, una zona mal escrita tumba todo el programa.

**`for _ in range(max_turns)`** — el bucle, con tope. Un `while True` puede quedarse dando vueltas para siempre si el modelo se obsesiona con una herramienta que falla una y otra vez — y cada vuelta cuesta dinero. `_` es la convención de Python para "esta variable no la uso": solo cuento vueltas.

**`if response.stop_reason != "tool_use": return ...`** — la condición de salida. Si el modelo no pidió herramientas, terminó: se juntan los bloques de texto y se devuelve. Fíjate que se pregunta por `stop_reason` y no por "¿hay bloques tool_use?": `stop_reason` es la señal oficial del protocolo, y además distingue el final legítimo (`end_turn`) de un corte por `max_tokens`, que querrás tratar aparte cuando el sistema crezca.

**`messages.append({"role": "assistant", "content": response.content})`** — el historial crece con la petición del modelo, **con `response.content` entero**. Sin esta línea (o guardando solo el texto), la siguiente llamada manda resultados de una petición que no aparece por ningún lado: 400.

**`for block in response.content: if block.type != "tool_use": continue`** — se recorren TODOS los bloques y se filtran los de tipo `tool_use`, porque puede haber texto mezclado y puede haber varias peticiones (llamadas paralelas). Un `response.content[0]` funcionaría hoy y fallaría el día que el modelo antepone "Let me check".

**`"tool_use_id": block.id`** — el ticket de la lavandería, copiado literal.

**`print(f"  [tool] ...")`** — no es adorno: sin esta línea, un loop de herramientas es una caja negra donde no ves qué pidió el modelo ni con qué argumentos. Es el mismo criterio del `print` en tus reintentos: un reintento invisible es indepurable, y una llamada a herramienta invisible también.

**`messages.append({"role": "user", "content": results})`** — TODOS los resultados, en UN solo mensaje (sección 3).

**`raise RuntimeError(...)`** — si se agotaron los turnos, el bucle no devuelve algo a medias en silencio: revienta y lo dice. Tu regla de S9: `else -> raise`.

### Cómo correrla y qué deberías ver

```bash
uv run python demo_tool_loop.py
```
`uv run` ejecuta el script dentro del entorno virtual del proyecto (la carpeta con su propia copia de Python y sus librerías), así que `anthropic` está disponible sin activarlo a mano. Salida esperada, dos líneas:

```
  [tool] get_current_time({'timezone': 'America/Bogota'}) -> '2026-09-26T09:14:22-05:00' error=False
It is currently 9:14 AM in Bogota.
```

La primera línea la imprime tu código al ejecutar la herramienta; la segunda es la respuesta final del modelo, ya con el dato. Si cambias la pregunta a `"What time is it in Mars/Olympus?"`, verás `error=True` con un `ZoneInfoNotFoundError` y, en la línea siguiente, al modelo explicando que esa zona no existe — la conversación no se cayó.

---

## Errores típicos

1. **Guardar solo el texto en el turno del asistente.** Se hace `messages.append({"role": "assistant", "content": text})` en vez de `response.content`. Síntoma: `BadRequestError 400` mencionando `tool_use_id` sin su `tool_use` correspondiente. Causa: el bloque `tool_use` se perdió al quedarte con el texto, y la API valida que cada `tool_result` responda a una petición presente en el historial.

2. **Nombres desincronizados entre la declaración y el código.** La declaración dice `"name": "get_time"` pero el diccionario de handlers tiene `"get_current_time"`, o el schema declara `"tz"` y la función recibe `timezone`. Síntomas: `KeyError: 'get_time'` en el primer caso, `TypeError: get_current_time() got an unexpected keyword argument 'tz'` en el segundo (el `**tool_input` empareja por nombre). Causa: la declaración y la función son dos objetos distintos que nadie obliga a coincidir.

3. **Devolver solo uno de los resultados cuando el modelo pidió dos.** Se procesa el primer `tool_use` y se sale del bucle con un `break`, o se manda cada resultado en su propio mensaje. Síntoma: 400 por resultados faltantes, o un modelo que deja de pedir cosas en paralelo. Causa: cada `tool_use` del turno exige su `tool_result`, todos juntos en el mensaje siguiente.

4. **`description` que dice qué hace pero no cuándo usarla.** No produce ningún error: produce algo peor, un modelo que simplemente no llama la herramienta y se inventa la respuesta. Síntoma: el `print` del tool nunca aparece. Causa: la descripción es el único criterio que tiene el modelo para decidir, y "Gets the time" no le dice que una pregunta sobre la hora es su caso.

---

## Preguntas — respóndelas en el chat

1. **Predicción.** Cambias la línea `messages.append({"role": "assistant", "content": response.content})` por `messages.append({"role": "assistant", "content": "I will check the time."})`. Corres el script. ¿Qué pasa exactamente en la siguiente llamada a la API, y por qué? Escribe qué crees que verías antes de mirar la sección de errores típicos.

2. Una herramienta tuya consulta una base de datos y el servidor está caído. ¿Por qué devolver `tool_result` con `is_error: True` en vez de dejar que la excepción suba y mate el programa? ¿Qué hace el modelo con ese resultado que no podría hacer si el programa hubiera reventado? ¿Y dónde pondrías el límite: qué tipo de fallo NO debería convertirse en `is_error`?

3. El modelo responde con dos bloques `tool_use` en el mismo turno. ¿Por qué los dos `tool_result` tienen que ir en un único mensaje `user` y no en dos mensajes consecutivos? Da las dos razones (la que produce un error inmediato y la que degrada el comportamiento con el tiempo).

4. **Diseño.** Declaras una herramienta `run_shell_command(command: str)` que ejecuta lo que le pidan en tu máquina. ¿Quién ejecuta realmente ese comando y dónde corre? ¿Qué implica eso para la seguridad, y qué le pondrías a esa herramienta antes de dejarla en un sistema que atiende a usuarios que no conoces?
