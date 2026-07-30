---
description: Ajustar la configuración del tutor (commands, roadmap, reglas) y publicar el cambio al remoto
---
Argumentos: $ARGUMENTS — el ajuste que el estudiante quiere. Si viene vacío, pregunta qué desea ajustar y lista lo soportado.

Ajustes soportados: crear o modificar slash commands (`.claude/commands/`), agregar fases o tópicos a `roadmap/roadmap.yaml`, ajustar reglas de `CLAUDE.md`, o retocar plantillas (`ejercicios/_plantilla/`).

Protocolo:
1. `git pull --ff-only` antes de tocar nada.
2. Reformula el cambio en 2-3 líneas: qué se va a hacer y qué archivos toca. Confirma con el estudiante ANTES de editar.
3. Aplica el cambio respetando estos guardarraíles:
   - Desde aquí NUNCA se edita `state/progress.json` (salvo que un cambio de roadmap agregue campos nuevos que el propio schema exija), ni las soluciones del estudiante en `ejercicios/`.
   - En `roadmap.yaml`: no cambies ids existentes (el progreso los referencia); lo nuevo sigue el schema del archivo (ids `f<n>.<slug>` únicos, `tipo` válido, `criterio_dominio` verificable, `horas` y actualizar `meta.horas_totales_estimadas`).
   - Commands nuevos siguen el formato de los existentes: frontmatter con `description` + instrucciones que referencian los protocolos de `CLAUDE.md` cuando aplique.
   - Cambios a `CLAUDE.md` no pueden romper los invariantes: protocolo de sesión, progresión de estados, repetición espaciada, cierre con commit+push, gate de `/setup`.
4. Verifica lo tocado: parsea (`yaml.safe_load` / `json.load`) si es yaml o json, y muestra al estudiante un resumen tipo diff de lo que cambió.
5. `git add -A && git commit -m "config: <resumen corto>" && git push`. Reporta el resultado del push explícitamente; si falla, dilo y ayuda a resolverlo.
