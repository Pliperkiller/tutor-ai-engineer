# EXERCISE — complete the TODOs. See enunciado.md.
"""HTTP client that fetches 10 models sequentially and concurrently,
measuring the wall-clock time of each strategy."""

import asyncio
import time

import httpx

BASE_URL = "http://127.0.0.1:8123"
MODEL_IDS = list(range(10))


async def fetch_model(client: httpx.AsyncClient, model_id: int) -> dict:
    """Fetch one model from GET /models/{model_id} and return the parsed JSON."""
    # TODO 1: make the GET request with `client`, raise on HTTP errors
    # (hint: response.raise_for_status()) and return response.json()
    response = await client.get(f"{BASE_URL}/models/{model_id}")
    response.raise_for_status()
    return response.json()


async def fetch_all_sequential() -> list[dict]:
    """Fetch every model in MODEL_IDS one after another (no concurrency)."""
    # TODO 2: open ONE httpx.AsyncClient (async with) and await fetch_model
    # for each id, collecting the results in order.
    iter = []
    async with httpx.AsyncClient() as client:
        for id in MODEL_IDS:
            iter.append(await fetch_model(client=client, model_id=id))

        return iter



async def fetch_all_concurrent() -> list[dict]:
    """Fetch every model in MODEL_IDS concurrently."""
    # TODO 3: open ONE httpx.AsyncClient (async with) and use asyncio.gather
    # so all requests are in flight at the same time. Results in order.
    
    async with httpx.AsyncClient() as client:
        iter = await asyncio.gather(*(fetch_model(client=client,model_id=id) for id in MODEL_IDS))

    return iter


def measure(label: str, coro) -> list[dict]:
    """Run a coroutine, print how long it took, and return its result."""
    start = time.perf_counter()
    result = asyncio.run(coro)
    elapsed = time.perf_counter() - start
    print(f"{label}: {elapsed:.2f}s for {len(result)} requests")
    return result


if __name__ == "__main__":
    sequential = measure("sequential", fetch_all_sequential())
    concurrent = measure("concurrent", fetch_all_concurrent())
    assert sequential == concurrent, "both strategies must return the same data"
    print("results match: OK")
