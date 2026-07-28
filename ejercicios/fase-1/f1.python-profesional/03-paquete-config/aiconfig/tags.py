"""Parseo de tags 'k=v' a un dict tipado."""


class TagError(Exception):
    """Se lanza cuando una entrada de tags está mal formada."""


def parse_tags(raw: str) -> dict[str, str]:
    """Convierte "k1=v1, k2=v2" en {"k1": "v1", "k2": "v2"}."""
    result: dict[str, str] = {}
    pares = raw.split(",")
    
    for value in pares:
        value = value.strip()
        if value == "":
            continue
        if "=" not in value:
            raise TagError(f"par sin '=': {value!r}")
        k, v = value.split("=", 1)
        result[k.strip()] = v.strip()
    return result
