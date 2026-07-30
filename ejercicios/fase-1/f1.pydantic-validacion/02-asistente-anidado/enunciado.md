# Ejercicio 02 — Asistente anidado

**Tipo**: script (tú escribes los modelos Y tus propios tests)
**Archivos**: `model.py` (tu trabajo), `test_model.py` (lo creas tú desde cero),
`datos.json` (entrada de ejemplo válida — NO lo modifiques)

## Contexto

El asistente ya no es un modelo plano: tiene un motor LLM configurado y una
lista de herramientas. Es la forma real de un config de agente. Meta del
tópico (criterio de dominio): 3+ modelos anidados con validators propios y
tests que cubren casos válidos e inválidos — este ejercicio ES ese criterio.

## P1 — Predicción (escribe ANTES de correr nada)

Si valido `{"nombre": "bot9", "motor": {"temperatura": 3.0}}` contra un
modelo con `motor: Motor` anidado, el `loc` del error será:

> TU RESPUESTA AQUÍ: nos mostraría ("motor", "temperatura")


## Especificación de los 3 modelos

### `Herramienta`
| Campo | Tipo | Regla | Default |
|---|---|---|---|
| `nombre` | `str` | minúsculas y sin espacios (formato identificador) | — |
| `descripcion` | `str` | longitud mínima 10 | — |
| `timeout_s` | `float` | mayor que 0 y hasta 120 inclusive | `30.0` |

### `ModelConfig`
La misma del ejercicio 01 — cópiala de allí, es tuya.

### `AsistenteConfig`
| Campo | Tipo | Regla | Default |
|---|---|---|---|
| `nombre` | `str` | longitud mínima 3 | — |
| `modelo` | `ModelConfig` | (valida solo, por anidación) | — |
| `herramientas` | `list[Herramienta]` | ver regla multi-campo | lista vacía |

**Regla 1 — nombres únicos**: los nombres de las herramientas no pueden
repetirse. Si hay duplicados, `ValueError` que diga cuál está duplicado.
(Vive dentro de un solo campo → un `field_validator` sobre `herramientas`
alcanza.)

**Regla 2 — agente necesita herramientas** (esta SÍ cruza dos campos →
exige `model_validator(mode="after")`): si `nombre` empieza con
`"agente-"`, `herramientas` no puede estar vacía. Un agente sin
herramientas no puede actuar.

⚠️ Recuerda tu patrón: antes de escribir el `if`, di en voz alta la
condición de RECHAZO ("rechazo cuando..."). Dos veces te ha mordido el
guard invertido.

## Tus tests (`test_model.py`) — mínimo 7

Casos válidos (mínimo 2):
1. Cargar `datos.json` completo con `model_validate_json` y verificar 2-3
   valores ya coercionados.
2. **Roundtrip**: construir un `AsistenteConfig`, hacer `model_dump_json()`,
   volver a validar el string, y verificar que el modelo resultante es
   igual (`==`) al original.

Casos inválidos (mínimo 5) — usa `pytest.raises(ValidationError)`:
3. `timeout_s` fuera de rango.
4. Herramientas con nombre duplicado (verifica que el mensaje menciona el
   nombre duplicado).
5. Error DENTRO del modelo anidado (`temperatura` inválida dentro de
   `modelo`) — este test debe verificar el `loc` del error: tu P1 a prueba.
6. `descripcion` demasiado corta.
7. Dos campos malos a la vez → un solo `ValidationError` con 2 errores
   (`exc.value.error_count()` o `len(exc.value.errors())`).
8. Asistente con nombre `"agente-..."` y `herramientas` vacía → rechazado
   (la Regla 2).

Pista de API para el 5: dentro de `pytest.raises(ValidationError) as exc_info`,
`exc_info.value.errors()` devuelve la lista de registros; cada uno tiene
`["loc"]`.

## Cómo correr

```bash
cd ejercicios/fase-1/f1.pydantic-validacion/02-asistente-anidado
python3 -m pytest test_model.py -v
```

Doc: https://docs.pydantic.dev/latest/concepts/validators/#model-validators
y https://docs.pydantic.dev/latest/concepts/serialization/

Avísame cuando tengas los 7+ en verde (o si te atascas).
