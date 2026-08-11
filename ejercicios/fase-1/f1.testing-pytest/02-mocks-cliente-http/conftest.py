from collections.abc import AsyncIterator

import httpx
import pytest


@pytest.fixture()
async def client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(timeout=1.0) as http_client:
        yield http_client
    