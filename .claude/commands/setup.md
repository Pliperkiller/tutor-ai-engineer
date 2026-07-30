---
description: Configuración inicial del repo de progreso (correr una sola vez)
---
Configura el repositorio remoto donde vivirá el progreso. Sin esto, `/diagnostico` y `/sesion` no operan.

Protocolo:
1. Si `setup.estado == "completado"` en `state/progress.json` Y `git remote get-url origin` responde: informa que ya está configurado (muestra el remoto) y solo reconfigura si el estudiante lo pide explícitamente.
2. Estado local: si no existe `.git` → `git init -b main && git add -A && git commit -m "init: repo-tutor"`. Si existe pero no hay commits, commitea todo.
3. Pide al estudiante crear MANUALMENTE un repo privado VACÍO (GitHub/GitLab, sin README, sin .gitignore, sin licencia) y pegarte la URL. **Espera la URL — no continúes sin ella y nunca la inventes.**
4. `git remote add origin <url>` (o `git remote set-url origin <url>` si ya existía) y luego `git push -u origin main`.
5. Reporta el resultado del push tal cual salió. Si falla, diagnostica por el mensaje de error y guía el troubleshooting:
   - **Autenticación** (401/403, "could not read Username", "Permission denied (publickey)"): por HTTPS → `gh auth login` o Personal Access Token como contraseña; por SSH → verificar llave con `ssh -T git@github.com`, y si no hay, `ssh-keygen -t ed25519` + registrar la llave pública en la plataforma.
   - **Repo no vacío** ("fetch first", "non-fast-forward"): el repo se creó con README u otro contenido. Si ese contenido no importa, `git push -u origin main --force` SOLO con confirmación explícita del estudiante; si importa, `git pull --rebase origin main` y reintentar.
   - **URL o permisos** ("repository not found"): verificar la URL exacta, que el repo exista y que la cuenta autenticada tenga acceso.
   Tras cada corrección reintenta el push, hasta lograrlo o hasta que el estudiante decida parar.
6. Con push exitoso: escribe en `state/progress.json` → `"setup": {"estado": "completado", "remote": "<url>", "completado_en": "<YYYY-MM-DD>"}`, luego `git add -A && git commit -m "setup: remoto configurado" && git push`.
7. Cierra con: "Configuración lista. Corre `/diagnostico` para ubicarte en el roadmap."
