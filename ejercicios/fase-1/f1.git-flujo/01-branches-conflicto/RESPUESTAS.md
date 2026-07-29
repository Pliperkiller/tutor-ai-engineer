# Respuestas — 01-branches-conflicto

## P1 — Forma de la historia inicial
```
(describe o dibuja en ASCII cómo se ven main y las dos branches)
* 664e713 (ajuste-temperatura) baja temperatura a 0.2 para respuestas deterministas
| * e35f750 (cambio-modelo) sube a opus con temperatura creativa y mas tokens
|/  
* 3077bc1 (HEAD -> main) config inicial del asistente
```
este comando muestra en codigo ascii los branch que existen en el repo junto con su ultimo commit y el branch desde el cual nacieron. HEAD indica desde que branch estas parado
...

## P2 — Predicción: merge de ajuste-temperatura en main
ANTES de ejecutar — ¿git creará un commit de merge? ¿por qué?

Predicción: si lo creará ya que tiene que agregar los cambios hechos en su propia historia y esta no está presente en el main antes del merge

Qué pasó realmente: como main no tenia commit propio desde el punto donde nació (merge sin divergencia) el branch la historia es la de un commit mas (fast forward) pero no se visualiza como merge

## P3 — Predicción: merge de cambio-modelo
ANTES de ejecutar — ¿qué hará git y por qué?

Predicción: informará que existe un conflicto entre las dos branch debido a que se va a hacer un merge sobre un cambio que el branch que se va a traer no tiene trackeado, y que ademas este mismo ya tiene un cambio sobre esa misma línea

Qué pasó realmente: mostro conflicto y pidio al usuario resolver el conflicto antes de mergear
