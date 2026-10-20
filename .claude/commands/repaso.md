---
description: Sesión corta (~15 min) solo de repasos vencidos
---
Sesión de solo repaso, sin tópico nuevo:
1. Apertura estándar (pull + leer estado).
2. Recuperación activa de **hasta 3** items con `next_review` vencido (4 solo si son cortos), los más antiguos primero, con preguntas o mini-código. Si hay más vencidos, di cuántos quedan en una línea y déjalos para las sesiones siguientes: esperan sin penalización y no se corren a la carrera (ver "Tope de carga" en `CLAUDE.md`). Anota el resultado de cada item como limpia / con reserva / fallada.
3. Si no hay vencidos: 2-3 preguntas sobre la entrada más reciente de `debilidades`.
4. Cierre estándar: actualizar estados y `next_review` en `progress.json` aplicando la escalera 2/7/21/60/150 según el resultado de cada item (limpia avanza un escalón, con reserva mantiene el intervalo, fallada baja a `visto` con +2; superada la de 150, `next_review` = `null` y sale de la rotación) Y en el frontmatter de las notas de tópico afectadas (tag `estado/...`, `repaso_proximo`), escribir la nota de sesión en `material/sesiones/`, commit y push.
