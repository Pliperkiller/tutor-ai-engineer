# Ejercicio 01 — De dataclass a Pydantic

**Tipo**: test (tests que fallan y debes hacer pasar)
**Archivos**: `model.py` (tu trabajo), `test_model.py` (NO lo modifiques)

## Contexto

Es el mismo dominio del ejercicio 02 de Python: la configuración de un
asistente LLM. Pero ahora los datos llegan "de afuera" (dicts tipo JSON)
y la validación la declara Pydantic — no la escribes tú en `__post_init__`.

## Especificación de `ModelConfig`

| Campo | Tipo | Regla | Default |
|---|---|---|---|
| `modelo` | `str` | debe empezar con `"claude-"` | — (obligatorio) |
| `temperatura` | `float` | entre 0.0 y 1.0 inclusive | `0.7` |
| `max_tokens` | `int` | mayor que 0 | `1024` |

## Qué necesitas (en este orden de dificultad)

1. `BaseModel` como clase base — los campos se declaran con type hints,
   como en dataclasses.
2. Rangos numéricos: NO escribas ifs — Pydantic los declara con
   `Field(ge=..., le=..., gt=...)`. Busca "Field constraints" en la doc.
3. La regla de `modelo` no es un rango: necesita un `@field_validator`,
   un método de clase que recibe el valor y lo devuelve (o lanza
   `ValueError`). Busca "field_validator" en la doc de Pydantic v2.

Doc oficial: https://docs.pydantic.dev/latest/concepts/fields/ y
https://docs.pydantic.dev/latest/concepts/validators/

## Cómo correr

```bash
cd ejercicios/fase-1/f1.pydantic-validacion/01-config-pydantic
python3 -m pytest test_model.py -v
```

Estado inicial: 6 tests, todos fallan. Meta: 6/6 en verde.
Lee los tests — son la especificación ejecutable. Avísame cuando pasen
(o si te atascas: pistas escalonadas, ya sabes).
