# Material — vault de Obsidian

Esta carpeta es un vault de Obsidian: ábrela con "Open folder as vault"
apuntando a `material/` y usa la vista de grafo para ver los tópicos,
sus relaciones y tu progreso (nodos coloreados por estado; la config
del grafo ya viene en `.obsidian/` y se versiona con el repo).

Contenido:
- `fase-N/<Nombre del tópico>.md` — una nota por tópico, creada como
  semilla al construir el repo y completada por el tutor al cierre de
  cada sesión: apuntes esenciales, errores cometidos y wikilinks en
  "Relacionados". El frontmatter lleva `topic_id`, `estado` y tags
  `estado/...` sincronizados con `state/progress.json`.
- `sesiones/YYYY-MM-DD.md` — una nota por sesión (bitácora), escrita
  por el tutor al cierre con wikilinks a los tópicos tocados. En el
  grafo actúan como hubs que conectan tópicos usados juntos.

También se puede leer todo como markdown plano desde VS Code.
