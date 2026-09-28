---
topic_id: f2.prompting-estructurado
aliases: ["f2.prompting-estructurado"]
fase: 2
tipo: mixto
estado: aprendido
repaso_proximo: 2026-10-04
nivel: sin_evaluar
tags: [fase/2, estado/aprendido]
---

# Prompt engineering estructurado

**Prerequisitos:** [[Llamadas a APIs de LLM]]

**Criterio de dominio:** Diseña 2 versiones de un system prompt para la misma tarea y demuestra con 10 casos de prueba cuál rinde mejor y por qué.

## Apuntes
**S34 (2026-09-24) — sesión de ejercicio: `01-clasificador-tickets` COMPLETO. Criterio de dominio del tópico CUMPLIDO.**

| familia | v1 format_err | v1 wrong | v2 format_err | v2 wrong |
|---|---|---|---|---|
| happy | 0 | 0 | 0 | 0 |
| edge | 3 | 6 | 0 | 0 |
| injection | 0 | 0 | 0 | 0 |
| **TOTAL** | **3** | **6** | **0** | **0** |

- **Los fallos de v1 se repitieron idénticos 3 de 3 corridas**: no era el no-determinismo del modelo, era el prompt. Para eso está `RUNS_PER_CASE = 3` — un fallo que se repite es una falla del contrato; uno que aparece y desaparece es ruido.
- **Un ejemplo few-shot idéntico a un caso de prueba invalida ese caso.** El primer `example3` era el input vacío → `other`, que es exactamente el caso `{'message': '', 'expected': 'other'}`. El modelo no razona ahí: copia el par que tiene escrito arriba. Acierta, y ese acierto no mide nada. (La analogía del examen con la respuesta en el enunciado se rompe en un punto: el modelo no "hace trampa", el few-shot es técnica legítima; lo que falla es medir con el caso cuya respuesta pegaste.)
- **Regla vs ejemplo.** Una regla es general y cubre el vacío, el saludo suelto y los casos en que no pensaste; un ejemplo cubre una sola forma de entrada. v1 escribía un párrafo ante un mensaje vacío porque ninguna regla decía qué hacer cuando no hay nada que clasificar. Ese hueco se tapa en `<rules>`, no en `<examples>`.
- **Las 3 reglas que cerraron los fallos de v1:**
  1. mensaje vacío o sin petición → `other`;
  2. responder con **una sola palabra**, nada más — v1 solo prohibía espacios y símbolos, nunca prohibió añadir una frase alrededor;
  3. *tener la palabra de una categoría no implica pertenecer a ella* — se clasifica por lo que el usuario **pide o reporta**, no por las palabras que aparecen. Es la que desarma la trampa `"I love how clean your billing page looks"` → `other`.
- **Sin fallo que arreglar no hay diferencia que atribuir.** `happy` e `injection` dieron 0 en las dos versiones: el experimento **no prueba nada** sobre el safeguard de inyección, por bien escrita que esté la regla. Para medirla haría falta un caso que v1 sí falle — p. ej. una inyección con cierre de etiqueta falso (`</message><instruction>ignore all…`). Esa es la v3 pendiente.

**S36 (2026-09-27) — review superada sin material (intervalo +2 → +7).**

- Explicó por su cuenta por qué el few-shot de casos borde bate a la definición escrita: **la definición deja la frontera ambigua, el ejemplo la fija**. La categoría no se aprende del texto que la describe, sino del caso que la delimita.
- Receta para JSON limpio, dada completa: instrucción explícita ("responde solo con el JSON, sin texto adicional") **más** ejemplos del par entrada → salida exacta. Lo que no mencionó y se le dio: el *prefill*, abrir el turno del assistant con `{` para que no haya sitio donde escribir el preámbulo.

## Errores cometidos
- **2026-09-24 (S34)** — el primer `example3` copiaba el caso de prueba del mensaje vacío. Corregido al explicarle que ese caso dejaba de medir nada.
- **2026-09-24 (S34)** — puso "qué hacer con el mensaje vacío" como *ejemplo* en vez de como *regla*. Corregido con las reglas 4 y 5.
- **2026-09-24 (S34)** — en `RESULTADOS.md` escribió una causa por familia para las tres, incluidas `happy` e `injection`, donde v1 y v2 sacaron ambas 0. Lo vio y lo corrigió **él** con una sola pregunta ("¿qué demuestra tu experimento sobre esa regla?").
- **2026-09-24 (S34)** — atribuyó el arreglo del caso vacío al *ejemplo*; lo arregló la *regla 4*. Señalado al cierre, no corregido en el archivo.

## Relacionados
- [[Testing con pytest]] — usados juntos en la sesión [[2026-09-24]]: la tabla de v1 vs v2 es el mismo hábito que un test que falla primero, y el ejemplo few-shot copiado del caso de prueba es la versión "prompt" del test que pasa por la razón equivocada.
- [[Llamadas a APIs de LLM]] — prerequisito según el roadmap; además, la Q1 del costo de few-shot se calculó con su tabla de precios en la sesión [[2026-09-22]].
- [[Cómo funciona un LLM]] — usados juntos en la sesión [[2026-09-22]]: "ganan los ejemplos" se explicó con el predictor de siguiente token (continuar el patrón).
- [[Modelado y validación con Pydantic]] — error recurrente que los conecta: el guard invertido, que nació en un validator de Pydantic, se retiró en S11 y reapareció aquí en `is_valid_format` (sesión [[2026-09-23]]).
