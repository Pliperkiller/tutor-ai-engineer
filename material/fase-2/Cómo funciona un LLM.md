---
topic_id: f2.como-funciona-llm
aliases: ["f2.como-funciona-llm"]
fase: 2
tipo: conceptual
estado: aprendido
nivel: sin_evaluar
repaso_proximo: 2026-09-20
tags: [fase/2, estado/aprendido]
---

# Cómo funciona un LLM

**Prerequisitos:** [[Testing con pytest]]

**Criterio de dominio:** Redacta un diseño de 1 página que explique tokens/contexto/temperatura y prediga el efecto de 3 configuraciones de sampling, verificando luego las predicciones contra la API real.

## Apuntes
**S26 (2026-09-10/11)** — Lección completa en `ejercicios/fase-2/f2.como-funciona-llm/leccion.md`; demo `01-predecir-tokens/demo_tokens.py` (tiktoken, sin API key).
- **Un LLM predice el siguiente token**, uno a la vez (autoregresivo): 300 tokens de salida = 300 cálculos completos. Por eso la salida cuesta más que la entrada.
- **Token = pieza de una tabla fija (vocabulario, ~200k entradas) construida con BPE** fusionando los pares más frecuentes del corpus. Consecuencias vistas con datos: ` gato` con espacio es 1 pieza y `gato` sin espacio son 2 (`g`+`ato`) porque la forma frecuente en texto es la que lleva espacio delante; `cat` tiene pieza en las tres formas porque el corpus tiene más inglés; los números van de 3 en 3 cifras; espacios extra, tabulador y salto de línea son piezas propias y cuestan tokens; mayúscula = pieza distinta.
- **El modelo no ve letras** (por eso falla contando las "r" de strawberry): lo determinista lo hace el código, y si debe ocurrir en medio de la conversación, el modelo llama al código (tool use, [[Tool use y function calling]]).
- **Ventana de contexto** = entrada + salida en UNA llamada (Claude Opus 5 / Sonnet 5: 1M; Haiku 4.5: 200k). **Sin memoria entre llamadas**: la app reenvía el historial entero cada turno; el costo acumulado de N turnos es cuadrático (500·N(N+1)/2), no lineal ni "fibonacci". Pasarse = error 400, no respuesta recortada.
- **Temperatura** divide los logits antes del softmax: T→0 afila (casi greedy), T=1 tal cual, T>1 aplana. Tabla calculada: ` azul` 99,3 % (T=0,2) / 66,7 % (T=1) / 47,3 % (T=2). El dado se tira POR TOKEN. T=0 no es determinista (coma flotante en GPU, empates). **top_p** recorta desde arriba hasta acumular p: solo QUITA candidatos; cuántos quedan depende de lo plana que sea la tabla real (punto que el estudiante defendió con razón). En Claude 4.7+/5 `temperature`/`top_p`/`top_k` dan 400: se controla con `effort`.
- **Embeddings**: significado → vector; cercanía (coseno) = similitud. Base de RAG (F3). Vectores de modelos distintos no se comparan.
- Tokenizador de Claude ≠ tiktoken: para Claude, la cuenta oficial es `count_tokens` (se usa en [[Llamadas a APIs de LLM]]).

**S28 (2026-09-13) — repaso en frío superado** (sin material a la vista), intervalo a +7.
- ` gato` 1 pieza vs `gato` 2: dado con mecanismo propio ("la forma frecuente en el corpus es la que lleva espacio"). Precisión: sabemos que son **2** piezas porque lo midió; *cuáles* son depende del vocabulario.
- `T=0` no determinista: "fluctuaciones en los cálculos de la GPU". Completado: la fluctuación solo cambia el resultado cuando dos candidatos están casi empatados, y como la generación es token a token, uno distinto cambia todo lo que sigue.
- `top_p=0.1`: formulación correcta al segundo intento — *ordena de mayor a menor y acumula desde arriba hasta el 10 %*. Con tabla plana (top al 2 %) sobreviven 5-10 candidatos; con tabla concentrada (top al 92 %), uno solo.

**S30 (2026-09-16) — deuda de la S26 cerrada: las predicciones de sampling, medidas contra la API real.** `sampling_check.py`, 15 requests (3 configuraciones × 5) a través de su propio `ask()`.

| configuración | predijo (S26) | salió | lectura |
|---|---|---|---|
| `temperature = 0` | 1 distinta | **1** | acertó — siempre el token más probable, misma respuesta siempre |
| `temperature = 1` | 5 distintas | **3** | parcial — y su lectura es la correcta |
| `top_p = 0.1` | 5 distintas | **1** | falló la predicción, **acertó la causa** |

