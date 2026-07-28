---
description: Sesión 0 — ubicar al estudiante dentro del roadmap
---
Ejecuta el protocolo /diagnostico definido en CLAUDE.md.

- Si `diagnostico.estado == "en_curso"`, retoma desde donde quedó según las notas del diagnóstico en `progress.json`.
- Si ya está `"completado"`, pregunta si quiere re-diagnosticar una fase específica antes de tocar nada.
- La verificación siempre incluye ejercicios de código reales en `ejercicios/diagnostico/`. Sé conservador al asignar estados: sin código verificado no hay `dominado`.

Cierra con `progress.json` poblado (status por tópico, fortalezas, debilidades, posicion_actual), bitácora, commit y push.
