# f2.llamadas-api — Llamadas a APIs de LLM · Lección

*Lee este documento completo y responde las preguntas del final en el chat, una por una, para irlas desarrollando con el tutor.*

---

## Por qué existe

En `f2.como-funciona-llm` viste QUÉ hace un LLM: predice el siguiente token, una y otra vez, sobre todo el texto que le des. Pero el modelo de verdad —los miles de millones de parámetros— vive en los servidores del proveedor (Anthropic, OpenAI), corriendo sobre GPUs que ni tú ni casi ninguna empresa puede comprar. Entonces, ¿cómo lo usa tu programa?

**El problema:** necesitas que TU código Python le mande texto a UN modelo que corre en OTRA máquina, al otro lado de internet, y reciba la respuesta.

**Eso ya lo sabes resolver.** Es exactamente lo que hiciste en la Fase 1 con Frankfurter y Open-Meteo: una *API REST* — un servidor que expone URLs, tú le mandas una request HTTP con datos, y te responde JSON. La API de Anthropic es eso mismo: un servidor HTTP. De hecho, podrías llamarla con `httpx` a pelo:

```
POST https://api.anthropic.com/v1/messages
```

con un JSON en el body y tu clave en un header. Sin magia: el mismo `POST` que le hiciste a tu propia API de FastAPI.

**Lo que se hacía antes** (y por qué era peor): llamar el endpoint a mano con `httpx` o `requests`. Funciona, pero cada equipo terminaba reescribiendo lo mismo: armar los headers de autenticación, serializar el body, parsear la respuesta, manejar el error 429 cuando mandas demasiadas requests, reintentar cuando el servidor falla, leer la respuesta en streaming trozo a trozo... Código repetido, con bugs repetidos, en cada empresa.

**La solución:** el proveedor publica un **SDK** — una librería oficial (`anthropic` para Python) que envuelve esa API HTTP. Tú escribes `client.messages.create(...)` y el SDK arma la request, pone los headers, parsea el JSON a objetos Python tipados, y reintenta los errores transitorios por ti. Analogía: el SDK es al endpoint HTTP lo que un cajero automático es a la bóveda del banco — no te da acceso a nada que no existiera antes, pero te ahorra hablar con la bóveda a mano y te protege de equivocarte en el protocolo. *Dónde deja de funcionar la analogía:* el cajero te limita a operaciones fijas; el SDK expone prácticamente TODO lo que la API sabe hacer — si algo existe en el endpoint, el SDK tiene un parámetro para ello.

Este tópico es la puerta de entrada de TODA la fase 2: tool use, salidas estructuradas, multi-proveedor — todo se monta sobre saber hacer esta llamada bien: con la estructura de mensajes correcta, midiendo lo que cuesta, en streaming cuando toca, y sin caerse cuando la red o el servidor fallan.

---

## Términos que vas a ver

- **API key**: una clave secreta (un string largo) que identifica TU cuenta ante el proveedor. Cada request la lleva; cada token que consumes se factura a la cuenta dueña de esa clave. Es una credencial como la `MODEL_REGISTRY_API_KEY` de tu propia API de la Fase 1 — solo que aquí el que cobra es Anthropic.
- **SDK** (Software Development Kit): librería oficial que envuelve la API HTTP de un proveedor para que la llames como funciones de tu lenguaje en vez de armar requests a mano.
- **Messages API**: el endpoint principal de Anthropic (`POST /v1/messages`). Le mandas una conversación (lista de mensajes) y te devuelve el siguiente mensaje del asistente.
- **role** (rol): etiqueta que dice quién habla en cada mensaje. `user` = el humano, `assistant` = el modelo, `system` = instrucciones del operador (tú, el programador).
- **system prompt**: instrucciones que le fijas al modelo ANTES de la conversación ("eres un asistente que responde en español, en máximo 3 frases"). No es un turno de la charla: es el contrato bajo el que corre toda la charla.
- **stateless** (sin estado): el servidor NO recuerda nada entre requests. Cada llamada llega, se procesa, se olvida. Si quieres que el modelo "recuerde" la conversación, tienes que mandarla completa cada vez. (Tu API de FastAPI con el `dict` de modelos era *stateful* — guardaba estado entre requests. Esta no.)
- **max_tokens**: tope de tokens que el modelo puede GENERAR en esta respuesta. Es un techo de gasto y de longitud, no una meta: el modelo puede parar antes.
- **stop_reason**: campo de la respuesta que dice POR QUÉ el modelo dejó de generar (terminó solo, chocó con `max_tokens`, quiere usar una herramienta...).
- **usage**: campo de la respuesta con el conteo exacto de tokens de entrada y de salida de ESA request. Es tu factura desglosada.
- **streaming**: en vez de esperar la respuesta completa, el servidor te la va mandando en trozos a medida que el modelo genera cada token. El mismo total, entregado en pedazos.
- **SSE** (Server-Sent Events): el mecanismo HTTP con el que llega el streaming — la conexión queda abierta y el servidor emite eventos de texto uno tras otro. El SDK te lo esconde: tú solo ves un iterador.
- **rate limit** (límite de tasa): tope de requests (y de tokens) por minuto que el proveedor le permite a tu cuenta. Si lo pasas, responde `429 Too Many Requests`. No es un castigo: protege al servidor de que un cliente lo sature.
- **backoff exponencial**: estrategia de reintento donde cada espera DUPLICA la anterior (1s, 2s, 4s, 8s...). "Backoff" = retirarse, dar un paso atrás antes de insistir.
- **jitter**: ruido aleatorio que se le suma a cada espera del backoff para que mil clientes que fallaron a la vez no reintenten todos en el mismo instante.

