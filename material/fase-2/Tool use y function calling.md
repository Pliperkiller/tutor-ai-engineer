---
topic_id: f2.tool-use
aliases: ["f2.tool-use"]
fase: 2
tipo: codigo
estado: visto
nivel: sin_evaluar
repaso_proximo: 2026-10-01
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

**S36 (2026-09-27) — sesión de ejercicio. `01-agente-notas` COMPLETO: 11/11 tests offline + corrida real. visto → aprendido.**

- **`input_schema` no se omite nunca**, ni para una función sin parámetros: se declara `{"type": "object", "properties": {}, "required": []}`. Es lo que le dice al modelo que la entrada válida es `{}`; sin schema puede inventarse un argumento, y `**tool_input` sobre `{}` es la llamada sin argumentos.
- **El ejemplo de formato en la `description` del parámetro evita errores que el modelo no puede adivinar.** `read_note` añade ella misma el `.md`; sin un `e.g. groceries` el modelo puede mandar `groceries.md` y producir `groceries.md.md`. Falla recuperable (`is_error`), pero gasta una vuelta del loop y tokens por un error evitable. Su sitio es la descripción del parámetro, no la de la herramienta.
- **Regla que aplica a N herramientas va en las N**: puso el ejemplo de formato en `read_note` y no en `append_to_note`, que recibe el mismo `name` y tiene la misma trampa.
- **`max_tokens` como constante de módulo** junto a `MODEL`: es una perilla de configuración del cliente, no un dato por conversación. Incrustado en la llamada es un número mágico y se duplica en cuanto haya dos llamadas.
- **Inyección de dependencia del cliente** (`chat(..., *, client)` en vez de un global): es lo que permite conducir el loop entero con un `FakeClient` que reproduce respuestas guionizadas y graba los kwargs — los 11 tests corren sin red y sin gastar un token.
- **`NotImplementedError` es subclase de `RuntimeError`**: un `pytest.raises(RuntimeError)` pasa en verde contra una función sin escribir. Un test puede pasar por la razón equivocada.
- **Observación propia (la mejor del día):** tras el fallo de `shopping`, el modelo se ofreció a *crear* la nota — algo que ninguna herramienta declarada sabe hacer. El modelo propone capacidades que no tiene: limitarlo es trabajo del system prompt y de las descripciones, no algo que el protocolo garantice.
- **Flag de depuración**: `verbose=True` por defecto no es un flag, es un `print`; y un booleano posicional (`run_tool(name, inp, True)`) es ilegible en el punto de llamada — keyword-only.

**S38 (2026-09-29) — REPASO FALLADO POR REINCIDENCIA. aprendido → visto, `next_review` = 2026-10-01.**
- Pregunta: dos bloques `tool_use` en una vuelta, ¿cuántos mensajes al historial y qué pasa si mandas solo un `tool_result`?
- **Primera mitad perfecta:** un solo mensaje `user` con los dos `tool_result` dentro.
- **Segunda mitad, mismo error que en S35:** dijo que "el modelo va a seguir preguntando por el tool faltante". No llega a haber modelo confundido — quien rechaza es **la API, con un 400**, antes de que el modelo vea nada. Corregido con una pista ("¿quién lo ve primero, el modelo o la API?"), pero es la segunda vez que cae en lo mismo.
- Que el `tool_use_id` huérfano lo rechace la **API** y no el modelo es lo que hace que el síntoma sea inmediato y ruidoso en vez de sutil. Volver a preguntarlo en frío el 2026-10-01.

## Errores cometidos
- **2026-09-26 (S35)** — en la predicción creyó que el `id` del `tool_use` "no se crea" al hardcodear el turno del asistente, y que el síntoma sería un modelo confundido. El `id` sí existe (lo devolvió el modelo); lo que se pierde es que viaje en el historial, y quien rechaza es la API con un 400. Llegó solo con una pregunta.
- **2026-09-26 (S35)** — no vio por su cuenta el límite de `is_error`: necesitó el contraejemplo del `TypeError` del despachador para distinguir fallo del entorno de bug propio. Conecta con la debilidad de S9 (dejar caer errores en silencio).

- **2026-09-27 (S36)** — `from test_agent import response` en `agent.py`, puesto por un auto-import del editor cuando escribió `response = client.messages.create(...)`. `response` era una variable local suya. Import circular: pytest ejecuta `test_agent`, que importa `agent`, que pide de vuelta un nombre todavía no definido → `ImportError: partially initialized module`. Reincidencia del self-import de `03-api-externa`. Regla de detección dada: si el nombre importado aparece también a la izquierda de un `=` en el propio archivo, el import sobra.
- **2026-09-27 (S36)** — f-string `f"{type(exc).__name__: {exc}}"`: un solo campo de reemplazo, donde los `:` abren un *format specifier* (la receta de cómo imprimir, como en `f"{pi:.2f}"`). Python intentó usar el mensaje de la excepción como receta → `ValueError: Invalid format specifier`. Correcto: dos campos con los `:` como texto literal entre ellos.
- **2026-09-27 (S36)** — `toosl=TOOLS` en `messages.create`. Detectado por el test (`KeyError: 'tools'`), no a ojo. Peligroso porque en la API real el síntoma es silencioso: sin `tools` el modelo no llama nada y se inventa la respuesta (error típico 4 de la lección).
- **2026-09-27 (S36)** — el `for` del loop terminaba sin `raise`: al agotar `max_turns` la función devolvía `None` en silencio. Misma familia que la debilidad de S9 (`else -> raise`).

- **2026-09-29 (S38)** — reincidencia del error del 2026-09-26: `tool_use` huérfano en el historial → creyó que el síntoma es un modelo confundido; es un 400 de la API.

## Relacionados
- [[Prompt engineering estructurado]] — prerequisito según el roadmap; además, la `description` de una herramienta es un contrato explícito y falla por las mismas razones que un system prompt vago.
- [[Llamadas a APIs de LLM]] — prerequisito de hecho: el loop reusa los bloques de `response.content` filtrados por `type`, el historial stateless y el criterio de escribir el mecanismo a mano antes de usar el ayudante del SDK.
- [[Modelado y validación con Pydantic]] — `input_schema` es JSON Schema, la misma idea de declarar la forma de los datos; un `enum` en el schema es un `Literal[...]` de Pydantic.
- [[Testing con pytest]] — usados juntos en la sesión del 2026-09-27: el ejercicio se verificó con 11 tests offline y un `FakeClient` inyectado, y ahí apareció que `NotImplementedError` es subclase de `RuntimeError` (un test que pasa por la razón equivocada, su debilidad de S7).
- [[Salidas estructuradas]] — el `input_schema` de una herramienta y el JSON Schema de un modelo Pydantic son el mismo objeto con el mismo papel; ambos tópicos se repasaron/trabajaron juntos el 2026-09-29 ([[2026-09-29]]).
