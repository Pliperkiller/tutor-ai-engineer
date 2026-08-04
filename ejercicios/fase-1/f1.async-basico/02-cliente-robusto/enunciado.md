# f1.async-basico · 02 — Cliente robusto: timeouts y errores en lote

- Herramienta: httpx (timeout) + asyncio.gather(return_exceptions=True)
- Tipo: script (+ predicción escrita antes de ejecutar)
- Tiempo objetivo: 12 min
- Directorio de trabajo: `ejercicios/fase-1/f1.async-basico/02-cliente-robusto/`

## Por qué esta herramienta
En el mundo real los servidores fallan y se cuelgan. Sin timeout, tu cliente
espera respuestas que nunca llegan; sin `return_exceptions=True`, una sola
excepción en el lote te hace perder los 9 resultados buenos (lo viste en
`demo.py`). Un cliente de producción SIEMPRE acota la espera y clasifica
qué salió bien y qué no.

## Objetivo
Escribe `robust_client.py`: pide los 10 modelos (`/models/0` … `/models/9`)
de forma concurrente a un servidor donde **el id 3 devuelve HTTP 500** y
**el id 7 se cuelga 10 segundos**, y termina en **~1 segundo** clasificando
los resultados en tres grupos:

```
ok:          8 models -> [0, 1, 2, 4, 5, 6, 8, 9]
http_errors: [3]
timeouts:    [7]
total time:  ~1.0s
```

Restricciones:
- UN solo `AsyncClient` compartido, con **timeout de 1.0s** (se pasa al
  crear el client: `httpx.AsyncClient(timeout=1.0)`).
- `gather` con `return_exceptions=True`.
- Usa `response.raise_for_status()` para que un 500 se convierta en excepción.
- Datos de la herramienta (los tipos que vas a distinguir con `isinstance`):
  - timeout vencido -> `httpx.TimeoutException`
  - status 4xx/5xx tras `raise_for_status()` -> `httpx.HTTPStatusError`
  - cualquier otra excepción inesperada: re-lánzala (`raise`), no la tragues.
- Mide el tiempo total con `time.perf_counter()` como en el ejercicio 01.

## Paso a paso
0. **Preparación** — En esta carpeta ya existen: `demo.py` (demo del tutor,
   solo lectura) y `flaky_server.py` (infraestructura, NO editar). Tú creas
   UN archivo: `robust_client.py`, en esta misma carpeta. No hay dependencias
   nuevas (httpx ya lo tienes del ejercicio 01). Levanta el servidor en una
   terminal aparte y déjalo corriendo:
   ```bash
   python flaky_server.py
   ```
1. **Predicciones primero** — abre `robust_client.py` y escribe como
   comentario inicial (en inglés):
   - P1: ¿cuánto tardará el run completo y POR QUÉ ese número?
   - P2: ¿qué objeto exacto esperas en la posición del id 7 y cuál en la
     del id 3 dentro de la lista que devuelve `gather`?
2. **`fetch_model(client, model_id)`** — corrutina que hace el GET a
   `http://127.0.0.1:8124/models/{model_id}`, convierte errores HTTP en
   excepción y devuelve el JSON parseado (igual espíritu que en 01).
3. **`fetch_all_robust()`** — abre el `AsyncClient` compartido con el
   timeout, lanza las 10 requests con `gather(..., return_exceptions=True)`
   y devuelve la lista (mezcla de dicts y excepciones).
4. **Clasificación** — recorre los pares (model_id, resultado) y sepáralos
   en `ok` / `http_errors` / `timeouts` según su tipo. Excepción de otro
   tipo: re-lánzala.
5. **Resumen** — imprime los tres grupos y el tiempo total medido, en el
   formato del Objetivo (aproximado, no hace falta idéntico).
6. **Verifica**: con el servidor corriendo, en otra terminal:
   ```bash
   python robust_client.py
   ```
   Confirma: 8 ok, el 3 en http_errors, el 7 en timeouts, total ~1.0-1.2s
   (si te da ~10s, el timeout no está actuando). Compara contra tus P1/P2 y
   anota al final del comentario si acertaste y qué te sorprendió.

## Convención de código
Variables, funciones, docstrings y comentarios en inglés (estándar del repo).
Ojo con nombres que sombrean builtins (`id`, `iter`) — te pasó en el 01.

## Cómo se evalúa
El tutor levanta `flaky_server.py` y corre `python robust_client.py`.
Criterio: clasificación correcta (8/1/1), tiempo total ~1s (el timeout
corta al colgado), un solo AsyncClient, predicciones escritas y comentadas
tras la ejecución, identificadores en inglés.

## Pistas
Pídelas al tutor: son escalonadas y no están escritas aquí a propósito.
