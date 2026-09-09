"""Extract data from an Open-Meteo payload without trusting its shape."""

from typing import Any


class UpstreamFormatError(Exception):
    """Raised when the upstream payload does not have the expected shape."""


def extract_temperature(payload: dict[str, Any]) -> float:
    """Return the current temperature from an Open-Meteo payload.

    The payload is EXTERNAL data: never trust its shape. Each missing
    piece must raise UpstreamFormatError with a message that names the
    missing key, instead of letting a KeyError escape.
    """
    # TODO(student): guard 1
    # TODO(student): guard 2
    return payload["current_weather"]["temperature"]
