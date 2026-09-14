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
   - Cambios a `CLAUDE.md` no pueden romper los invariantes: protocolo de sesión, progresión de estados, repetición espaciada, cierre con commit+push, gate de `/setup`, las convenciones del vault de Obsidian en `material/`, ni el gate de aprobación de `/upgrade-agent`.
4. Verifica lo tocado: parsea (`yaml.safe_load` / `json.load`) si es yaml o json, y muestra al estudiante un resumen tipo diff de lo que cambió.
5. Registra la personalización en `state/agente.json` → lista `personalizaciones`, añadiendo `{"fecha": "YYYY-MM-DD", "descripcion": "<qué quiso el estudiante, una línea>", "archivos": ["<rutas tocadas>"], "detalle": "<qué cambió exactamente y dónde: sección, regla, valor anterior → nuevo>"}`. El `detalle` importa: `/upgrade-agent` lo usa para volver a aplicar el ajuste sobre la versión nueva del archivo cuando la skill se actualice; un registro vago ("ajusté el CLAUDE.md") se pierde en el siguiente upgrade. Cambios a `roadmap.yaml` no se registran aquí: el roadmap no lo toca ningún upgrade. Fuera de esa lista, `state/agente.json` no se edita.
6. `git add -A && git commit -m "config: <resumen corto>" && git push`. Reporta el resultado del push explícitamente; si falla, dilo y ayuda a resolverlo.
