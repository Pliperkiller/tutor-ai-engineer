# Ejercicio 02 — Publicar el repo y fusionar vía Pull Request

**Tipo**: script + predecir
**Repo de trabajo**: `../01-branches-conflicto/repo-practica/` (el de ayer, con tu historia de 6 commits).
**Herramientas**: `git`, `gh` (ya autenticado).

Escribe tus predicciones en `RESPUESTAS.md` **ANTES** de ejecutar cada parte. Eso es lo que reviso.

---

## Parte 0 — Predicción (sin ejecutar nada)

En `RESPUESTAS.md`, responde:

- **P1**: Vas a ejecutar `git push -u origin main` después de crear el repo en GitHub. Tienes 4 branches locales (`main`, `cambio-modelo`, `ajuste-temperatura`, `docs-uso`). ¿Cuáles de esos branches van a existir en GitHub después del push? ¿Por qué?

## Parte 1 — Publicar

Desde `repo-practica/`:

1. Crea el repo en GitHub y conéctalo:
   ```
   gh repo create asistente-config --public --source=. --remote=origin
   ```
2. Sube `main`: `git push -u origin main`
3. Verifica tu predicción P1: `git branch -r` y mira el repo en GitHub (`gh repo view --web` si quieres).

## Parte 2 — Branch + Pull Request

1. Crea un branch `docs-parametros` desde `main`.
2. En él, **2 commits atómicos** (uno por cambio, mensaje que documente el *porqué*):
   - Commit A: en `README.md`, añade una sección `## Parámetros` que explique qué controla `temperature` y por qué está en 0.2.
   - Commit B: en la misma sección, explica qué controla `max_tokens` y por qué 2048.
3. Sube el branch: `git push -u origin docs-parametros`
4. Abre el PR:
   ```
   gh pr create --title "..." --body "..."
   ```
   ⚠️ El *body* del PR no es decorativo: explica **qué cambia y por qué**. Ayer dejaste un mensaje de merge por defecto — hoy no.

## Parte 3 — Predicción + merge vía PR

- **P2** (en `RESPUESTAS.md`, ANTES de mergear): `main` no se ha movido desde que creaste el branch. Ayer aprendiste qué hace git en ese caso (fast-forward). Vas a mergear con `gh pr merge --merge`. Predice: después de hacer `git pull` en `main`, ¿el graph mostrará un fast-forward (línea recta) o un commit de merge (rombo)? Justifica.
- Mergea: `gh pr merge --merge`
- Vuelve a `main`, haz `git pull`, y mira: `git log --oneline --graph --all`
- **P3**: ¿Qué observaste? Si no coincide con tu predicción P2, ¿qué hizo GitHub distinto de lo que haría `git merge` local?

## Entregable

- Repo `asistente-config` público en tu GitHub con el PR fusionado.
- `RESPUESTAS.md` con P1, P2 y P3 respondidas (predicciones escritas antes de ejecutar).

Avísame cuando termines y lo reviso con `gh` y `git log`.
