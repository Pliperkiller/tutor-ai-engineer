# Resultados — 01-cliente-anthropic

## Predicción del paso 7 (escríbela ANTES de correr el comando)

Con una key inválida, `ask_with_retries` va a...
(¿reintenta o muere de inmediato? ¿qué excepción? ¿cuánto tarda en morir, aprox?)

**Predicción:**
va a levantar una excepcion ya que no la tenemos controlado en el try catch de la linea 133, dicho try catch solo controla excepciones de la lista TRANSIENT_ERRORS que corresponden a las admitidas para los retry
la excepcion que se levanta: anthropic.authenticationerror
**Lo que pasó de verdad:**
Muere de inmediato y levanta la excepcion anthropic.authenticationerror

## Parte C verificada contra la API real (predicciones de la S26)

| configuración | predije (S26) | salió (distintas de 5, o RECHAZADA) | ¿acerté? |
|---|---|---|---|
| `temperature = 0` | 1 |1 |si |
| `temperature = 1` | 5 |3 |parcialmente, a veces si son 5 otras veces 3, etc |
| `top_p = 0.1` | 5 (con duda: "depende de qué tan plana sea la curva") |1 |no |

> Si alguna fila sale RECHAZADA por la API, eso no invalida el ejercicio: anota el
> mensaje de error y responde abajo por qué un modelo actual quitaría ese dial.

## Una frase por fila: por qué salió lo que salió

- `temperature = 0`: se esta tomando 'PlantAlert' como la respuesta mas probable a mi solicitud por ende solo sale esa
- `temperature = 1`: se retornan varias opciones debido a que una temperatura 1 permite una curva mas plana de opciones
- `top_p = 0.1`: a pesar de tener una curva mas plana, 'PlantAlert' ya cubre un 10% de probabilidad
