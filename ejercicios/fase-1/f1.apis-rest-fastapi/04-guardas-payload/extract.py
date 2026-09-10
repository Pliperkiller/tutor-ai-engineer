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
    if "current_weather" not in payload:
        raise UpstreamFormatError("Missing upstream value: current_weather")

    if "temperature" not in payload["current_weather"]:
        raise UpstreamFormatError(
            "Missing upstream value: temperature in current_weather"
        )

    return payload["current_weather"]["temperature"]
