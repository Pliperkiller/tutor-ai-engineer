---
description: Abrir una sesión de estudio de ~30 min siguiendo el roadmap (se cierra con /end-sesion)
---
Ejecuta el protocolo /start-sesion definido en CLAUDE.md, paso a paso: apertura → repasos → concepto → ejercicio. NO cierres la sesión: el cierre es `/end-sesion`.

Argumentos: $ARGUMENTS
- Si viene un topic_id, úsalo como tema del día SOLO si sus prerequisitos y los tópicos anteriores necesarios están en `aprendido` o mejor; si no, explica por qué y propone el tópico correcto según `posicion_actual`.
- Si viene vacío, continúa desde `progress.json.pendiente` si existe (recap y retoma), o desde `posicion_actual`.

Si hay cambios sin commit de una sesión anterior, ejecuta primero el protocolo /end-sesion sobre ellos.

La teoría del tópico del día no va en el chat: escríbela en `ejercicios/fase-N/<topic_id>/leccion.md` (formato en `ejercicios/_plantilla/leccion.md`) asumiendo cero conocimiento previo — sin saltar pasos, definiendo cada término y explicando cada línea de la demo — y en el chat solo pide leerla y responder las preguntas ahí mismo.

Cuando el ejercicio esté resuelto, pasen ~30 min, o el estudiante deba irse, indícale: "Corre `/end-sesion` para cerrar y guardar el progreso."