---

## Concepto

### 1. La estructura de mensajes: la conversación es una lista

Todo lo que la Messages API recibe y devuelve gira alrededor de UNA estructura: una lista de mensajes, cada uno con `role` y `content`:

```python
messages = [
    {"role": "user", "content": "My name is Alice."},
    {"role": "assistant", "content": "Nice to meet you, Alice!"},
    {"role": "user", "content": "What's my name?"},
]
```

Esto ES el prompt. En `f2.como-funciona-llm` viste que el modelo recibe "todo el texto" y predice lo que sigue: pues este es el formato en que ese texto viaja. El modelo lee la lista entera y genera el siguiente mensaje con `role: "assistant"`.

Tres reglas de la lista:
1. El primer mensaje es siempre de `user`.
2. Los roles se alternan en una conversación normal: user, assistant, user, assistant...
3. El `system` prompt NO va en la lista: va en un parámetro aparte (`system=`), porque no es un turno de nadie — son las reglas del juego.

**Y aquí la consecuencia más importante de todo el tópico: la API es stateless.** El servidor no tiene memoria de tu request anterior. Cada `POST /v1/messages` es un universo nuevo. Si en el turno 3 mandas solo `"What's my name?"` sin los turnos anteriores, el modelo NO SABE quién eres — no porque "olvide", sino porque literalmente jamás vio los turnos 1 y 2: esa historia vive en TU programa, en una lista de Python, y solo existe para el modelo si la incluyes en la request.

Analogía: cada request es como contratar a un consultor nuevo cada mañana. Es brillante, pero no estuvo en la reunión de ayer: si quieres que decida con contexto, le entregas el expediente completo cada día. El expediente es tu lista `messages`. *Dónde deja de funcionar:* al consultor humano le puedes resumir el expediente y sobreentiende; el modelo solo cuenta con los tokens exactos que le des — lo que no está en la lista, no existe.

Esto conecta directo con tu Q2 de la sesión pasada: ahora ves EL MECANISMO del costo cuadrático. "Mantener la conversación" = re-mandar la lista entera en cada turno = pagar los tokens de toda la historia otra vez como entrada.

### 2. La respuesta: bloques, no un string

La respuesta no trae un string suelto: trae una lista de **bloques de contenido** (`response.content`). Hoy casi siempre verás un solo bloque de tipo `text`, pero el mismo sobre puede traer bloques de otros tipos — `thinking` (razonamiento del modelo), `tool_use` (el modelo pide ejecutar una herramienta — tópico `f2.tool-use`). Por eso el acceso correcto es filtrar por tipo, nunca asumir `content[0].text` a ciegas.

Además del contenido, la respuesta trae dos campos que un ingeniero SIEMPRE mira:

- **`stop_reason`**: por qué paró. `end_turn` = terminó lo que quería decir. `max_tokens` = lo cortaste tú con el techo — la respuesta está TRUNCADA y no hay error ni aviso más allá de este campo. Ignorarlo es la versión LLM de tu vieja conocida: el test verde por la razón equivocada — una respuesta que "llegó bien" pero está cortada a la mitad.
- **`usage`**: cuántos tokens entraron (`input_tokens`) y salieron (`output_tokens`). Con esto y la tabla de precios calculas el costo exacto de cada request.

