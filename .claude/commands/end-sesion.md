---
description: Cerrar la sesión en curso ahora mismo — ceremonia de cierre completa (estado, notas, commit, push)
---
El estudiante indica que la sesión termina en este momento. Ejecuta el protocolo /end-sesion definido en CLAUDE.md, completo y en orden, sin importar en qué punto quedó la sesión (ejercicio terminado, a medias o sin empezar):

1. Evalúa lo hecho (ejercicio, repasos, preguntas de la lección).
2. Actualiza `state/progress.json`: status y `next_review` de los tópicos tocados, `debilidades`, `posicion_actual`, `sesiones_completadas`, `ultima_sesion`, y `pendiente` (objeto con `topic_id`, `ejercicio`, `paso`, `siguiente` si quedó trabajo a medias; `null` si no).
3. Sincroniza las notas de tópico en `material/fase-N/` (apuntes, errores, frontmatter, links según la regla).
4. Escribe la nota de sesión `material/sesiones/YYYY-MM-DD.md`.
5. `git add -A && git commit -m "sesion <N>: <topic_id> — <resultado>" && git push`. Si el push falla, dilo y no des la sesión por cerrada.
6. Confirma en ≤4 líneas qué cambió y qué quedó pendiente, y cierra con "Retoma con `/start-sesion`".

Reglas: `aprendido` solo con ejercicio verificado; nunca `dominado` en la sesión en que se enseñó el tópico. Si no hay sesión abierta ni cambios por guardar, dilo y no toques archivos.
