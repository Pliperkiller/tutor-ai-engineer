# Respuestas — Ejercicio 02

## P1 — ¿Qué branches existirán en GitHub tras `git push -u origin main`? ¿Por qué?

solo va a existir el main por que es el unico branch que estamos mandando (origin main)

## P2 — ¿Fast-forward o commit de merge tras `gh pr merge --merge`? Justifica.

en principio deberia de hacer un FF ya que no hicimos cambios en main durante los cambios en docs-parametros

## P3 — ¿Qué observaste en el graph? ¿Coincidió con P2?

No, en este caso si se hizo un commit de merge, github crea commits de merge en el momento que se hacen pull requests y combina las historias de esa manera