### 3. Tokens y dinero: la tabla de precios

Se factura por token, con precio distinto para entrada y salida (la salida es más cara: generar cuesta más que leer). Precios de la API de Anthropic por **millón** de tokens (fuente: referencia oficial, junio 2026):

| Modelo | ID | Entrada $/1M | Salida $/1M |
|---|---|---|---|
| Claude Opus 5 | `claude-opus-5` | $5.00 | $25.00 |
| Claude Sonnet 5 | `claude-sonnet-5` | $3.00 | $15.00 |
| Claude Haiku 4.5 | `claude-haiku-4-5` | $1.00 | $5.00 |

Para dimensionar: una request con 1,000 tokens de entrada y 500 de salida en Opus 5 cuesta `1000/1_000_000 * 5 + 500/1_000_000 * 25 = $0.0175` — menos de dos centavos de dólar. Los ejercicios de este tópico completos te costarán centavos, no dólares. La fórmula que usarás mil veces:

```
costo = input_tokens / 1_000_000 * precio_entrada + output_tokens / 1_000_000 * precio_salida
```

Hay además un endpoint para contar tokens SIN llamar al modelo (`client.messages.count_tokens(...)`): le pasas los mensajes y te devuelve `input_tokens` sin generar nada y sin costo de salida. Es el sustituto correcto de la regla de dedo "4/3 caracteres" que usaste en el ejercicio pasado — y ojo: cuenta con el tokenizador REAL del modelo que le indiques, no con `tiktoken` (que es de OpenAI: tokenizador parecido, conteo distinto).

### 4. Streaming: los mismos tokens, entregados a medida que nacen

Sin streaming, la llamada es como las que hiciste con `httpx`: mandas la request, esperas, llega TODO junto. Si la respuesta tarda 30 segundos en generarse, tu usuario mira una pantalla congelada 30 segundos — y peor: una respuesta muy larga puede exceder el timeout HTTP y morir a mitad de camino.

Con streaming, el servidor mantiene la conexión abierta y te va empujando cada trozo de texto según el modelo lo genera (eso es SSE por debajo). El primer trozo llega en ~1 segundo, y el usuario ve la respuesta "escribiéndose" — exactamente lo que ves en claude.ai o ChatGPT: no es un efecto visual, es el streaming real de la API.

Dos cosas que el streaming NO cambia: el contenido total (los mismos tokens, el mismo orden — el modelo genera igual, solo cambia la entrega) y el costo (se factura por token, no por forma de entrega). Lo que SÍ cambia: la **latencia percibida** (tiempo hasta el primer token vs tiempo hasta el último) y la **robustez** (una conexión que va recibiendo datos no se muere por timeout).

Analogía: descarga completa vs ver la película en streaming. Mismos bytes; la diferencia es cuándo empiezas a disfrutarlos. *Dónde deja de funcionar:* en Netflix puedes saltar al minuto 40; aquí no — los tokens llegan en orden y no hay adelantar, porque el minuto 40 aún no existe: se está generando.

### 5. Cuando falla: reintentos con backoff exponencial

Llamar a una API por internet falla. No "puede fallar": falla, con certeza estadística, y tu código de la Fase 1 ya lo sabía (timeouts de httpx, 502/504). Con APIs de LLM hay un fallo nuevo y frecuente: **429, rate limit** — mandaste más requests (o tokens) por minuto de los que tu cuenta permite.

La pregunta clave ante cualquier error HTTP: ¿reintentar sirve de algo?

- **429 y 5xx (500, 502, 503...)**: fallos **transitorios**. El servidor está saturado o tu ventana de rate limit está llena; en unos segundos el mundo cambia. Reintentar SÍ sirve.
- **4xx (400, 401, 404...)**: fallos **permanentes**. Tu request está mal armada (400), tu clave es inválida (401), el modelo no existe (404). Reintentar mandaría LA MISMA request rota y recibiría LA MISMA respuesta, N veces. Reintentar NO sirve: hay que arreglar el código.

