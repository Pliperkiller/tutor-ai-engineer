# f1.python-profesional · 02 — RunConfig con dataclass y validación

- Herramienta: `@dataclass` + `__post_init__` (Python 3.12)
- Tipo: completar
- Tiempo objetivo: 10 min
- Archivos: `starter.py`, `test_starter.py`

## Por qué esta herramienta
Antes modelabas la config como un `dict[str, str]`: todo string, sin
autocompletado y con `KeyError` ante cualquier typo. Una **dataclass** te da
un objeto tipado con acceso por atributo, `__init__`/`__repr__`/`__eq__`
generados, y `__post_init__` como el lugar natural para validar al construir.

## Tu tarea
Completa `RunConfig` en `starter.py`:
1. Declara los 4 campos tipados en orden correcto (default al final):
   `modelo: str`, `temperatura: float`, `max_tokens: int = 1024`,
   `stream: bool = False`.
2. En `__post_init__`, valida:
   - `0.0 <= temperatura <= 2.0`, si no → `raise ConfigError(...)`.
   - `max_tokens > 0`, si no → `raise ConfigError(...)`.

No cambies los nombres de la clase, los campos ni la excepción.

## Cómo se evalúa
Desde esta carpeta:
```
pytest test_starter.py -q
```
Los 5 tests deben pasar.

## Pistas
Pídelas al tutor: son escalonadas y no están escritas aquí a propósito.
