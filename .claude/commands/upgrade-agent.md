---
description: Actualizar el motor del tutor (commands, CLAUDE.md, plantillas, comportamientos) a una versión nueva de la skill create-learning-agent — primero plan, aplicación solo con aprobación explícita
---
Argumentos: $ARGUMENTS — dónde está la skill nueva: ruta a un `.skill` (es un zip), a un `.zip`, a la carpeta ya descomprimida (la que contiene `SKILL.md`) o a una carpeta donde buscarla (p. ej. `~/Downloads`). Si viene vacío, pregunta dónde está y detente.

Este comando tiene DOS fases separadas por una puerta. En la fase 1 no se modifica nada del repo — si el estudiante lo corre en plan mode, mejor: está pensado para eso. La fase 2 empieza únicamente cuando el estudiante aprueba el plan de forma explícita.

## Fase 1 — Analizar y planear (sin escribir en el repo)
1. `git status --porcelain` debe estar vacío. Única excepción: que lo único sin commit sea este mismo archivo (`.claude/commands/upgrade-agent.md`, recién copiado a mano en un repo anterior a 3.0); se commitea junto con el upgrade. Cualquier otro cambio sin commit → di "cierra la sesión con `/end-sesion` antes de actualizar" y detente. Luego `git pull --ff-only`.
2. Localiza la skill a partir de los argumentos. Si la ruta es una carpeta, busca dentro (sin recursión profunda) `*.skill`, `create-learning-agent*.zip` o una subcarpeta con `SKILL.md`; si hay varias candidatas, toma la más reciente y dilo. Si no encuentras nada, NO rastrees el disco: pide una indicación más precisa (ruta completa o nombre exacto del archivo) y detente.
3. Descomprime el `.skill` FUERA del repo (`mktemp -d`) — nunca dentro: nada de la skill se commitea. Verifica en su `SKILL.md` que `name: create-learning-agent`; si es otra skill, dilo y detente.
4. Versiones. Nueva: `metadata.version` del `SKILL.md` de la skill. Actual: `version` de `state/agente.json`. Si el manifest no existe, el repo es anterior a 3.0: identifícala con las huellas de `references/changelog.md` de la skill y déjala como supuesto a confirmar en el plan. Misma versión → "el tutor ya está en v<X>; no hay nada que actualizar", detente. Versión actual mayor que la nueva → no hay downgrade: pide la skill más reciente y detente.
5. Lee `references/upgrade-protocol.md` de la skill NUEVA y síguelo al pie de la letra para construir el plan. La migración la conoce la versión entrante, no este comando: el protocolo define las zonas del repo, cómo recuperar los placeholders, cómo preservar las personalizaciones hechas con `/config`, cómo migrar `state/progress.json` y el frontmatter de las notas sin tocar valores, y el formato del plan. Si este comando y el protocolo se contradicen en un detalle, manda el protocolo; los invariantes de abajo no se negocian.
6. Entrega el plan: escríbelo en `docs/upgrades/YYYY-MM-DD-v<actual>-a-v<nueva>.md` (formato: `docs/upgrades/_plantilla.md`, o `assets/repo/plantilla-plan-upgrade.md` de la skill si el repo aún no la tiene) y en el chat muestra solo un resumen de ≤10 líneas + "Lee el plan en `<ruta>` y responde `aprobado`, o dime qué cambiar". Si el entorno no te deja escribir archivos (plan mode), presenta el plan por el mecanismo de plan y escribe el archivo como primer paso de la fase 2.

Ajusta el plan con el estudiante tantas veces como pida. Sin un `aprobado` explícito no hay fase 2. Si descarta el upgrade, elimina el archivo del plan sin commit y limpia el temporal.

## Fase 2 — Aplicar (solo tras `aprobado`)
Sigue la sección "Aplicación" del protocolo, en este orden: archivos del motor → migraciones aditivas → personalizaciones re-aplicadas → `state/agente.json` (`version`, `actualizado_en`, entrada en `upgrades`) → validación con `python3 <skill>/scripts/validate_repo.py . --diff-base HEAD` → sección "Resultado" del plan (estado `aplicado`) → `git add -A && git commit -m "upgrade: agente v<actual> → v<nueva>"` → `git tag agente-v<nueva>` → `git push && git push --tags`. Si la validación falla, corrige y revalida antes de commitear. Si el push falla, dilo y no des el upgrade por cerrado. Al final borra el directorio temporal.

## Invariantes (valen aunque el protocolo cambie)
- La zona del estudiante no se modifica ni se borra: `roadmap/`, `docs/roadmap.md`, los valores de `state/progress.json`, `material/fase-*/`, `material/sesiones/YYYY-MM-DD.md`, `ejercicios/fase-*/`, `ejercicios/diagnostico/`, `labs/<nombre>/`. En `progress.json` y en el frontmatter de las notas solo se AÑADEN claves que falten; las excepciones las dicta el changelog y aparecen en el plan antes de aprobarse.
- Ningún cambio antes de la aprobación; ningún commit antes de que la validación pase.
- Todo lo hecho queda escrito en el archivo del plan: `docs/upgrades/` es el historial de upgrades del repo.