¿Y CÓMO se reintenta lo transitorio? Aquí entra el backoff exponencial. Reintentar inmediatamente y en bucle es contraproducente: si el servidor está saturado, mil clientes martillándolo sin pausa lo mantienen saturado. La estrategia estándar tiene tres piezas:

1. **Esperar antes de reintentar** — darle aire al servidor.
2. **Duplicar la espera en cada intento** (1s, 2s, 4s, 8s...) — eso es lo "exponencial": si el problema persiste, insistes cada vez menos.
3. **Sumar jitter** (ruido aleatorio) — si mil clientes fallaron en el mismo instante y todos esperan exactamente 1s, reintentan todos a la vez y recrean la estampida. Con jitter, cada uno espera 1s + random(0,1) y los reintentos se desparraman.

Analogía: un número telefónico ocupado. Remarcar sin parar cada segundo es spam; esperas un minuto, luego dos, luego cinco. Y si toda la oficina llama al mismo número, mejor que no remarquen todos sincronizados. *Dónde deja de funcionar:* el teléfono no te dice cuánto esperar; la API a veces sí — el 429 puede traer un header `retry-after` con los segundos exactos, y eso le gana a cualquier fórmula.

**La buena noticia:** el SDK de Anthropic trae esto DE FÁBRICA. Reintenta automáticamente errores de conexión, 429 y ≥500, con backoff exponencial, 2 reintentos por defecto (configurable con `max_retries`). Los 4xx no los reintenta — como debe ser. En el ejercicio vas a implementar el backoff a mano UNA vez para entender la mecánica (criterio del roadmap), y después dejarás que el SDK lo haga, sabiendo exactamente qué hace por ti.

### 6. ¿Y OpenAI?

El roadmap pide saber llamar a AMBOS proveedores. La estructura es un calco conceptual: OpenAI también expone una API HTTP con SDK oficial (`openai`), también recibe una lista de mensajes con roles, también es stateless, también streamea por SSE, también factura por tokens de entrada/salida y también responde 429 cuando te pasas. Cambian los nombres (el método, cómo viaja el system prompt, la forma del JSON de respuesta) — detalles que verás con la documentación oficial al frente cuando toque en el ejercicio de este tópico y en `f2.multi-proveedor`. Lo importante hoy: los CONCEPTOS de esta lección (mensajes, stateless, usage, streaming, backoff) son el idioma de TODOS los proveedores de LLM, no un dialecto de Anthropic.

---

## Demo mínima

Dos scripts cortos. **Léelos y entiéndelos hoy; los correremos en la sesión de ejercicio** (necesitan una API key — ver "Antes de la próxima sesión" al final). Viven en esta carpeta como `demo_basic_call.py` y `demo_streaming.py`.

### Demo 1 — `demo_basic_call.py`: una llamada completa, con costo

```python
import anthropic

PRICE_INPUT_PER_MTOK = 5.00
PRICE_OUTPUT_PER_MTOK = 25.00

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-5",
    max_tokens=200,
    system="You are a concise assistant. Answer in one sentence.",
    messages=[
        {"role": "user", "content": "Why is the sky blue?"},
    ],
)

for block in response.content:
    if block.type == "text":
        print(block.text)

print(f"\nstop_reason: {response.stop_reason}")
print(f"input tokens:  {response.usage.input_tokens}")
print(f"output tokens: {response.usage.output_tokens}")

cost = (
    response.usage.input_tokens / 1_000_000 * PRICE_INPUT_PER_MTOK
    + response.usage.output_tokens / 1_000_000 * PRICE_OUTPUT_PER_MTOK
)
print(f"cost: ${cost:.6f}")
```

Línea por línea:

