# Resultados — 01-cliente-anthropic

## Predicción del paso 7 (escríbela ANTES de correr el comando)

Con una key inválida, `ask_with_retries` va a...
(¿reintenta o muere de inmediato? ¿qué excepción? ¿cuánto tarda en morir, aprox?)

**Predicción:**

**Lo que pasó de verdad:**

## Parte C verificada contra la API real (predicciones de la S26)

| configuración | predije (S26) | salió (distintas de 5, o RECHAZADA) | ¿acerté? |
|---|---|---|---|
| `temperature = 0` | 1 | | |
| `temperature = 1` | 5 | | |
| `top_p = 0.1` | 5 (con duda: "depende de qué tan plana sea la curva") | | |

> Si alguna fila sale RECHAZADA por la API, eso no invalida el ejercicio: anota el
> mensaje de error y responde abajo por qué un modelo actual quitaría ese dial.

## Una frase por fila: por qué salió lo que salió

- `temperature = 0`:
- `temperature = 1`:
- `top_p = 0.1`:
