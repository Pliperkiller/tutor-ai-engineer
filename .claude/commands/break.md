---
description: Pausar la sesión en curso guardando todo el contexto para retomarla después
---
Para cuando una sesión iniciada no puede terminar. Protocolo:

1. Escribe `state/sesion_en_curso.md` con exactamente este contenido:
   - Fecha y hora de la pausa.
   - Tópico del día (`topic_id`) y en qué punto del protocolo quedó la sesión (repasos / concepto / ejercicio / cierre).
   - Qué se alcanzó a cubrir (conceptos vistos, preguntas ya respondidas).
   - Ejercicio en curso: ruta exacta y en qué paso del enunciado quedó el estudiante (qué compila/pasa y qué no).
   - Repasos del día: cuáles se hicieron y su resultado, cuáles quedaron pendientes.
   - **Siguiente paso concreto** al retomar (una línea accionable).
2. En `state/progress.json` NO cambies el status del tópico ni incrementes `sesiones_completadas` — eso ocurre solo en cierres completos. Los repasos que sí se completaron antes de la pausa sí actualizan su `next_review`.
3. Escribe o actualiza la bitácora `state/sessions/YYYY-MM-DD.md` marcándola como "(pausada)".
4. `git add -A && git commit -m "break: <topic_id> — sesión pausada" && git push`. Si el push falla, dilo explícitamente.
5. Confirma al estudiante: "Pausa guardada. Retoma cuando quieras con `/sesion`."

Al retomar: la apertura de `/sesion` detecta `state/sesion_en_curso.md`, hace el recap y re-ubica al estudiante donde iba (ver CLAUDE.md). El archivo se borra únicamente cuando esa sesión cierra completa.
