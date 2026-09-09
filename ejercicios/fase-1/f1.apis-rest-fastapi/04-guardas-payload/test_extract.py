"""Tests for extract_temperature. Scaffolding: do not modify."""

import pytest

from extract import UpstreamFormatError, extract_temperature

FULL_PAYLOAD = {
    "latitude": 6.22,
    "longitude": -75.55,
    "current_weather_units": {"temperature": "°C", "windspeed": "km/h"},
    "current_weather": {
        "time": "2026-09-09T20:45",
        "temperature": 27.9,
        "windspeed": 12.6,
        "winddirection": 92,
    },
}


def test_happy_path_returns_temperature() -> None:
    assert extract_temperature(FULL_PAYLOAD) == 27.9


def test_missing_current_weather_raises() -> None:
    payload = {
        "latitude": 6.22,
        "current_weather_units": {"temperature": "°C"},
    }
    with pytest.raises(UpstreamFormatError) as exc_info:
        extract_temperature(payload)
    assert "current_weather" in str(exc_info.value)


def test_missing_temperature_inside_current_weather_raises() -> None:
    payload = {
        "current_weather": {"windspeed": 12.6, "winddirection": 92},
    }
    with pytest.raises(UpstreamFormatError) as exc_info:
        extract_temperature(payload)
    assert "temperature" in str(exc_info.value)


def test_temperature_at_wrong_level_still_raises() -> None:
    # "temperature" exists at the TOP level, but not where the code reads it.
    payload = {
        "temperature": 99.9,
        "current_weather": {"windspeed": 12.6},
    }
    with pytest.raises(UpstreamFormatError):
        extract_temperature(payload)


def test_empty_payload_raises() -> None:
    with pytest.raises(UpstreamFormatError):
        extract_temperature({})
