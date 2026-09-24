# Resultados — v1 (vibras) vs v2 (contrato)

## Predicción (paso 5, ANTES de correr v1)

- ¿Qué familia crees que va a fallar más con v1, y por qué?
  > edge cases por que pueden conducir a confundir a nuestro llm
- ¿Crees que v1 va a tener errores de formato? ¿En qué casos?
  > si, en los edge cases y en los prompt injection

## Tabla (copia los TOTAL y las filas de `run_eval.py`)

| familia   | v1 format_err | v1 wrong | v2 format_err | v2 wrong |
|-----------|---------------|----------|---------------|----------|
| happy     |               |          |               |          |
| edge      |               |          |               |          |
| injection |               |          |               |          |
| **TOTAL** |               |          |               |          |

## ¿Cuál rinde mejor y por qué?

Por cada familia donde v1 y v2 difieren: qué pieza del contrato de v2 (rol, regla, formato, caso borde, ejemplo, frontera de datos) explica la diferencia. Una línea por familia, con la causa, no solo el dato.

- happy:
- edge:
- injection:

## ¿Tu predicción acertó?

>

## Si v2 falló algún caso

Qué cambiarías en el prompt (una v3) y qué tendrías que volver a correr antes de aceptar ese cambio.

>
