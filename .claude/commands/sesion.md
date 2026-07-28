---
description: Sesión de estudio de ~30 minutos siguiendo el roadmap
---
Ejecuta el protocolo /sesion definido en CLAUDE.md, paso a paso: apertura → repasos → concepto → ejercicio → cierre.

Argumentos: $ARGUMENTS
- Si viene un topic_id, úsalo como tema del día SOLO si sus prerequisitos y los tópicos anteriores necesarios están en `aprendido` o mejor; si no, explica por qué y propone el tópico correcto según `posicion_actual`.
- Si viene vacío, continúa desde `posicion_actual`.

Recuerda: el cierre es obligatorio aunque el ejercicio quede a medias — actualizar `state/progress.json`, apuntes, bitácora, commit y push.
