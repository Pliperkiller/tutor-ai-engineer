# f1.python-profesional · 03 — Refactor a paquete tipado que pasa ruff

- Herramienta: estructura de paquete (`__init__.py`) + `ruff` (lint)
- Tipo: completar + debug
- Tiempo objetivo: 12 min
- Archivos: `aiconfig/` (paquete), `test_paquete.py`, `pyproject.toml`

## Por qué esto
Es el cierre del tópico "Python profesional": tu código de las sesiones 1 y 2
ya vive en un **paquete** (`aiconfig/`) con módulos separados (`tags.py`,
`config.py`). Falta que el paquete **exporte** su API pública y que pase el
linter sin quejas. Así es como se entrega código profesional.

## Estructura
```
03-paquete-config/
├── pyproject.toml          # config del proyecto + ruff
├── aiconfig/               # el paquete
│   ├── __init__.py         # <- TÚ lo completas (exports)
│   ├── tags.py             # parse_tags + TagError (tiene lint que arreglar)
│   └── config.py           # RunConfig + ConfigError
└── test_paquete.py
```

## Tu tarea
1. **Exporta la API** en `aiconfig/__init__.py` para que
   `from aiconfig import parse_tags, TagError, RunConfig, ConfigError` funcione.
2. **Deja el paquete limpio de lint**: corre ruff, lee cada violación y
   arréglala (hay imports/variables sin usar, y algo en tu propio `__init__.py`).

## Cómo se evalúa
Desde esta carpeta (`03-paquete-config/`), ambas cosas deben estar en verde:
```
python -m ruff check .
python -m pytest test_paquete.py -q
```
`ruff` debe decir "All checks passed!" y los 4 tests deben pasar.

## Pistas
Pídelas al tutor: son escalonadas y no están escritas aquí a propósito.
