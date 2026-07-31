# f1.async-basico · 01 — Cliente HTTP concurrente

- Herramienta: asyncio + httpx
- Tipo: completar
- Tiempo objetivo: 12 min
- Directorio de trabajo: `ejercicios/fase-1/f1.async-basico/01-cliente-concurrente/`

## Por qué esta herramienta
Un cliente HTTP secuencial desperdicia casi todo su tiempo esperando la red.
Antes se resolvía con threads (caros, sincronización manual); `asyncio` logra
la misma concurrencia con un solo hilo y un event loop. `httpx` es el cliente
HTTP moderno que habla async de forma nativa (`requests` no puede).

## Objetivo
Contra una API local que tarda ~0.3s por request, obtener los 10 modelos de
`GET /models/{id}` de dos formas — secuencial y concurrente — y medir la
diferencia. Meta: la versión concurrente debe bajar de ~3s a <1s.

## Paso a paso

0. **Preparación** — Ya existen: `server.py` (API mock del tutor, NO se toca)
   y `client.py` (esqueleto con 3 TODOs que completas tú). Abre DOS
   terminales en este directorio. En la primera, deja corriendo:
   ```bash
   python server.py
   ```
1. **PREDICCIÓN (antes de escribir código)** — escribe al final de este
   archivo, bajo `## Predicción`: ¿cuántos segundos estimas para la versión
   secuencial y cuántos para la concurrente? (10 requests × 0.3s c/u).
2. **TODO 1** en `client.py`: `fetch_model` — un GET con el `AsyncClient`,
   `raise_for_status()` y devolver el JSON parseado.
3. **TODO 2**: `fetch_all_sequential` — un solo `AsyncClient` (context
   manager `async with`), un loop que hace `await` request por request.
4. **TODO 3**: `fetch_all_concurrent` — mismo cliente único, pero las 10
   corrutinas registradas de una vez con `asyncio.gather`.
5. **Verifica**: en la segunda terminal corre
   ```bash
   python client.py
   ```
   y confirma: dos tiempos impresos, `results match: OK`, y el concurrente
   por debajo de 1s. Compara contra tu predicción.

## Convención de código
Variables, funciones, docstrings y comentarios en inglés (estándar del repo).

## Cómo se evalúa
El tutor ejecuta `python client.py` (con `server.py` corriendo) y lee tu
código. Criterio: ambas versiones devuelven los mismos 10 modelos, la
concurrente muestra ganancia clara (≥3x) y la predicción está escrita.

## Pistas
Pídelas al tutor: son escalonadas y no están escritas aquí a propósito.

## Predicción
version secuencial: como mínimo 10 * 0.3 segundos = 3 segundos aprox 
version concurrente: como mínimo 0.3 segundos