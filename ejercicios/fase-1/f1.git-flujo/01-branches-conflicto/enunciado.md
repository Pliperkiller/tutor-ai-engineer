# f1.git-flujo · 01 — Branches, merges y tu primer conflicto

- Herramienta: Git (branches, merge, resolución de conflictos)
- Tipo: debug + predecir
- Tiempo objetivo: 10-12 min
- Archivos: `setup.sh` (crea `repo-practica/`), `RESPUESTAS.md` (tus predicciones)

## Por qué esta herramienta
Antes de las branches: carpetas `proyecto_v2_FINAL/` o todos commiteando a la
misma línea de historia, pisándose entre sí. Una branch es una línea de
historia paralela: trabajas sin romper `main` y fusionas cuando está listo.

## Tu tarea
Trabaja SIEMPRE dentro de `repo-practica/` (créalo con `./setup.sh`).
El repo tiene `main` y dos branches que parten del mismo commit:
`ajuste-temperatura` y `cambio-modelo`. Ambas tocaron `config.py`.

1. **Explora**: `git log --oneline --graph --all` y `git branch`.
   Dibuja/describe en `RESPUESTAS.md` (P1) la forma de la historia.
2. **Predice (P2)**: vas a hacer `git merge ajuste-temperatura` estando en
   `main`. `main` no se ha movido desde que la branch nació. ¿Git necesita
   crear un commit de merge? Escribe tu predicción ANTES de ejecutar.
   Luego ejecuta y anota qué pasó.
3. **Predice (P3)**: ahora `git merge cambio-modelo`. Las dos branches
   editaron `TEMPERATURA` desde el mismo punto de partida. ¿Qué crees que
   hará git? Escríbelo, luego ejecuta.
4. **Resuelve el conflicto** editando `config.py` con esta decisión de
   negocio: queremos el **modelo nuevo** (`claude-opus-5`) pero la
   **temperatura determinista** (`0.2`) y `MAX_TOKENS = 2048`.
   Sin marcadores `<<<<<<<` residuales. Cierra con un commit cuyo mensaje
   diga qué decidiste y por qué.
5. **Tu propia branch**: crea `docs-uso`, agrega un `README.md` (qué es el
   repo + cómo usar `config.py`) en **2 commits atómicos** con mensajes
   descriptivos, y fusiónala a `main`.

## Cómo se evalúa
El tutor ejecutará dentro de `repo-practica/`:
- `git log --oneline --graph --all` → historia con los merges visibles
- `cat config.py` → decisión aplicada, sin marcadores de conflicto
- `git branch --merged main` → todas las branches fusionadas
- Lectura de `RESPUESTAS.md` → predicciones escritas ANTES de ejecutar

## Pistas
Pídelas al tutor: son escalonadas y no están escritas aquí a propósito.
