"""Fetch the current temperature in Medellin from the real Open-Meteo API.

Scaffolding: do not modify.
"""

import httpx

from extract import extract_temperature

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
PARAMS = {"latitude": 6.25, "longitude": -75.56, "current_weather": "true"}


def main() -> None:
    response = httpx.get(OPEN_METEO_URL, params=PARAMS, timeout=5.0)
    response.raise_for_status()
    temperature = extract_temperature(response.json())
    print(f"Current temperature in Medellin: {temperature} C")


if __name__ == "__main__":
    main()
