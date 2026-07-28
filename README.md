# Tutor AI Engineer — con Claude Code

Repo-tutor personal: Claude Code actúa como tutor de AI Engineer siguiendo el roadmap de `docs/roadmap.md`, con sesiones de ~30 minutos en las que **siempre se produce trabajo verificable**. Todo el estado vive en el repo, así que puedes continuar desde cualquier PC con acceso a él.

## Requisitos

- Git y un repo privado (GitHub/GitLab)
- Claude Code — funciona en la terminal y en VS Code: https://docs.claude.com/en/docs/claude-code/overview
- Python 3.12+ y Docker Desktop. Desde la Fase 2: una API key de Anthropic u OpenAI (pago por consumo; el tutor la pide cuando toca y te ayuda a acotar el gasto)

## Instalación (una sola vez)

```bash
unzip tutor-ai-engineer.zip && cd tutor-ai-engineer
git init -b main
git add -A && git commit -m "init: tutor ai-engineer"
git remote add origin <url-de-tu-repo-privado>
git push -u origin main
```

## Primera vez

```bash
claude
> /diagnostico
```

El tutor te ubica en el roadmap: autoevaluación por fases + verificación con ejercicios reales. Puede tomar 1-3 sesiones; el avance queda guardado. Al terminar, `state/progress.json` refleja tu punto de partida real.

## Flujo de cada sesión

```bash
git pull      # traes el estado más reciente
claude
> /sesion
```

Al cierre, el tutor actualiza el estado, escribe apuntes y bitácora, y hace **commit + push** por ti. En otro PC: clonar, `git pull`, `/sesion`, y sigues exactamente donde ibas.

## Comandos

| Comando | Qué hace |
|---|---|
| `/diagnostico` | Sesión 0: ubicarte en el roadmap |
| `/sesion` | Sesión de estudio de ~30 min (`/sesion <topic_id>` fuerza un tópico) |
| `/repaso` | Sesión corta (~15 min) solo de repasos vencidos |
| `/estado` | Resumen de progreso, solo lectura |

## Estructura

```
tutor-ai-engineer/
├── CLAUDE.md              # instrucciones del tutor (se cargan solas)
├── roadmap/roadmap.yaml   # currículo estructurado (44 tópicos, 8 fases)
├── docs/roadmap.md        # versión humana del roadmap, con fuentes
├── state/
│   ├── progress.json      # fuente de verdad de tu avance (lo escribe el tutor)
│   └── sessions/          # bitácora por sesión
├── material/              # apuntes por tópico, generados en sesión
├── ejercicios/            # enunciados, esqueletos, tests y tus soluciones
│   └── _plantilla/        # formato estándar de ejercicio
└── labs/                  # infraestructura local para ejercicios (si aplica)
```

## Reglas del juego (resumen)

- **Aquí se produce**: cada tópico exige trabajo tuyo; el tutor lo ejecuta o revisa — no acepta "ya lo hice".
- `dominado` solo se gana en una sesión **posterior**, superando recuperación activa sin ayuda.
- `state/progress.json` lo escribe únicamente el tutor, al cierre de cada sesión.
- Si pides la solución completa, el tópico no avanza esa sesión: te espera una variante del ejercicio.
