---
topic_id: f2.llamadas-api
aliases: ["f2.llamadas-api"]
fase: 2
tipo: codigo
estado: aprendido
nivel: sin_evaluar
repaso_proximo: 2026-09-18
tags: [fase/2, estado/aprendido]
---

# Llamadas a APIs de LLM

**Prerequisitos:** [[Cómo funciona un LLM]]

**Criterio de dominio:** Cliente que llama a ambos proveedores con streaming, reintentos con backoff exponencial y registro del costo en tokens de cada request.

## Apuntes

**S27 (2026-09-12/13) — sesión de lección.** Lección en `ejercicios/fase-2/f2.llamadas-api/leccion.md`; demos `demo_basic_call.py` y `demo_streaming.py` (leídas, sin correr: falta la API key).

- **La API de un LLM es una API REST más**: `POST /v1/messages` con JSON y una key en el header — el mismo patrón que Frankfurter/Open-Meteo en F1. El SDK (`anthropic`) es un cliente httpx envuelto: arma headers, parsea a objetos tipados y reintenta transitorios. Sin magia.
- **La conversación es una lista** de `{role, content}` (`user`/`assistant`; el `system` va como parámetro aparte). La API es **stateless**: la historia vive en tu programa y se re-manda ENTERA cada turno — ese es el mecanismo del costo cuadrático calculado en S26 (input ~lineal por turno, la suma es cuadrática). El *prompt caching* abarata el prefijo repetido sin volver stateful al servidor (stateful rompería el escalado horizontal).
- **La respuesta trae bloques, no un string** (`response.content` es lista: filtrar por `block.type`), y dos campos obligatorios de mirar: `stop_reason` (`end_turn` vs `max_tokens` = respuesta TRUNCADA con 200 y sin excepción — familia "verde por la razón equivocada") y `usage` (input/output tokens exactos = la factura).
- **Precios por millón de tokens** (jun 2026): Opus 5 $5/$25, Sonnet 5 $3/$15, Haiku 4.5 $1/$5. Fórmula: `tokens/1M × precio`, entrada y salida por separado. `count_tokens` cuenta con el tokenizador real sin generar (sustituye la regla de dedo 4/3).
- **Streaming (SSE)**: mismos tokens, misma factura; cambia la entrega. Resuelve latencia percibida + timeouts. `usage` solo existe al final: *no se puede predecir la cantidad de tokens — toca generarlos*.
- **Reintentos**: transitorio (429, 5xx, timeout) se reintenta con backoff exponencial + jitter; permanente (400, 401, 404) se arregla en el código, no insistiendo. El SDK lo trae de fábrica (`max_retries=2`). 429 ≠ timeout: el 429 es una response real (con `retry-after`); el timeout es ausencia de respuesta (excepción del cliente).
- **API key**: ~~env var en el perfil del shell~~ → **corregido el 2026-09-13**: un `.env` dentro de la carpeta del proyecto, cargado con `uv run --env-file .env`. Una variable exportada en `~/.zshrc` la hereda *todo* proceso de esa terminal — incluidas herramientas que hablan con esta misma API y facturan contra tus créditos. El código solo conoce el *nombre* de la variable; el `.env` va en `.gitignore`.

**Acordado:** ejercicio extra tras el principal — mini-SDK con httpx a pelo contra su Ollama remoto (RTX 5080): armar el POST, parsear SSE a mano, backoff propio.

**S28 (2026-09-13) — sesión de ejercicio.** Ejercicio `01-cliente-anthropic/`: 2 de 3 TODO completos y verificados ejecutando.

