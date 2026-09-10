# Tutor AI Engineer — con Claude Code

Repo-tutor personal: Claude Code actúa como tutor de AI Engineer siguiendo el roadmap de `docs/roadmap.md`, con sesiones de ~30 minutos en las que **siempre se produce trabajo verificable**. Todo el estado vive en el repo, así que puedes continuar desde cualquier PC con acceso a él.

## Requisitos

- Git y un repo privado (GitHub/GitLab)
- Claude Code — funciona en la terminal y en VS Code: https://docs.claude.com/en/docs/claude-code/overview
- Python 3.12+ y Docker Desktop. Desde la Fase 2: una API key de Anthropic u OpenAI (pago por consumo; el tutor la pide cuando toca y te ayuda a acotar el gasto)

## Instalación (una sola vez)

```bash
unzip tutor-ai-engineer.zip && cd tutor-ai-engineer
claude
> /setup
```

`/setup` inicializa git, te pide crear un repo privado vacío (GitHub/GitLab) y pegarle la URL, hace el primer push y te guía con el troubleshooting si algo falla. Hasta que `/setup` no termine bien, el tutor no ejecuta `/diagnostico` ni `/start-sesion`.

## Primera vez

```bash
> /diagnostico
```

El tutor te ubica en el roadmap con preguntas puntuales sobre cada tópico (nada de "¿sabes mucho o poco?") y ejercicios reales, y te asigna un nivel por fase: nulo, bajo, medio, alto o experto. Puede tomar 1-3 sesiones; el avance queda guardado. Al terminar, `state/progress.json` refleja tu punto de partida real.

## Flujo de cada sesión

```bash
git pull      # traes el estado más reciente
claude
> /start-sesion
> ... (30 min de trabajo)
> /end-sesion
```

Al correr `/end-sesion`, el tutor actualiza el estado, escribe apuntes y bitácora, y hace **commit + push** por ti. En otro PC: clonar, `git pull`, `/start-sesion`, y sigues exactamente donde ibas.

## Comandos

| Comando | Qué hace |
|---|---|
| `/setup` | Configuración inicial: conectar el repo de progreso (una sola vez) |
| `/diagnostico` | Sesión 0: ubicarte en el roadmap |
| `/start-sesion` | Abre una sesión de estudio de ~30 min (`/start-sesion <topic_id>` fuerza un tópico); si quedó trabajo a medias, lo retoma con recap |
| `/end-sesion` | Cierra la sesión ahora mismo: estado, apuntes, bitácora, commit y push. Úsalo siempre al terminar, aunque el ejercicio quede a medias |
| `/repaso` | Sesión corta (~15 min) solo de repasos vencidos |
| `/estado` | Resumen de progreso, solo lectura |
| `/fase` | Estado de una fase + fecha tentativa de cierre según tu ritmo |
| `/config` | Ajustar el tutor (commands, roadmap, reglas) y publicar el cambio |
| `/upgrade-agent <ruta>` | Actualizar el motor del tutor a una versión nueva de la skill: primero un plan en `docs/upgrades/`, aplica solo con tu `aprobado` |

## Estructura

```
tutor-ai-engineer/
├── CLAUDE.md              # instrucciones del tutor (se cargan solas)
├── roadmap/roadmap.yaml   # currículo estructurado (44 tópicos, 8 fases)
├── docs/
│   ├── roadmap.md         # versión humana del roadmap, con fuentes
│   └── upgrades/          # historial de actualizaciones del tutor (un plan por upgrade)
├── state/
│   ├── progress.json      # fuente de verdad de tu avance (lo escribe el tutor)
│   └── agente.json        # versión de la skill, placeholders y personalizaciones (motor)
├── material/              # vault de Obsidian: notas por tópico + notas de sesión
│   ├── .obsidian/         # config del vault (grafo coloreado por estado), versionada
│   ├── fase-N/            # una nota por tópico, con wikilinks y frontmatter
│   └── sesiones/          # una nota-bitácora por sesión (hubs del grafo)
├── ejercicios/            # enunciados, esqueletos, tests y tus soluciones
│   └── _plantilla/        # formato estándar de ejercicio
└── labs/                  # infraestructura local para ejercicios (si aplica)
```

## Visualizar en Obsidian

Abre `material/` como vault ("Open folder as vault"). La vista de grafo muestra
los tópicos coloreados por estado (gris = no visto, ámbar = visto, verde-azulado =
aprendido, morado = dominado) y las sesiones en coral conectando lo que se usó
junto — la config ya viene en `material/.obsidian/` y se comparte entre tus PCs
vía git (solo el estado de ventanas queda fuera). Las mismas notas se leen como
markdown plano desde VS Code.

## Actualizar el tutor

La skill `create-learning-agent` evoluciona (nuevos commands, mejores protocolos de sesión, explicación, evaluación). Este repo no se actualiza solo; lo haces con `/upgrade-agent`:

```bash
# 1. Descarga la versión nueva de la skill desde claude.ai (archivo .skill) y déjala donde el tutor la vea, p. ej. ~/Downloads
claude
# 2. (recomendado) entra en plan mode con Shift+Tab: el tutor solo analiza hasta que apruebes
> /upgrade-agent ~/Downloads
# 3. Lee el plan en docs/upgrades/<fecha>-v<actual>-a-v<nueva>.md y responde "aprobado" (o pide cambios)
```

Se actualiza el **motor** (commands, `CLAUDE.md`, plantillas, comportamientos) conservando tus ajustes de `/config`. No se tocan el roadmap, tu progreso, tus notas ni tus ejercicios. Cada upgrade queda como commit + tag `agente-v<versión>`, así que se revierte con `git revert`.

## Reglas del juego (resumen)

- **Aquí se produce**: cada tópico exige trabajo tuyo; el tutor lo ejecuta o revisa — no acepta "ya lo hice".
- La teoría no llega por el chat: cada tópico nuevo trae su `leccion.md` (contenido + preguntas). La lees en tu editor y respondes las preguntas en el chat.
- `dominado` solo se gana en una sesión **posterior**, superando recuperación activa sin ayuda.
- `state/progress.json` lo escribe únicamente el tutor, en `/end-sesion`.
- Si pides la solución completa, el tópico no avanza esa sesión: te espera una variante del ejercicio.