- **Que salgan 3 distintas de 5 muestras no significa que el modelo tenga 3 candidatos.** Con 5 muestras de una distribución amplia puedes repetir por puro azar. Lo dijo él: *"a veces sí son 5, otras veces 3"*. Para ver el abanico real hacen falta muchas más muestras que 5.
- **`top_p = 0.1` da MENOS variedad, no más** — el error de la S26, ahora cerrado con el caso concreto y medido. Su causa, textual: *"a pesar de tener una curva más plana, 'PlantAlert' ya cubre un 10% de probabilidad"*. Eso es **acumulación desde arriba**: se ordenan los candidatos de mayor a menor y se corta al llegar al 10% acumulado; si el primero ya llega solo al 10%, la lista se queda con **un único candidato** → una sola respuesta posible. No es un umbral por token ni un reparto del 10%.
- **Pregunta de control respondida sin andamiaje:** `top_p = 0.9` → más respuestas distintas, porque acumula candidatos hasta el 90% y la lista de la que muestrea es mucho más larga.
- **`temperature` y `top_p` ya no viajan en la firma de la Messages API** (SDK `anthropic` 1.5.0): llegan a Haiku 4.5 por `extra_body`. El dial existe en el modelo, no en la superficie de la API.

**Falta para `dominado`:** la única pieza del `criterio_dominio` sin producir es el **diseño de 1 página** que explique tokens / ventana de contexto / temperatura. La parte de "predecir 3 configuraciones de sampling y verificarlas contra la API real" está hecha y verificada.

## Errores cometidos
- **2026-09-11** — Predijo `gato`/`Gato` como 1 token "porque es una palabra simple": simple ≠ frecuente en el corpus (y el corpus tiene más inglés). Corregido con la tabla real.
- **2026-09-11** — Razonó bien casa/` casa` (forma frecuente = con espacio) y aun así marcó "mismo número de tokens: sí", media hora después de ver el caso gato. No explicó la contradicción (3 preguntas sin respuesta; se dejó por fatiga). Repreguntar el 09-13.
- **2026-09-11** — Nombró "fibonacci" la serie 500/1500/3000 del costo acumulado: es cuadrática (suma 1..N). Los números estaban bien.
- **2026-09-11** — `top_p = 0.1` leído al revés: "reparto el 10 % entre muchos nombres" (más variedad) en vez de "me quedo con los de arriba hasta acumular 10 %" (menos). Corregido el porqué en RESPUESTAS.md; retención sin verificar.
- **2026-09-11** — Parte B: pegó la salida de los pares y marcó bien/mal sin una causa (patrón "dato en vez de frase", 2.ª vez). Las causas salieron con frase con huecos.
- **2026-09-11** — Q4: propuso "un diccionario de frecuencias de letras por token" para que el modelo cuente letras: nadie por dentro del modelo puede leerlo; el conteo lo hace el código.
- **2026-09-13 (S28)** — `top_p`, **variante nueva del error**: ya no lo lee al revés, pero su primera respuesta fue *"escoge los tokens que tienen 10 % o más de probabilidad cada uno"* — umbral **por token** en vez de acumulación desde arriba. Se autocorrigió solo al devolverle su propio caso de la S26 (tabla plana con el top al 2 %, donde él mismo defendió que quedan 5-10 candidatos). En el repaso del 09-20, preguntarlo **sin** darle ese ejemplo.
- **2026-09-16 (S30) — `top_p` leído al revés: CERRADO.** Abierto en la S26 (lo entendió como "reparto el 10% entre muchos candidatos" = más variedad), corregido en discusión en la S28 pero sin el ancla del caso concreto que la nota de entonces pedía. Hoy la API le contradijo la predicción (predijo 5 respuestas distintas, salió 1) y **escribió la causa correcta por su cuenta**. Aprendió del número que lo refutaba en vez de defender la predicción.

## Relacionados
- [[Testing con pytest]] — prerequisito según el roadmap.
- [[2026-09-11]] — sesión 26: lección, 4 preguntas y ejercicio 01-predecir-tokens (a).
- [[2026-09-13]] — sesión 28: repaso en frío superado (ítems ` gato`, `top_p`, `T=0`).
- [[Llamadas a APIs de LLM]] — ahí se verificaron las 3 predicciones de sampling de la parte C contra la API real (hecho en la sesión [[2026-09-16]], con `sampling_check.py` corriendo sobre el `ask()` que él escribió) y se usa `count_tokens`.
- [[2026-09-16]] — sesión 30: la verificación de la parte C cierra el `top_p` leído al revés y sube este tópico a `aprendido`.