- **El cliente no es la request.** `anthropic.Anthropic()` se construye una vez y guarda lo que no cambia entre llamadas (`api_key`, `base_url`, `timeout`, `max_retries`) — mismo papel que el `AsyncClient` compartido del `lifespan` en F1. El *contenido* (`model`, `messages`, `max_tokens`, `system`, sampling) va en cada `messages.create()`.
- **`temperature` y `top_p` ya no existen en la Messages API** del SDK `anthropic` 1.5.0: se quitaron de la firma y del TypedDict. Los modelos actuales exponen `output_config.effort` y administran su propio sampling. Llegan a modelos anteriores (Haiku 4.5) por `extra_body={"temperature": 0.0}` — probado en vivo, 200 sin error.
- **`usage` tiene más campos que los dos que importan**: `input_tokens` y `output_tokens` son la factura; `cache_*` es prompt caching (tópico posterior), `server_tool_use` son tokens de herramientas del servidor, `inference_geo` y `service_tier` son de infraestructura.
- **Entrada y salida se cuentan y se cobran por separado** (Haiku $1 vs $5 por millón). Una función de costo que las suma con la misma tarifa produce un número que no se mueve al cambiar la salida.
- `" ".join(bloque.text for bloque in content if bloque.type == "text")` — acumula y devuelve `""` con cero bloques, en vez de sobrescribir y estallar.
- **La expresión ternaria no tiene `elif`**: solo `A if cond else B`; para encadenar, el segundo ternario va dentro del `else`. `elif` pertenece a la sentencia `if`, que no produce un valor.

**S29 (2026-09-14/15) — sesión de ejercicio.** `TODO(3) ask_with_retries` escrito y a medias: la mecánica del backoff quedó, el manejo del fallo final no.

- **Backoff exponencial, la mecánica medida.** `2**N + random.uniform(0, 1)` produjo `1.21`, `2.63`, `4.81` en la corrida real. El `2**N` es la progresión; el `random.uniform(0, 1)` es el jitter que evita que mil clientes que fallaron juntos reintenten en el mismo instante.
- **`except` acepta una tupla de clases** (`except TRANSIENT_ERRORS as exc:`), no hay que recorrerla. Tiene que ser tupla: con lista da `TypeError`. Lo que no entra en la tupla **no se atrapa y sube solo** — la cláusula "el error permanente escapa intacto" no se escribe, se obtiene gratis. Verificado: el `401` del paso 7 subió sin una sola línea de reintento.
- **`**kwargs` es empaquetado; `**dict` en la llamada es desempaquetado.** `def f(..., **ask_kwargs)` recoge en un dict todo argumento con nombre no declarado en la firma; `ask(prompt, **ask_kwargs)` lo devuelve a su forma. Por qué existe: un envoltorio que solo añade reintentos no debe repetir los parámetros de la función que envuelve — si los repite, duplica los valores por defecto y se queda sordo a los parámetros nuevos. *Coste:* mypy deja de verificar lo que va ahí dentro; un nombre mal escrito revienta en ejecución, dentro de `ask`.
- **El mensaje se imprime ANTES de dormir, y anuncia la espera que viene** — no la ya hecha. Su razón de ser es que, cuando el programa se queda quieto 8 segundos, sepas por qué y cuánto. Impreso después, o con el valor del intento anterior, la línea no sirve para nada.
- **Una función que termina sin `return` devuelve `None`**, y ese `None` viaja hasta el `answer, cost = ...` del que llama, que revienta con `TypeError` (el `NoneType` aparece *dentro* del mensaje, no es la excepción). Lo perverso: el error habla de desempaquetado cuando la causa fue que la API falló cinco veces. Por eso el contrato pide re-lanzar el error original.
- **Cómo forzar un error transitorio sin red ni key** (`retry_check.py`, andamiaje): apuntar el cliente a `http://127.0.0.1:9` (puerto *discard*, nadie escucha) → conexión rechazada → `anthropic.APIConnectionError`, que está en `TRANSIENT_ERRORS`. Se cambia reasignando el nombre a nivel de módulo (`llm_client.client = ...`) sin tocar `llm_client.py`, porque `ask()` resuelve `client` en el módulo cada vez que se ejecuta.
- **Hueco de diseño del propio enunciado, encontrado hoy:** ni el paso 5 (camino feliz) ni el paso 7 (key rota, error permanente) hacen correr el bucle de reintentos. Una verificación que no ejercita lo que dice verificar — la misma familia que lleva seis apariciones en su historial.

**S30 (2026-09-16) — sesión de ejercicio.** `01-cliente-anthropic` **COMPLETO y verificado**. Los tres cabos de la S29 cerrados por él.

