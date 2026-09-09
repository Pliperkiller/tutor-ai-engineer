# f1.git-flujo · 03 — Conflicto resuelto vía Pull Request

- Herramienta: git + gh
- Tipo: script + predecir
- Tiempo objetivo: 15 min
- Repo de trabajo: `asistente-config` (tu repo de GitHub), clonado **FUERA** de `tutor-ai-engineer`
- Predicciones: `RESPUESTAS.md` en esta carpeta, escritas **ANTES** de ejecutar cada parte

## Por qué este ejercicio

En un equipo real los conflictos no aparecen en tu terminal: aparecen en el PR, cuando un compañero fusionó primero y tocó la misma línea que tú. Hoy provocas ese escenario tú solo — dos branches que editan la misma línea, la primera se fusiona, la segunda queda bloqueada — y lo destrabas como se hace en la industria: resolviendo en tu branch y actualizando el PR.

## Objetivo

Dos PRs nuevos fusionados en `asistente-config`, el segundo con un conflicto real resuelto por ti. Al terminar, el repo cumple el criterio de dominio completo del tópico: 3+ branches fusionadas vía PR, 10+ commits atómicos, al menos un conflicto resuelto vía PR.

## Paso a paso

0. **Preparación** (estás en máquina nueva; el repo vive en GitHub, no aquí):
   ```powershell
   gh auth status
   cd C:\Users\pipek\OneDrive\Documentos\dev
   gh repo clone Pliperkiller/asistente-config
   cd asistente-config
   ```
   Si `gh auth status` falla, primero `gh auth login`.
   Antes de crear nada: asegúrate de **en qué branch estás parado** y de que `main` está al día con el remoto. Los comandos de verificación los conoces — no van escritos aquí a propósito.

1. **Branch A**: crea una branch `clarify-temperature-docs` y muévete a ella. En `README.md`, **reescribe** la línea de la sección `## Parámetros` que explica `temperature` (mismo contenido, mejor redactado: qué controla y por qué está en 0.2). Un commit atómico, mensaje en inglés que documente el *porqué*. Push del branch y abre el PR con `gh pr create` (título y body en inglés, el body explica qué cambia y por qué). **NO lo fusiones todavía.**

2. **Branch B — desde `main`, NO desde la branch A**: vuelve a `main`, crea `document-temperature-range` y muévete a ella. En `README.md` toca **la misma línea** de `temperature`, con un cambio distinto: añade a la explicación el rango válido del parámetro (0 a 1). Un commit, push, PR. **Tampoco lo fusiones.**

3. **P1 en `RESPUESTAS.md`, antes de fusionar nada**: cuando fusiones el PR A, ¿qué va a mostrar GitHub en la página del PR B y por qué? ¿El botón de merge del PR B va a estar disponible?

4. Fusiona el PR A:
   ```powershell
   gh pr merge <numero-A> --merge
   ```
   Abre el PR B (`gh pr view <numero-B> --web`) y compara con tu P1.

5. **P2 en `RESPUESTAS.md`, antes de resolver**: ¿en qué archivo y entre qué marcadores vas a ver el conflicto? ¿Qué dos versiones de la línea van a aparecer y de dónde viene cada una?

6. Resuelve el conflicto **en la branch B, localmente**:
   - Muévete a la branch B.
   - Trae el `main` del remoto y fusiónalo en tu branch:
     ```powershell
     git pull origin main
     ```
     (`pull` = `fetch` + `merge`: descarga el `main` remoto y lo fusiona en la branch donde estás parado. Aquí es donde salta el conflicto.)
   - Resuelve mezclando **ambos lados** (la redacción nueva del A + el rango del B), sin marcadores residuales. El commit de merge documenta cómo decidiste. Push.

7. Vuelve a la página del PR B: debe estar fusionable ya. Fusiónalo con `gh pr merge <numero-B> --merge`.

8. **Verifica**: en tu `main` local, actualízalo y corre:
   ```powershell
   git log --oneline --graph
   ```
   **P3 en `RESPUESTAS.md`**: ¿cuántos commits tiene ahora la historia completa? ¿Cuántos merge commits añadió todo este flujo y de dónde salió cada uno?

## Convención de código

Mensajes de commit, títulos y bodies de PR en inglés (estándar del repo).

## Cómo se evalúa

El tutor correrá `gh pr list --repo Pliperkiller/asistente-config --state merged` y `git log --oneline --graph` sobre tu clon: 2 PRs nuevos fusionados, README sin marcadores residuales, 10+ commits en la historia, mensajes que documentan el porqué.

## Pistas

Pídelas al tutor: son escalonadas y no están escritas aquí a propósito.
