'''
P1: it will take at least 1 sec (timeout) + overhead if we have a delayed model, else the least value will be 0.3 sec
P2: HTTPStatusError for id 3 and TimeoutException for id 7
'''

import asyncio
import time

import httpx
from httpx import HTTPStatusError,TimeoutException

BASE_URL = "http://127.0.0.1:8124"
MODEL_IDS = list(range(10))


async def fetch_model(client: httpx.AsyncClient, model_id: int) -> dict:
    """Fetch one model from GET /models/{model_id} and return the parsed JSON."""
    response = await client.get(f"{BASE_URL}/models/{model_id}")
    response.raise_for_status()
    return response.json()

async def fetch_all_robust() -> list:
    async with httpx.AsyncClient(timeout=1.0) as client:
        response = await asyncio.gather(*(fetch_model(client=client,model_id=model_id) for model_id in MODEL_IDS),
                                    return_exceptions=True)
    return response





def summary(coro) -> list[dict]:
    """Run a coroutine, print how long it took, and return its result."""
    start = time.perf_counter()
    result = asyncio.run(coro)
    elapsed = time.perf_counter() - start
    result_ok= 0
    ok_models = []
    error_models = []
    timeout_models = []

    for model in MODEL_IDS:
        item = result[model]
        if isinstance(item, HTTPStatusError):
            error_models.append(model)

        elif isinstance(item, TimeoutException):
            timeout_models.append(model)

        elif isinstance(item, dict):
            result_ok+=1
            ok_models.append(model)

        else:
            raise item

    print(f"ok: {result_ok} models -> {ok_models}")
    print(f"http_errors: {error_models}")
    print(f"timeouts: {timeout_models}")
    print(f"total time: ~{elapsed}s")
    return result


if __name__ == '__main__':
    summary(fetch_all_robust())