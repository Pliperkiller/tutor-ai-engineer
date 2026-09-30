---
topic_id: f2.salidas-estructuradas
aliases: ["f2.salidas-estructuradas"]
fase: 2
tipo: codigo
estado: visto
nivel: sin_evaluar
tags: [fase/2, estado/visto]
---

# Salidas estructuradas

**Prerequisitos:** [[Tool use y function calling|Tool use / function calling]]

**Criterio de dominio:** Extrae datos estructurados de 20 textos libres hacia un modelo Pydantic con tasa de parseo del 100%, incluyendo estrategia de reintento ante salidas inválidas.

## Apuntes

**S37 (2026-09-28)** — Lección escrita y entregada: `ejercicios/fase-2/f2.salidas-estructuradas/leccion.md`, con el `Intake` del capstone (`intake.py`) y tres demos (`demo_parse_failures.py` offline, `demo_structured_parse.py` contra la API, `demo_manual_retry.py` offline con `FakeClient`). Ejes: dos capas de "válido" (sintaxis vs contrato), la escalera prompt → JSON mode → structured outputs (decodificación restringida) → Pydantic + reintento, qué garantiza y qué no el schema, `messages.parse` vs `create` + `output_config`, y reintento con retroalimentación frente al backoff de transporte. Cerré la sesión sin leerla: queda de tarea leerla y traer las 4 preguntas (la 1 es de predicción, antes de correr la demo 1). El estado sigue `no_visto`: aún no hubo lectura ni discusión.

Dato verificado por el tutor sobre el SDK (anthropic 1.9): `messages.parse` lanza `pydantic.ValidationError` igual si la respuesta rompe una regla, si se trunca por `max_tokens` o si es un `refusal`, así que no deja mirar el `stop_reason`. Para distinguir las causas hace falta el camino manual.

**S38 (2026-09-29) — sesión de lección. Lección leída y Q1, Q2 y Q3 discutidas. Q4 pendiente; ejercicio no montado.**

- **Las dos capas son chequeos de TU código, no de la API.** Capa 1 `json.loads`: *¿este texto es JSON sintácticamente?* Capa 2 `Intake.model_validate_json`: *¿cumple el contrato?* La demo 1 no toca la red: los 7 textos están escritos a mano. Analogía: capa 1 es "¿se puede abrir el sobre?", capa 2 es "¿la carta dice lo que pedí?" (se rompe en que un sobre roto a veces deja leer algo; un JSON roto no se parsea, punto).
- **Los cuatro `type` de error de Pydantic no son equivalentes.** `json_invalid`, `literal_error` y `missing` salen del **schema** (sintaxis, enum, campos requeridos). `value_error` sale de **código Python tuyo** (`@field_validator`) que el schema no puede expresar. Esa distinción es exactamente la que decide qué sobrevive a structured outputs.
- **Validar ≠ decodificación restringida.** Validar: el texto malo **llega** a tu programa y tu código lo rechaza — aduana, el paquete entró y lo devuelves. Structured outputs: el servidor **borra de la lista de candidatos**, en cada token, todo lo que rompería el schema; el texto malo **nunca se genera**. Después de `{"case_type": "` los únicos tokens disponibles son los que empiezan una de las 4 categorías: `"car accident"` no es rechazado, es **inalcanzable**. Es la fábrica que no puede producir la pieza mala. Donde la analogía se rompe: la fábrica controla la **forma**, no el **sentido** ni que llegue a terminar la pieza.
- **De las 7 variantes, con structured outputs sobreviven DOS, y por razones distintas:**
  - `truncated` — las rieles garantizan que cada token emitido es un **prefijo válido**, no que la generación **llegue al final**. Con `max_tokens=20` y un `Intake` de ~80, sale texto correcto y cortado. Se detecta en `stop_reason == "max_tokens"`, no en el validador.
  - `future date` — `"2031-01-15"` es una fecha impecable para el schema. JSON Schema conoce la **forma** (`YYYY-MM-DD`), no la **regla** ("no posterior a hoy"). Ahí el `@field_validator` es insustituible.
  - **Conclusión: structured outputs reduce la superficie de fallo; no elimina la validación.**
