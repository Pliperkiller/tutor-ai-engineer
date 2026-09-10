---
description: Sesión 0 — ubicar al estudiante en el roadmap por nivel (nulo/bajo/medio/alto/experto)
---
Ejecuta el protocolo /diagnostico definido en CLAUDE.md.

- Si `diagnostico.estado == "en_curso"`, retoma desde la fase/tópico donde quedó el sondeo según las notas del diagnóstico en `progress.json`.
- Si ya está `"completado"`, pregunta si quiere re-diagnosticar una fase específica antes de tocar nada.
- Nada de autoevaluación genérica ("¿sabes alto/medio/bajo?"): el nivel sale de preguntas puntuales sobre cada tópico (p. ej. "¿qué hace `git merge`?", "¿qué muestra `ls -a`?") y de ejercicios reales en `ejercicios/diagnostico/`. Sé conservador: sin ejercicio verificado nadie pasa de `medio`.

Cierra con `progress.json` poblado (nivel y status por tópico, niveles por fase, nivel global, fortalezas, debilidades, posicion_actual), el frontmatter de las notas de tópico sincronizado, nota de sesión en `material/sesiones/`, commit y push, y una tabla fase → nivel en el chat.
