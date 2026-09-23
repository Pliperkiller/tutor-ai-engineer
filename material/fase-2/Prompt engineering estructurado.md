---
topic_id: f2.prompting-estructurado
aliases: ["f2.prompting-estructurado"]
fase: 2
tipo: mixto
estado: visto
nivel: sin_evaluar
tags: [fase/2, estado/visto]
---

# Prompt engineering estructurado

**Prerequisitos:** [[Llamadas a APIs de LLM]]

**Criterio de dominio:** Diseña 2 versiones de un system prompt para la misma tarea y demuestra con 10 casos de prueba cuál rinde mejor y por qué.

## Apuntes

**S31 (2026-09-17)** — Lección escrita y entregada como tarea: `ejercicios/fase-2/f2.prompting-estructurado/leccion.md` (system prompt como contrato, estructura con etiquetas XML, few-shot, versionado y casos de prueba). Queda de mi parte leerla antes de la próxima sesión y traer las 4 preguntas del final; si las respondo bien en los primeros minutos, el ejercicio va ese mismo día. El estado sigue `no_visto`: aún no hubo lectura ni discusión.


**S32 (2026-09-22) — sesión de lección: las 4 preguntas discutidas.**
- **Costo del few-shot:** con Haiku 4.5 ($1/M de entrada), 100.000 requests: v1 (~20 tokens de system) = $2/mes, v2 (~400) = $40/mes → **$38/mes de diferencia**. El "20×" vale para el system prompt, no para la factura total (el mensaje y la respuesta cuestan igual en las dos versiones).
- **¿Se pagan solos los ejemplos?** Corre v1 y v2 contra **los mismos casos** y compara errores. v2 se paga sola si *errores evitados al mes × costo de cada error > $38*. Con 10 casos la muestra es chica y el modelo no es determinista: cada caso se corre varias veces.
- **Si los ejemplos contradicen las reglas, ganan los ejemplos.** El modelo predice el siguiente token continuando el **patrón** que tiene delante; tres pares input → output en inglés pesan más que una regla `Respond in Spanish`. Reglas y ejemplos tienen que decir lo mismo; la mezcla de idiomas es el síntoma de un prompt que se contradice.
- **Defensa contra inyección = dos piezas que se necesitan entre sí:** las **etiquetas** (`<message>…</message>`) marcan la frontera del dato; la **regla** dice qué hacer con lo de dentro (clasificar, no obedecer). Solo etiquetas: se sabe dónde está el dato, pero nadie dijo que no se obedezca. Solo regla: no se sabe qué texto es "el mensaje". v1 pierde porque una frase imperativa al final parece la instrucción más reciente. Reduce la inyección, no la elimina → se mide con un caso de prueba.
- **Familias de casos de prueba:** camino feliz (**uno por categoría** — prueba reglas y rol), casos borde (vacío, otro idioma, ninguna categoría → `other`, dos categorías — prueba la sección de bordes del contrato), inyección (prueba la frontera). El **formato de salida no es una familia**: es un `assert` que corre sobre **todas** las salidas.

## Errores cometidos

- **2026-09-22 (S32)** — Q2: predijo "lo más probable, español" con la regla en español y ejemplos en inglés, contra la regla en negrita de §3 (ganan los ejemplos). Lo corrigió al conectarlo con el predictor de siguiente token.
- **2026-09-22 (S32)** — primeras respuestas incompletas en las 4 preguntas: la conclusión bien, pero sin el número (Q1), sin el mecanismo (Q3, "un seguro") o sin la justificación (Q4). Con una repregunta sale cada pieza.

## Relacionados
- [[Llamadas a APIs de LLM]] — prerequisito según el roadmap; además, la Q1 del costo de few-shot se calculó con su tabla de precios en la sesión [[2026-09-22]].
- [[Cómo funciona un LLM]] — usados juntos en la sesión [[2026-09-22]]: "ganan los ejemplos" se explicó con el predictor de siguiente token (continuar el patrón).