- **Un campo requerido no-anulable es una orden de inventar.** Con `incident_date: date` (sin `| None`) y un mensaje sin fecha, el modelo **no puede emitir `null`** y tampoco se calla: siempre elige el token más probable de los permitidos. Resultado: una fecha fabricada dentro de un `Intake` **válido**, sin una sola excepción. Peor que un error, porque un error detiene el pipeline y se ve; un valor inventado y bien formado es indistinguible de un dato bueno aguas abajo — en el capstone, un plazo de prescripción calculado sobre una fecha ficticia.
- **Un LLM no tiene reloj.** "Hace un mes" no es calculable si el system prompt no dice qué día es hoy. De ahí el `Today is {date.today().isoformat()}` de las demos.
- **`null` ambiguo.** Poner `null` cuando el mensaje dice "last month" hace que `null` signifique dos cosas indistinguibles: *"no habló de tiempo"* y *"habló, impreciso"*. La salida que no pierde información y tampoco inventa es un campo aparte con la frase cruda (`incident_date_text: str | None = "last month"`).
- **Transporte vs contenido, la prueba rápida:** *¿tienes en la mano un texto generado por el modelo?* No → transporte (conexión rechazada, timeout, 429, 500, 401: el modelo ni se enteró de que existías). Sí y está mal → contenido (200 OK, el transporte funcionó perfecto).
- **Taxonomía de reintento** (Q3):

| situación | capa | ¿reintento? | forma |
|---|---|---|---|
| `ValidationError`: summary de 230 | contenido | sí | retroalimentación inyectando `{exc}` — el propio error trae campo, valor y motivo |
| `stop_reason == "max_tokens"` | contenido | sí, **cambiando algo** | subir `max_tokens` (primera opción), o pedir salida más corta |
| `stop_reason == "refusal"` | contenido | **no** | revisión humana; reintentar es discutir con un filtro de seguridad |
| `RateLimitError` 429 | transporte | sí | backoff + jitter, y `retry-after` manda sobre tu `2**n`. Único caso donde la request **idéntica** es lo correcto |
| `case_type` válido pero equivocado | contenido | **no detectable** | evals sobre casos etiquetados + juez (LLM-as-judge o humano) |

- **Criterio para decidir "retroalimentación sí":** ¿el modelo **puede** cumplir? Acortar una frase, sí. Dejar de negarse, no. Adivinar un dato que no está en el mensaje, tampoco.
- **`count_tokens` (S27) es el desempate de `max_tokens`:** cuenta un `Intake` bueno conocido. Si el mínimo válido ya supera el presupuesto, el modelo no estaba siendo verboso — tu presupuesto estaba mal puesto, y ninguna retroalimentación lo salva.
- **El fallo que ninguna capa ve.** `employment` **es** un valor permitido del `Literal`: el validador comprueba pertenencia al conjunto, y pertenece. El fallo no es "forma inválida" sino "el valor válido equivocado para este mensaje". No hay `try`, no hay `except`, no hay `if`: `save_to_case_file(intake)` se ejecuta. Analogía: un formulario de estado civil donde escribir "soltero" siendo casado pasa la validación sin un rasguño — comprueba la forma, no si dices la verdad. Detectarlo exige leer el `summary` y juzgar si encaja: un juez. Por eso esto **se mide** (evals), no se reintenta.

## Errores cometidos

- **2026-09-29 (S38)** — en la predicción de Q1 marcó `future date` como OK/OK. Se le pasó que el `@field_validator` de `reject_future_dates` es código propio, no schema; es la única de las 7 filas cuyo error no lo genera Pydantic a partir de los tipos.
- **2026-09-29 (S38)** — creía que "capa 1" era algo que hacía la API ("la API tiene una manera de aceptar algunos casos"). Las dos capas son chequeos de su propio código y la demo 1 es enteramente offline.
- **2026-09-29 (S38)** — dijo que `truncated` **desaparece** con structured outputs. Raíz: modelaba structured outputs como "me llega y lanzo excepción" en vez de "no se genera". Corregido con `max_tokens=20`: las rieles garantizan prefijo válido, no terminación.
- **2026-09-29 (S38)** — en Q3(e) propuso comprobar con el `field_validator` si `employment` es un `case_type` permitido. Lo es. Confundía "valor inválido" con "valor válido equivocado". Necesitó el boceto de código (sin `try`, sin `if`) para ver que ninguna línea se entera.

## Relacionados

- [[Tool use y function calling|Tool use / function calling]] — prerequisito según el roadmap; además comparten mecanismo: el `input_schema` de una herramienta y el JSON Schema de `Intake` son el mismo objeto cumpliendo el mismo papel (declararle la forma al modelo).
- [[Llamadas a APIs de LLM]] — usados juntos el 2026-09-29 ([[2026-09-29]]): la taxonomía de reintento de Q3 se apoya entera en el backoff, el `stop_reason` y la distinción transitorio/permanente de ese tópico, y el repaso fallado de hoy fue justamente `max_tokens`.
- [[Modelado y validación con Pydantic]] — prerequisito de hecho: `Literal`, `Field(max_length=...)` y `@field_validator` son el contrato; hoy quedó claro cuál de los tres puede delegarse al schema y cuál no.
- [[Prompt engineering estructurado]] — un error recurrente los conecta: "verde por la razón equivocada". Allí fue un evaluador que aprobaba salidas malas; aquí, un `Intake` válido con el `case_type` inventado que ninguna capa detecta.