- **La espera pertenece al hueco ENTRE intentos, no al intento que falló.** Con `max_retries=3` hay 3 intentos y **2** esperas: dormir después del último es tiempo muerto, porque ya no queda nada que reintentar. Analogía: con 3 postes de cerca hay 2 huecos. Consecuencia en el código: lo primero que decide el `except` es *"¿era este el último intento?"* → si sí, lanza; si no, entonces calcula, imprime y duerme. La guarda correcta es `if retry_no == max_retries - 1:` porque `max_retries - 1` es el **índice** del último intento (con 3 intentos: 0, 1, **2**).
- **El `as` de `except E as exc` no es un context manager**, es solo el nombre donde se guarda el objeto. Pero Python hace un **`del exc` implícito** al salir del bloque `except` — para no mantener viva una referencia al traceback, que referencia el frame, que referencia las locales (fuga de memoria). Así que la variable **no existe después del `except`**. De ahí los dos caminos para el fallo final: (A) lanzar *dentro* del `except`, o (B) copiar el objeto a otra variable que viva fuera del bucle.
- **`raise` a secas relanza la excepción activa.** Dentro de un `except`, Python ya sabe cuál se está manejando. `raise exc` funciona pero repite un dato que Python ya tiene; `raise` a secas comunica *"esto pasa de largo intacto"* y es inmune a que el nombre `exc` se reasigne más adelante. Es la regla `TRY201` de ruff.
- **Por qué re-lanzar el original y no fabricar uno nuevo:** el traceback del error relanzado trae la cadena completa hasta la causa raíz — `anthropic.APIConnectionError: Connection error.` → `httpx2.ConnectError` → `httpcore2.ConnectError: [Errno 61] Connection refused`. Ese `Errno 61` es lo único que dice *por qué* falló la red. Un error fabricado tira esa cadena a la basura. (Y `raise anthropic.APIConnectionError` sin paréntesis ni siquiera construye: `TypeError: missing 1 required keyword-only argument: 'request'` — una **clase** no es una **instancia**.)
- **Estado acumulado vs cálculo directo.** El backoff se puede llevar acumulando (`delay = 1`, luego `delay * 2`, guardando el valor entre vueltas) o calculando (`2**retry_no`). Producen la misma secuencia (1, 2, 4, 8), pero la segunda no tiene estado que sobreviva entre iteraciones — y el estado entre iteraciones es justo lo que se rompe cuando alguien mueve una línea.
- **Cómo se lee la salida de ruff**: código de regla (el prefijo dice la familia: `TRY` = `try/except`, `F` = pyflakes, `E` = estilo), `archivo:línea:columna`, el subrayado `^^^` sobre el trozo exacto que sobra, y el `help:` con el arreglo.
- **`uv run --env-file X` NO sobrescribe una variable que ya exista en el entorno**: el shell gana y el archivo solo rellena huecos. Comprobado en aislado: `PROBE_VAR=from_shell uv run --env-file probe.env python -c "print(os.environ['PROBE_VAR'])"` → `from_shell`. Consecuencia práctica: el paso 7 (key rota vía `.env.broken`) **solo funciona en una terminal donde `ANTHROPIC_API_KEY` no esté exportada**.
- **Comprobar si un secreto está puesto sin imprimirlo**: `echo "${VAR:+ESTA PUESTA}"` imprime un texto fijo si la variable existe y nada si no. La forma `${VAR:-NO}` **imprime el valor** — nunca usarla con secretos.

**Resultados de la verificación (tutor, ejecutando):** `retry_check.py` → 2 bloques (intentos 0 y 1), esperas ~1.8 / ~2.2, traceback real con `Errno 61`. `.env.broken` → `AuthenticationError` 401 con cero reintentos. `ruff check .` → `All checks passed!`. `RESULTADOS.md` → pasos 7 y 8 completos con causa por fila.

**Falta para `dominado`:** el `criterio_dominio` pide **ambos proveedores** (falta OpenAI) y **streaming** dentro del cliente propio. Sigue acordado el ejercicio extra del mini-SDK con `httpx` a pelo contra su Ollama remoto.

## Errores cometidos

