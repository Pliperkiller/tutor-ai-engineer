---
topic_id: f2.tool-use
aliases: ["f2.tool-use"]
fase: 2
tipo: codigo
estado: visto
nivel: sin_evaluar
tags: [fase/2, estado/visto]
---

# Tool use / function calling

**Prerequisitos:** [[Prompt engineering estructurado]]

**Criterio de dominio:** Implementa el loop completo de tool calling con 3 herramientas reales y manejo de errores de herramienta sin romper la conversación.

## Apuntes
**S35 (2026-09-26) — sesión de lección. Lección leída, 4 preguntas discutidas. Ejercicio NO empezado.**

- **El modelo nunca ejecuta nada.** Pide. Devuelve un bloque `tool_use` (`id`, `name`, `input` ya parseado como dict) y tu código ejecuta, en tu máquina, con tus permisos. El modelo es un cerebro sin manos; las manos son tuyas.
- **Una herramienta son dos objetos separados** que nadie obliga a coincidir: la función Python real y la declaración (`name`, `description`, `input_schema` en JSON Schema) que viaja en `tools`. Desincronizarlas no da error hasta producción.
- **La `description` es prompt, no documentación.** Decir *cuándo* llamarla ("Call this whenever the user asks about the current time") sube la tasa de acierto; decir solo qué hace deja al modelo inventándose la respuesta sin llamar nada — y eso no produce ningún error visible.
- **El historial crece con DOS mensajes por vuelta**: `{"role": "assistant", "content": response.content}` **entero** (si guardas solo el texto, el bloque `tool_use` desaparece) y `{"role": "user", "content": [tool_result, ...]}`. El resultado va como `user` porque la API solo tiene dos roles: `user` es "el lado de afuera del modelo", no "la persona".
- **`tool_use_id` es el ticket de lavandería**: el único vínculo entre petición y respuesta. Un id sin dueño en el historial lo rechaza **la API con un 400**, antes de que el modelo vea nada — no es un modelo confundido, es que no hay respuesta.
- **Llamadas paralelas**: varios `tool_use` en un turno → todos los `tool_result` en **un solo** mensaje `user`. Razón dura: falta uno y es 400. Razón blanda: partirlos le enseña al modelo a dejar de pedir en paralelo, y cada vuelta extra reenvía el historial completo (más latencia y más tokens de entrada pagados).
- **`is_error: True` mantiene viva la conversación**: el fallo llega al modelo como información y puede reintentar con otros argumentos, probar otra herramienta o avisar al usuario. El contenido del error es prompt: dice qué falló **y qué alternativas hay**.
- **El límite de `is_error`** (lo que costó ver): fallos del **entorno** (red caída, dato inexistente, argumento inválido del modelo) → `is_error`. Fallos de **tu código** (`TypeError`/`KeyError` del despachador) → que revienten. Enmascararlos hace que el modelo reintente contra un despachador roto, gastando turnos y dinero, y el bug nunca se ve.
- **`stop_reason`** es la señal oficial de salida del loop (`tool_use` vs `end_turn`), no "¿hay bloques tool_use?": además distingue el final legítimo de un corte por `max_tokens`.
- **Seguridad** (Q4, la respondió bien solo): la herramienta corre con los permisos de la app. Whitelist + shell restringido. Lo que le faltaba: la **inyección de prompt** — el modelo obedece a cualquier texto que entre en su contexto (una página descargada, un documento, una fila de la BD), así que la whitelist va en el código; el system prompt no es una frontera de seguridad.
- **Loop a mano, no `tool_runner`**: mismo criterio que los reintentos escritos a mano en [[Llamadas a APIs de LLM]] — una caja negra no se depura.

## Errores cometidos
- **2026-09-26 (S35)** — en la predicción creyó que el `id` del `tool_use` "no se crea" al hardcodear el turno del asistente, y que el síntoma sería un modelo confundido. El `id` sí existe (lo devolvió el modelo); lo que se pierde es que viaje en el historial, y quien rechaza es la API con un 400. Llegó solo con una pregunta.
- **2026-09-26 (S35)** — no vio por su cuenta el límite de `is_error`: necesitó el contraejemplo del `TypeError` del despachador para distinguir fallo del entorno de bug propio. Conecta con la debilidad de S9 (dejar caer errores en silencio).

## Relacionados
- [[Prompt engineering estructurado]] — prerequisito según el roadmap; además, la `description` de una herramienta es un contrato explícito y falla por las mismas razones que un system prompt vago.
- [[Llamadas a APIs de LLM]] — prerequisito de hecho: el loop reusa los bloques de `response.content` filtrados por `type`, el historial stateless y el criterio de escribir el mecanismo a mano antes de usar el ayudante del SDK.
- [[Modelado y validación con Pydantic]] — `input_schema` es JSON Schema, la misma idea de declarar la forma de los datos; un `enum` en el schema es un `Literal[...]` de Pydantic.
