---
description: Sesión corta (~15 min) solo de repasos vencidos
---
Sesión de solo repaso, sin tópico nuevo:
1. Apertura estándar (pull + leer estado).
2. Recuperación activa de TODOS los items con `next_review` vencido (prioriza los más antiguos), con preguntas o mini-código.
3. Si no hay vencidos: 2-3 preguntas sobre la entrada más reciente de `debilidades`.
4. Cierre estándar: actualizar estados y `next_review` en `progress.json` Y en el frontmatter de las notas de tópico afectadas (tag `estado/...`), escribir la nota de sesión en `material/sesiones/`, commit y push.
