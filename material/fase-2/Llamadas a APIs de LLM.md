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
- **API key**: env var por máquina (`~/.zshrc` / perfil de PowerShell), jamás en el repo; el código solo conoce el *nombre* de la variable.

**Acordado:** ejercicio extra tras el principal — mini-SDK con httpx a pelo contra su Ollama remoto (RTX 5080): armar el POST, parsear SSE a mano, backoff propio.

## Errores cometidos

- **2026-09-13**: "429 es un timeout" — confundió una response de rate limit con la ausencia de respuesta. Corregido en sesión y reproducido bien en la repregunta ("si hay status code, hubo respuesta"). Vigilar el vocabulario al clasificar fallos en el ejercicio.
- **2026-09-13** (menor): en el inventario de la request del turno 10 omitió el 10.º mensaje de `user` (la request nueva que dispara la llamada).

## Relacionados

- [[Cómo funciona un LLM]] — prerequisito según el roadmap; además, las 3 predicciones de sampling de su ejercicio 01 (parte C) se verifican contra la API real en el ejercicio de ESTE tópico (sesión [[2026-09-13]]).