- `import anthropic` — el SDK oficial. Se instala con `uv add anthropic` (lo harás en el ejercicio). Sin él, tendrías que armar el POST con httpx a mano.
- `PRICE_INPUT_PER_MTOK = 5.00` / `PRICE_OUTPUT_PER_MTOK = 25.00` — los precios de Opus 5 por millón de tokens, NOMBRADOS como constantes arriba (la regla que peleaste en S15-S16: un valor usado más de una vez se nombra una vez). Si mañana cambia el precio o el modelo, se toca UNA línea.
- `client = anthropic.Anthropic()` — construye el cliente. Sin argumentos: el SDK busca la clave en la variable de entorno `ANTHROPIC_API_KEY` por sí solo. Por eso la clave NUNCA aparece en el código — mismo patrón que tu `MODEL_REGISTRY_API_KEY` con `os.environ`, y por la misma razón: el código va a git, los secretos no. Por debajo, este objeto es un cliente HTTP (httpx, de hecho) apuntando a `https://api.anthropic.com`.
- `client.messages.create(...)` — LA llamada. Ejecuta un `POST /v1/messages`, espera la respuesta completa y la parsea. Es bloqueante y sin streaming: la forma más simple. Sus argumentos:
  - `model="claude-opus-5"` — qué modelo atiende la request. Obligatorio: el precio y la calidad dependen de esto.
  - `max_tokens=200` — techo de generación. Obligatorio en esta API: te fuerza a decidir cuánto estás dispuesto a pagar/esperar como máximo. Si el modelo necesita más, corta y te lo dice en `stop_reason`.
  - `system="..."` — las instrucciones del operador. Fíjate que va como parámetro, FUERA de la lista de mensajes.
  - `messages=[...]` — la conversación. Un solo turno de `user` aquí. Si esto fuera un chat con historia, la lista traería todos los turnos anteriores.
- `for block in response.content: if block.type == "text":` — la respuesta es una LISTA de bloques; filtramos los de texto en vez de asumir que el primero lo es. Sin este filtro, el día que la respuesta traiga un bloque `thinking` primero, `content[0].text` revienta con `AttributeError`.
- `print(response.stop_reason)` — el porqué del final. Esperas `end_turn`; si ves `max_tokens`, la respuesta de arriba está incompleta aunque se imprima sin error.
- `response.usage.input_tokens` / `.output_tokens` — el conteo exacto que el servidor facturó. No es estimación: es la factura.
- `cost = ...` — la fórmula de la sección 3, con las constantes de arriba. Verás algo como `$0.000275`: la demo entera cuesta menos que un grano de arroz.

Salida esperada (los números variarán):

```
The sky is blue because air molecules scatter short-wavelength blue light
from sunlight more than other colors (Rayleigh scattering).

stop_reason: end_turn
input tokens:  25
output tokens: 31
cost: $0.000900
```

### Demo 2 — `demo_streaming.py`: la misma llamada, en streaming

```python
import anthropic

client = anthropic.Anthropic()

with client.messages.stream(
    model="claude-opus-5",
    max_tokens=500,
    messages=[
        {"role": "user", "content": "Write a 4-line poem about the ocean."},
    ],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
    final_message = stream.get_final_message()

print(f"\n\noutput tokens: {final_message.usage.output_tokens}")
```

Línea por línea (solo lo que cambia respecto a la demo 1):

- `client.messages.stream(...)` — mismo endpoint, pero pide la respuesta como flujo SSE. Nota que se usa con `with ... as stream:`: es un *context manager*, igual que tu `async with httpx.AsyncClient()` de la Fase 1, y por la misma razón — hay una conexión abierta que debe cerrarse pase lo que pase, incluso si tu código revienta a mitad del flujo.
- `for text in stream.text_stream:` — el iterador de trozos de texto. Cada vuelta del `for` entrega los siguientes caracteres A MEDIDA QUE EL MODELO LOS GENERA. El `for` avanza al ritmo del modelo, no del procesador: es I/O, como cuando esperabas a Frankfurter.
- `print(text, end="", flush=True)` — dos detalles que SIN los cuales la demo miente: `end=""` evita que `print` meta un salto de línea tras cada trozo (los trozos son fragmentos de palabra, no líneas), y `flush=True` obliga a pintar el trozo YA — sin él, Python acumula la salida en un buffer y la suelta en bloques grandes, y el "efecto máquina de escribir" desaparece: verías la respuesta llegar a golpes, como si no hubiera streaming.
- `stream.get_final_message()` — al terminar el flujo, el SDK te arma el objeto de respuesta COMPLETO (el mismo tipo que devuelve `create`), con `usage` y `stop_reason` incluidos. Clave: `usage` solo puede existir al FINAL — mientras el modelo genera, nadie sabe aún cuántos tokens saldrán.

Salida esperada: el poema apareciendo palabra a palabra en tu terminal (eso no se puede mostrar en un documento estático — por eso hay que correrla), y al final el conteo de tokens.

### ¿Y los reintentos?

