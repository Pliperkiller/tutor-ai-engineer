# f1.python-profesional · 01 — Tags tipados con errores explícitos

- Herramienta: type hints + excepciones propias (Python 3.12)
- Tipo: completar
- Tiempo objetivo: 10 min
- Archivos: `starter.py`, `test_starter.py`

## Por qué esta herramienta
Antes, en Python, una función recibía "cualquier cosa" y fallaba tarde y feo
(un `KeyError` a 40 líneas de distancia, o peor: un dato basura silencioso).
Los **type hints** documentan y permiten que una herramienta verifique los
tipos ANTES de ejecutar; las **excepciones propias** convierten "algo salió
mal" en un error con nombre que quien te llama puede capturar a propósito.

## Tu tarea
Implementa `parse_tags(raw: str) -> dict[str, str]` en `starter.py` según su
docstring:
- `"modelo=opus, temp=0.7"` → `{"modelo": "opus", "temp": "0.7"}`
- Ignora espacios alrededor de claves y valores.
- Ignora pares vacíos (coma final sobrante).
- Si un par no vacío no tiene `=`, lanza `TagError` (no un error genérico).

No cambies las firmas ni el nombre de la excepción.

## Cómo se evalúa
El tutor ejecuta, desde esta carpeta:
```
pytest test_starter.py -q
```
Los 4 tests deben pasar.

## Pistas
Pídelas al tutor: son escalonadas y no están escritas aquí a propósito.