- **2026-09-13**: "429 es un timeout" — confundió una response de rate limit con la ausencia de respuesta. Corregido en sesión y reproducido bien en la repregunta ("si hay status code, hubo respuesta"). Vigilar el vocabulario al clasificar fallos en el ejercicio.
- **2026-09-13** (menor): en el inventario de la request del turno 10 omitió el 10.º mensaje de `user` (la request nueva que dispara la llamada).
- **2026-09-13 (S28) — media corrección, tres pasadas.** En `cost_usd` las dos líneas eran idénticas (mismo conteo, misma tarifa). Tras señalarlo cambió **solo** la tarifa (`[0]`→`[1]`) y dejó `input_tokens`: el costo seguía sin moverse con la salida. Cada línea debía cambiar *dos* cosas respecto a la otra y vio una. Lo que lo destrabó: la prueba diferencial — fijar la entrada y mover la salida de 100 a 900 para ver que el precio no cambiaba.
- **2026-09-13 (S28)**: `elif` dentro de una expresión ternaria → `SyntaxError: expected 'else' after 'if' expression`.
- **2026-09-13 (S28)**: `out_text = block.text` dentro del bucle — sobrescribe en vez de acumular. Verde por accidente (llegó un solo bloque). A favor: predijo las dos consecuencias exactas al preguntárselo.

- **2026-09-15 (S29) — media corrección, segunda aparición.** Al subir el cálculo de `sleep_time` por encima del `print` (lo pedido, y bien hecho) se llevó de paseo el `retry_no += 1` y rompió la numeración de intentos, que estaba correcta y sobre la que se le había dicho "no la toques": pasó a imprimir `1, 2, 3` donde el contrato dice `0, 1, 2`. Mueve el bloque en vez de la línea y no reevalúa lo que quedaba bien alrededor. Lo destrabó otra vez la prueba diferencial: `retry_check.py` puso los tres números en pantalla.
- **2026-09-15 (S29)**: la cláusula del `raise` se señaló como el punto grave y en la versión siguiente seguía sin una sola línea de `raise`, pese a haber razonado bien el mecanismo al preguntárselo. Familia "manejo de lo inesperado" (S9): la función promete `-> tuple[str, float]` y devuelve `None`.
- **2026-09-15 (S29)**: la última espera del bucle es tiempo muerto — duerme y sale sin reintentar. Con 3 intentos hay 3 sleeps y solo 2 útiles.
- **2026-09-15 (S29)**: corrió el paso 7 (tipo `predecir`) sin escribir antes la predicción; `RESULTADOS.md` quedó vacío. Un ejercicio de predecir del que se salta la predicción no mide nada.
- **2026-09-16 (S30) — media corrección, tercera y cuarta aparición, las dos el mismo día.** (1) Al mover el `raise` arrastró consigo el `print`, dejándolo **debajo** del `time.sleep`: la línea que anuncia la espera se imprimía cuando la espera ya había pasado — exactamente el punto corregido en la S29. (2) Se le pidió borrar las líneas 131 y 132 (`delay = 0` y `sleep_time = delay`) y borró solo la 131, dejando la lectora sin la creadora → `NameError: name 'delay' is not defined`, en la 132, **antes** de entrar al bucle. Antídoto a exigir: al mover o borrar una línea, decir en voz alta qué *más* cambia de sitio con ella.
- **2026-09-16 (S30) — dijo "listos" sin correr la verificación.** El archivo ni importaba (`NameError` garantizado en la primera llamada) y el comando de verificación se le había dado literal en la misma instrucción. Regla acordada: "listo" significa *"lo corrí y vi la salida esperada"*; si no se corrió, se dice "lo escribí, no lo he corrido".

## Relacionados

- [[Cómo funciona un LLM]] — prerequisito según el roadmap; además, las 3 predicciones de sampling de su ejercicio 01 (parte C) se verifican contra la API real en el ejercicio de ESTE tópico (sesiones [[2026-09-13]]).
- [[APIs REST con FastAPI]] — usados juntos en la sesión [[2026-09-13]]: la separación cliente/request del SDK se explicó reanclando al `AsyncClient` compartido del `lifespan` de su ejercicio `03-api-externa`. Y en la sesión [[2026-09-15]] la forma del `try` / `except X as exc` del backoff se reancló a la que él mismo escribió en `03-api-externa/main.py:151-157`.
- [[Async y concurrencia básica]] — error recurrente que los conecta: "manejo de lo inesperado", abierto desde la S9 (dejar caer errores en silencio). Reapareció en la sesión [[2026-09-15]] con `ask_with_retries` devolviendo `None` al agotar los reintentos en vez de re-lanzar; **cerrado en la sesión [[2026-09-16]]** con el re-raise del error original dentro del `except`.