No llevan demo aparte porque ya corrieron en las dos de arriba sin que se vieran: el cliente `anthropic.Anthropic()` trae `max_retries=2` por defecto — si la request recibe un 429 o un 500, el SDK espera con backoff exponencial y reintenta hasta 2 veces, todo dentro de la misma línea `create(...)`. Se configura así:

```python
client = anthropic.Anthropic(max_retries=5)   # más paciencia
client = anthropic.Anthropic(max_retries=0)   # sin reintentos (lo usarás para VER los errores crudos)
```

En el ejercicio implementarás el backoff a mano una vez — con el bucle, el `2 ** attempt` y el jitter — para que lo que el SDK hace por ti no sea magia sino mecánica que ya escribiste.

---

## Errores típicos

1. **Mandar solo el último mensaje en un chat multi-turno.** Síntoma: el modelo "olvida" todo — le dices tu nombre y en el turno siguiente no lo sabe. No hay error ni excepción: solo respuestas amnésicas. Causa: la API es stateless; la historia vive en tu lista de Python y si no la re-mandas completa, para el modelo esos turnos nunca existieron.

2. **Ignorar `stop_reason` y servir respuestas truncadas.** Síntoma: respuestas que terminan a mitad de frase, JSON cortado que revienta al parsearlo dos funciones más adelante. Causa: `max_tokens` demasiado bajo + nadie miró `stop_reason == "max_tokens"`. Es la familia "verde por la razón equivocada": la request devolvió 200, pero el contenido está incompleto y el único aviso es ese campo.

3. **Hardcodear la API key en el código.** Síntoma: nada... hasta que haces `git push` y tu clave queda pública en GitHub — hay bots que escanean repos buscando exactamente eso, y la factura de lo que consuman llega a tu cuenta. Prevención: la clave SIEMPRE en `ANTHROPIC_API_KEY` (variable de entorno) y el cliente sin argumentos; jamás `Anthropic(api_key="sk-ant-...")` con el string literal.

4. **Reintentar un 401 o 400 en bucle.** Síntoma: tu programa "se cuelga" un minuto martillando el servidor y muere igual, con el mismo error de la primera vez. Causa: tratar un fallo permanente (clave mala, request mal armada) como si fuera transitorio. La request no va a mejorar por insistir: el reintento es para 429/5xx, el 4xx se arregla en el código.

---

## Antes de la próxima sesión (la de ejercicio)

El ejercicio llama a la API real, así que necesitas una **API key de Anthropic**:

1. Crea una cuenta en `console.anthropic.com` (la consola de desarrolladores — distinta de claude.ai).
2. En **API Keys**, genera una clave (empieza con `sk-ant-`). Cópiala al crearla: no se vuelve a mostrar.
3. Hará falta un método de pago o crédito inicial; con $5 USD sobra para TODA la fase 2 (las demos cuestan décimas de centavo).
4. Guárdala como variable de entorno en tu máquina (en el Mac, zsh): `export ANTHROPIC_API_KEY="sk-ant-..."` — en la sesión de ejercicio la dejaremos persistente y verificaremos que funciona.

---

## Preguntas — respóndelas en el chat

1. **(Conexión con lo que ya sabes)** La API es stateless y en la sesión pasada calculaste que una conversación de 40 turnos cuesta cuadrático, no lineal. Explica, usando la lista `messages`, el mecanismo exacto que conecta las dos cosas: ¿qué contiene la request del turno 10 y por qué eso hace que cada turno sea más caro que el anterior?

2. **(Predicción)** Llamas `client.messages.create(...)` con `max_tokens=10` y el mensaje `"Explain photosynthesis in detail."`. La request devuelve 200, sin excepción. ¿Qué esperas encontrar en `stop_reason`, qué pinta tiene el texto de la respuesta, y qué valor aproximado trae `usage.output_tokens`?

3. **(Criterio)** El SDK reintenta automáticamente el 429 y el 500, pero el 401 y el 400 los lanza como excepción SIN reintentar. ¿Por qué esa línea divisoria? ¿Qué pasaría — concretamente, paso a paso — si el SDK reintentara un 401 con backoff exponencial de 5 intentos?

4. **(Matiz)** Streaming no cambia ni el contenido ni el costo de la respuesta — los mismos tokens, la misma factura. Entonces, ¿qué DOS problemas reales resuelve? Y una trampa: ¿por qué `usage` solo está disponible en `get_final_message()`, al terminar el flujo, y no al empezar?
