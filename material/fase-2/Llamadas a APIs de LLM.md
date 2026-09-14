---
topic_id: f2.llamadas-api
aliases: ["f2.llamadas-api"]
fase: 2
tipo: codigo
estado: visto
nivel: sin_evaluar
tags: [fase/2, estado/visto]
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

## Errores cometidos

- **2026-09-13**: "429 es un timeout" — confundió una response de rate limit con la ausencia de respuesta. Corregido en sesión y reproducido bien en la repregunta ("si hay status code, hubo respuesta"). Vigilar el vocabulario al clasificar fallos en el ejercicio.
- **2026-09-13** (menor): en el inventario de la request del turno 10 omitió el 10.º mensaje de `user` (la request nueva que dispara la llamada).
- **2026-09-13 (S28) — media corrección, tres pasadas.** En `cost_usd` las dos líneas eran idénticas (mismo conteo, misma tarifa). Tras señalarlo cambió **solo** la tarifa (`[0]`→`[1]`) y dejó `input_tokens`: el costo seguía sin moverse con la salida. Cada línea debía cambiar *dos* cosas respecto a la otra y vio una. Lo que lo destrabó: la prueba diferencial — fijar la entrada y mover la salida de 100 a 900 para ver que el precio no cambiaba.
- **2026-09-13 (S28)**: `elif` dentro de una expresión ternaria → `SyntaxError: expected 'else' after 'if' expression`.
- **2026-09-13 (S28)**: `out_text = block.text` dentro del bucle — sobrescribe en vez de acumular. Verde por accidente (llegó un solo bloque). A favor: predijo las dos consecuencias exactas al preguntárselo.

## Relacionados

- [[Cómo funciona un LLM]] — prerequisito según el roadmap; además, las 3 predicciones de sampling de su ejercicio 01 (parte C) se verifican contra la API real en el ejercicio de ESTE tópico (sesiones [[2026-09-13]]).
- [[APIs REST con FastAPI]] — usados juntos en la sesión [[2026-09-13]]: la separación cliente/request del SDK se explicó reanclando al `AsyncClient` compartido del `lifespan` de su ejercicio `03-api-externa`.
