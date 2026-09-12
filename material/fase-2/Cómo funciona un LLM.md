---
topic_id: f2.como-funciona-llm
aliases: ["f2.como-funciona-llm"]
fase: 2
tipo: conceptual
estado: visto
nivel: sin_evaluar
repaso_proximo: 2026-09-13
tags: [fase/2, estado/visto]
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

## Errores cometidos
- **2026-09-11** — Predijo `gato`/`Gato` como 1 token "porque es una palabra simple": simple ≠ frecuente en el corpus (y el corpus tiene más inglés). Corregido con la tabla real.
- **2026-09-11** — Razonó bien casa/` casa` (forma frecuente = con espacio) y aun así marcó "mismo número de tokens: sí", media hora después de ver el caso gato. No explicó la contradicción (3 preguntas sin respuesta; se dejó por fatiga). Repreguntar el 09-13.
- **2026-09-11** — Nombró "fibonacci" la serie 500/1500/3000 del costo acumulado: es cuadrática (suma 1..N). Los números estaban bien.
- **2026-09-11** — `top_p = 0.1` leído al revés: "reparto el 10 % entre muchos nombres" (más variedad) en vez de "me quedo con los de arriba hasta acumular 10 %" (menos). Corregido el porqué en RESPUESTAS.md; retención sin verificar.
- **2026-09-11** — Parte B: pegó la salida de los pares y marcó bien/mal sin una causa (patrón "dato en vez de frase", 2.ª vez). Las causas salieron con frase con huecos.
- **2026-09-11** — Q4: propuso "un diccionario de frecuencias de letras por token" para que el modelo cuente letras: nadie por dentro del modelo puede leerlo; el conteo lo hace el código.

## Relacionados
- [[Testing con pytest]] — prerequisito según el roadmap.
- [[2026-09-11]] — sesión 26: lección, 4 preguntas y ejercicio 01-predecir-tokens (a).
- [[Llamadas a APIs de LLM]] — ahí se verifican las 3 predicciones de sampling de la parte C contra la API real y se usa `count_tokens` (segunda mitad del criterio de dominio de este tópico).
