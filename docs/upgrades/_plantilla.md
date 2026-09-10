# Upgrade del tutor: v<actual> → v<nueva>

- Fecha: YYYY-MM-DD
- Skill usada: `<ruta del .skill o carpeta>` (create-learning-agent v<nueva>)
- Versión actual: v<actual> — <"según state/agente.json" | "SUPUESTA por huellas: <qué huellas>; confirmar antes de aprobar">
- Estado: propuesto

## Qué cambia entre versiones
<Por cada versión intermedia del changelog (de la siguiente a la actual hasta la nueva), 2-5 líneas
en lenguaje del estudiante: qué gana el tutor, qué desaparece y qué tiene que hacer distinto él.>

## Placeholders
| Placeholder | Valor | Origen |
|---|---|---|
| TEMA | <valor> | manifest / inferido de `CLAUDE.md` / propuesto desde el yaml |
| SLUG | <valor> | ... |
| HERRAMIENTAS_EVAL | <valor> | ... |
| EJEMPLO_TEST | <valor> | ... |
| LABS_EJEMPLOS | <valor> | ... |
| REQUISITOS_EXTRA | <valor> | ... |
| STACK_GITIGNORE | <valor, resumido si es largo> | ... |

<Si algún origen es "inferido" o "propuesto", pide confirmación explícita en el resumen del chat.>

## Acciones sobre el motor
| Archivo | Acción | Motivo (versión del changelog) |
|---|---|---|
| `.claude/commands/<x>.md` | crear / reemplazar / eliminar / conservar (propio del estudiante) | <vX: ...> |
| `CLAUDE.md` | reemplazar, re-aplicando <n> personalizaciones | <...> |
| ... | ... | ... |

## Personalizaciones
| # | Qué | Origen | Decisión |
|---|---|---|---|
| 1 | <descripción> | manifest (YYYY-MM-DD) / detectada por diff | re-aplicar en `<archivo>` / conservar / conflicto: <por qué y qué se propone> |

<Toda personalización detectada por diff es una hipótesis: el estudiante confirma o descarta.>

## Migraciones aditivas
- `state/progress.json`: <claves que se añaden y su valor por defecto>; `_reglas` se reemplaza. Valores existentes: sin cambios.
- Frontmatter de notas de tópico: <claves que se añaden, en qué notas>. Cuerpo: sin cambios.
- Estructura: <directorios, semillas de tópico sin nota, plantillas que faltaban>.
- <Cualquier excepción que dicte el changelog (p. ej. contexto de /break → `pendiente`), con su justificación.>

## Lo que NO se toca
`roadmap/`, `docs/roadmap.md`, los valores de `state/progress.json`, `material/fase-*/` (salvo lo aditivo listado arriba),
`material/sesiones/YYYY-MM-DD.md`, `ejercicios/fase-*/`, `ejercicios/diagnostico/`, `labs/<nombre>/`.

## Validación prevista
`python3 <skill>/scripts/validate_repo.py . --diff-base HEAD` — schema completo + comprobación de que la zona del
estudiante no cambió (solo adiciones en `progress.json` y en el frontmatter de las notas).

## Cómo aprobar
Responde `aprobado` en el chat para aplicar, o indica qué cambiar en este plan. Sin aprobación no se modifica nada.

## Resultado
<Lo escribe /upgrade-agent al terminar: fecha, commit, tag, salida de la validación, incidencias y cómo se resolvieron.
Si el upgrade se descarta, este archivo se elimina sin commit.>
