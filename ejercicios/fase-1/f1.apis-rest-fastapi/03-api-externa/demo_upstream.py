"""Demo: calling an external API from inside FastAPI, and testing it without network.

Run it:  uv run python demo_upstream.py

Every part prints what happens. No network is used: the upstream is mocked with respx.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
import respx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

UPSTREAM = "https://api.example.com"


# ---------------------------------------------------------------------------
# PART 1 — lifespan: one shared AsyncClient for the whole app
# ---------------------------------------------------------------------------
# Opening an AsyncClient per request would pay a new TCP+TLS handshake every
# time (the connection pool you measured in S9 would be useless). The lifespan
# runs once on startup, once on shutdown, and hangs the client on app.state.


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    print("[lifespan] startup: creating the shared AsyncClient")
    app.state.http_client = httpx.AsyncClient(timeout=2.0)
    yield  # <- the app serves requests here
    print("[lifespan] shutdown: closing the shared AsyncClient")
    await app.state.http_client.aclose()


app = FastAPI(title="Demo upstream", lifespan=lifespan)


# ---------------------------------------------------------------------------
# PART 2 — a dependency that hands the shared client to the endpoints
# ---------------------------------------------------------------------------
# Request is FastAPI's object for the raw incoming request; request.app is the
# FastAPI instance, so request.app.state is the same state the lifespan filled.


def get_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


# ---------------------------------------------------------------------------
# PART 3 — the endpoint: call the upstream and translate ITS failures
# ---------------------------------------------------------------------------
# Rule: an upstream failure is not "my server crashed" (500). It is:
#   - 502 Bad Gateway     -> the upstream answered, but with an error status
#   - 504 Gateway Timeout -> the upstream did not answer in time
# Anything else leaking out would become a 500 and would lie to the client.


@app.get("/quote/{symbol}")
async def quote(
    symbol: str,
    client: httpx.AsyncClient = Depends(get_client),  # noqa: B008 — FastAPI's idiom
) -> dict:
    try:
        response = await client.get(f"{UPSTREAM}/rates", params={"symbol": symbol})
        response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="Upstream timed out") from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502, detail=f"Upstream error: {exc.response.status_code}"
        ) from exc

    payload = response.json()
    return {"symbol": symbol, "price": payload["price"]}


# ---------------------------------------------------------------------------
# PART 4 — testing it: respx mocks the upstream, TestClient drives the app
# ---------------------------------------------------------------------------
# respx patches httpx's real network transport. TestClient talks to the app
# through an in-process ASGI transport, so respx does NOT intercept it: your
# request to your own app goes through, the app's call to the upstream is faked.
#
# `with TestClient(app) as client:` (as a context manager) is what runs the
# lifespan. A bare `TestClient(app)` would skip startup and app.state would be
# empty -> AttributeError.


def demo_happy_path() -> None:
    print("\n--- PART 4: happy path ---")
    with respx.mock:
        route = respx.get(f"{UPSTREAM}/rates").mock(
            return_value=httpx.Response(200, json={"price": 42.5})
        )
        with TestClient(app) as client:
            response = client.get("/quote/EUR")

        print("status:", response.status_code, "body:", response.json())
        print("upstream was called:", route.called, "times:", route.call_count)
        print("params the app really sent:", route.calls.last.request.url.params)


# ---------------------------------------------------------------------------
# PART 5 — the two error paths, one with a status, one with side_effect
# ---------------------------------------------------------------------------


def demo_error_paths() -> None:
    print("\n--- PART 5: upstream 500 -> 502 ---")
    with respx.mock:
        respx.get(f"{UPSTREAM}/rates").mock(return_value=httpx.Response(500))
        with TestClient(app) as client:
            response = client.get("/quote/EUR")
        print("status:", response.status_code, "body:", response.json())

    print("\n--- PART 5: upstream timeout -> 504 ---")
    with respx.mock:
        respx.get(f"{UPSTREAM}/rates").mock(
            side_effect=httpx.ConnectTimeout("too slow")
        )
        with TestClient(app) as client:
            response = client.get("/quote/EUR")
        print("status:", response.status_code, "body:", response.json())


if __name__ == "__main__":
    demo_happy_path()
    demo_error_paths()
