# RESPUESTAS — 01 Predecir tokens y sampling

Rellena las partes A y C ANTES de correr `count_tokens.py`. La parte B, después.

---

## Parte A.1 — Ordena de menos a más tokens (predicción)

Textos (en desorden):

- `Bogotá` 2
- `internacionalización`7
- `internationalization`5
- `3.14159265`4
- `🙂🙂🙂`3
- `The quick brown fox jumps over the lazy dog.`10

Tu orden, con el número de tokens que predices para cada uno:

1. `The quick brown fox jumps over the lazy dog.` → 10 tokens
2. `internacionalización` → 7 tokens
3. `internationalization` → 5 tokens
4. `3.14159265` → 4 tokens
5. `🙂🙂🙂` → 3 tokens
6. `Bogotá` → 2 tokens

## Parte A.2 — Pares (predicción)

| par | ¿mismo número de tokens? | ¿mismos ids? | por qué (una frase, con "pieza de la tabla") |
|---|---|---|---|
| `casa` vs `casa` con espacio delante |si |no |casa sola es una palabra que inicia una feace, casa con espacio delante es una palabra dentro de una oracion |
| `casa` vs `CASA` |no |no |CASA se podria escribir como CA+SA |
| `perro` vs `perros` |no |si |tienen el mismo id para la parte de perro, pero perros tendria un token adicional en perro+s |

---

## Parte B — Resultado real y explicación de cada fallo

Pega aquí la salida de `uv run python count_tokens.py`:

```text
'Bogotá'                                          2 tokens  pieces=['Bog', 'otá']
'internationalization'                            2 tokens  pieces=['international', 'ization']
'internacionalización'                            3 tokens  pieces=['intern', 'acional', 'ización']
'🙂🙂🙂'                                             3 tokens  pieces=['🙂', '🙂', '🙂']
'3.14159265'                                      5 tokens  pieces=['3', '.', '141', '592', '65']
'The quick brown fox jumps over the lazy dog.'   10 tokens  pieces=['The', ' quick', ' brown', ' fox', ' jumps', ' over', ' the', ' lazy', ' dog', '.']
```

Por cada predicción fallada (o, si acertaste todo, las dos menos obvias), una frase con la causa:

- se usa international como un solo token lo cual ahorra muchos resultados yo usé la regla de la leccion (cada 4 caracteres 1 token para palabras en inglés)
- se tokeniza intern acional izacion yo usé la regla de la leccion (cada 3 caracteres 1 token para palabras en español)
- se usa el caracter . para separar tokens de numeros, usualmente se agrupan los tokens de numeros de 3 en 3

=== part A.2: pairs ===
'casa'     -> [66, 5643] 
' casa'    -> [10859]
   same count: False   same ids: False
'casa'     -> [66, 5643]
'CASA'     -> [72693, 32]
   same count: True   same ids: False
'perro'    -> [543, 298]
'perros'   -> [543, 2199]
   same count: True   same ids: False


- `casa` vs `casa` con espacio delante, no cumple mismo numero de tokens (mal), tampoco mismo numero de ids (bien), `casa` casi nunca aparece sin espacios en un corpus y es por eso que usa una version fragmentada c+asa, mientras que ` casa` si lo hace ya que acompaña a una oracion
- `casa` vs `CASA`, mismo numero de tokens (mal), no mismo numero de ids (bien), en un corpus es normal no usar mucho, ni `casa` ni ` CASA` aparecen solas en un corpus, por eso se fragmentan en c+asa y CAS+A respectivamente
- `perro` vs `perros`, mismo numero de tokens (mal), no mismo numero de ids (parcialmente, se acierta en prediccion), perro ni perros estan en la tabla y se arman con per + (ro,ros), por eso el primer id coincide (per) pero el segundo ya no

### B.3 (opcional) — Mis dos textos

| texto | tokens predichos | tokens reales | por qué |
|---|---|---|---|
| | | | |
| | | | |

---

## Parte C — Sampling (predicción; se verifica en `f2.llamadas-api`)

Prompt fijo para las tres: *"Dame un nombre para una app que recuerda regar las plantas. Responde solo con el nombre."* Cada configuración se correría 5 veces seguidas.

| configuración | ¿cuántas respuestas distintas de 5? | ¿coherentes? | por qué (con la tabla de temperaturas) |
|---|---|---|---|
| `temperature = 0` | 1 |si|apunta al nombre mas probable del prompt entregado|
| `temperature = 1` | 5 | si | el prompt dispararía a varios nombres dentro de la tabla de probabilidades, el peor de los casos es que dispare 5 opciones diferentes dentro de la tabla |
| `temperature = 1` con `top_p = 0.1` |5| si | se recortan la cantidad de candidatos de lo que tenemos en el caso 2. Se obtienen casos parecidos y la cantidad de resultados depende que que tan plana sea realmente la curva de probabilidad de los candidatos |

Una frase más: ¿cuál de las tres usarías para extraer el número de factura de 500 PDFs, y por qué?
temperature = 0 ya que se alinearia a tomar un valor fijo dentro del prompt que se le entrega (los pdf). Eso si, los pdf tienen que ser uniformes y con la misma estructura

...
