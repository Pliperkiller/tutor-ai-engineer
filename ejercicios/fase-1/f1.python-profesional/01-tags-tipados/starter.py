"""f1.python-profesional · 01 — parse_tags: tipado + errores explícitos.

Completa los TODO. No cambies las firmas ni el nombre de la excepción:
el test los importa tal cual.
"""


class TagError(Exception):
    """Se lanza cuando una entrada de tags está mal formada."""


def parse_tags(raw: str) -> dict[str, str]:
    """Convierte "k1=v1, k2=v2" en {"k1": "v1", "k2": "v2"}.

    Reglas:
    - Pares separados por coma; clave y valor separados por '='.
    - Ignora espacios alrededor de claves y valores.
    - Ignora pares vacíos (p. ej. una coma final sobrante: "a=1,").
    - Si un par NO vacío no contiene '=', lanza TagError.
    """
    # TODO: implementar según el docstring, respetando la anotación de tipo
    #       de la firma (-> dict[str, str]).
    result = {}
    raw_list = raw.split(",")
    for value in raw_list:
        value = value.strip()
        if value == "":
            continue

        if "=" not in value:
            raise TagError
        
        k,v = value.split("=")
        k = k.strip()
        v = v.strip()

        result[k] = v

    return result




