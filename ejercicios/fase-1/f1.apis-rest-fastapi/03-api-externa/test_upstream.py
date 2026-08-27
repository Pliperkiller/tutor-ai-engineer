"""Tests for GET /models/{model_id}/cost — the endpoint that calls the upstream.

Every test here mocks Frankfurter with respx: no network is used.
"""

# P1 (write it BEFORE touching conftest.py):
# If the `client` fixture stays as `return TestClient(app)`, and a test hits
# /models/1/cost?currency=EUR — which line of main.py breaks first, with which
# exception, and does pytest report ERROR or FAILED?
# is going to fail over request.app.state.http_client will report an exception and this will show a FAILED test
# R/ correct on both counts. The missing name: AttributeError
#    ('State' object has no attribute 'http_client'). Nothing is created and nothing is
#    None -- the attribute simply does not exist, because only the lifespan sets it.

# P2 (write it BEFORE test 3):
# The upstream answers 404 because the currency does not exist. Which status does
# YOUR client receive, and why is it not a 404?
# TODO: your answer here.

import httpx
import pytest
import respx

from main import FRANKFURTER_URL

# Payload shaped exactly like a real Frankfurter response.
UPSTREAM_OK = {
    "amount": 1.0,
    "base": "USD",
    "date": "2026-08-13",
    "rates": {"EUR": 0.5},
}


def test_cost_happy_path(client):
    """Upstream answers 200 with a known rate.

    Asserts:
      - status 200
      - the exact `rate` and the exact `cost` in the body (compute them by hand
        from model 1's max_tokens and USD_PER_1K_TOKENS — do not copy them from
        a test run)
      - the route as a spy: the upstream was called exactly once, and the params
        the app really sent were base=USD and symbols=EUR
    """
    # --- GIVEN BY THE TUTOR as the worked demo for respx. Not graded. ---
    with respx.mock:
        route = respx.get(FRANKFURTER_URL).mock(
            return_value=httpx.Response(200, json=UPSTREAM_OK)
        )
        response = client.get("/models/1/cost?currency=EUR")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "claude-fable-5",
        "currency": "EUR",
        "rate": 0.5,
        # 64000 / 1000 * 3.0 = 192.0 USD, times the 0.5 rate.
        "cost": 96.0,
    }

    # The route doubles as a spy: what the app really sent upstream.
    assert route.call_count == 1
    sent = route.calls.last.request.url.params
    assert sent["base"] == "USD"
    assert sent["symbols"] == "EUR"


def test_unknown_model_never_calls_upstream(client):
    """GET /models/999/cost?currency=EUR -> 404, and no network call was made.

    The 404 is decided before touching the network, so the mocked route must
    report that it was never called.
    """
    # TODO


def test_upstream_error_status_becomes_502(client):
    """The upstream answers with an error status -> the API answers 502.

    Parametrize this one over at least three upstream statuses (404, 500, 503).
    """
    # TODO


def test_upstream_timeout_becomes_504(client):
    """The upstream never answers in time -> the API answers 504.

    Use side_effect with an httpx timeout exception, not a Response.
    """
    # TODO


def test_currency_missing_from_rates_becomes_502(client):
    """Upstream answers 200, but the requested currency is not inside `rates`.

    The payload is well formed, just not useful: the API must not trust it and
    must answer 502 instead of blowing up with a KeyError.
    """
    # TODO
