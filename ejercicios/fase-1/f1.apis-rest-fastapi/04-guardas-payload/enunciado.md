# 04 — Guardas sobre un payload ajeno (variante)

**Tipo**: completar · **Tiempo estimado**: 10-15 min · **Tópico**: f1.apis-rest-fastapi

## Contexto

En la S16, las dos guardas del payload de Frankfurter las terminó escribiendo el tutor
(regla de las 3 pistas agotada). Esta variante existe para que las escribas TÚ, solo,
sobre un payload nuevo. Es lo único que falta para cerrar el criterio de la Fase 1.

La API es [Open-Meteo](https://open-meteo.com) (pública, sin API key). Su respuesta
real tiene esta forma (recortada):

```json
{
  "latitude": 6.22,
  "current_weather_units": {"temperature": "°C", "windspeed": "km/h"},
  "current_weather": {"time": "2026-09-09T20:45", "temperature": 27.9, "windspeed": 12.6}
}
```

Ojo: `temperature` aparece en DOS sitios. Solo uno es el que tu código lee.

## Las tres reglas (tuyas, de S15/S16)

1. La guarda va **ARRIBA** del acceso que protege (abajo es código muerto).
2. La guarda menciona **EXACTAMENTE** la clave que abre la línea de abajo.
   Dos aperturas encadenadas = dos guardas.
3. `in` sobre un **dict** pregunta por CLAVE; sobre un **string** pregunta por
   SUBCADENA. Verifica sobre qué tipo estás preguntando.

## Qué ya existe y qué haces tú

| Archivo | Estado |
|---|---|
| `extract.py` | **Lo completas tú**: 2 guardas en los `# TODO(student)` |
| `test_extract.py` | Dado (andamiaje). 5 tests. NO lo modifiques |
| `main.py` | Dado (andamiaje). Corre contra la red real |
| `RESPUESTAS.md` | **Lo completas tú**: la predicción P1, ANTES del primer pytest |

Lo único que produces son las 2 guardas: cada una detecta el hueco y lanza
`UpstreamFormatError` con un mensaje que **nombra la clave que falta** (los tests
lo verifican). La excepción ya está definida en `extract.py`.

## Paso a paso

1. Preparación (desde la raíz del repo, Mac/zsh):
   ```sh
   cd ejercicios/fase-1/f1.apis-rest-fastapi/04-guardas-payload
   uv init --bare
   uv add httpx
   uv add --dev pytest ruff
   ```
2. Lee `extract.py` y `test_extract.py`. **ANTES de correr nada**, escribe P1 en
   `RESPUESTAS.md`: con el esqueleto tal cual (sin guardas), ¿cuántos de los 5
   tests pasan, y los que fallan, con QUÉ excepción y quién la lanza?
3. Verifica tu predicción:
   ```sh
   uv run pytest -v
   ```
   Anota en `RESPUESTAS.md` qué acertaste y qué no.
4. Escribe las 2 guardas en `extract.py`. Antídoto acordado en S16: si un test
   falla, **relee el payload del test** antes de tocar la guarda — el dato real
   está en el archivo, dos líneas arriba.
5. Verifica:
   ```sh
   uv run pytest -v        # objetivo: 5/5
   uv run ruff check .     # objetivo: 0 errores, ANTES de decir "listo"
   ```
6. Camino feliz contra la red real:
   ```sh
   uv run python main.py   # imprime la temperatura actual en Medellín
   ```

## Criterio de éxito

- 5/5 tests verdes sin modificar `test_extract.py`.
- `ruff check .` limpio.
- `main.py` imprime la temperatura real.
- P1 escrita ANTES del primer pytest, con la corrección honesta después.
