"""Model Registry API — exercise 01 skeleton.

Run with: uv run fastapi dev main.py
Docs at: http://127.0.0.1:8000/docs
"""
# f1.apis-rest-fastapi · 01
# P1 (before opening /docs): Is expected to have an interactive documentation of the endpoints,
#  with examples of how will the body look and a way for you to run your own requests to the api
# this information comes from fast api when creating the app variable and adding the decorators
# asociated with the endpoints
# after running the manual tests it was correct

# P2 (POST with max_tokens = -5): the issue will be a responsability of the field
# validator of pydantic and the status code will be 422, unprocessable Entity
# after running the tests it was correct
# ---------------------------------------
# f1.apis-rest-fastapi · 02
# P1: 401 Unauthorized and FastAPI will be in charge of this
# R/ 500 internal server error, is managed directly by the code due by a type error (none vs str)
#
# P2: the id related with the newest model will be the same as the one we had on the previous model
# if someone has configured an application by calling the models by id, it will be calling the
# newest model silently, instead of returning an exception telling that the model he was using
# doesn't exist anymore
# R/ this prediction was correct

import os
import secrets
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pyexpat import model

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.http_client = httpx.AsyncClient(timeout=2.0)
    yield
    await app.state.http_client.aclose()


app = FastAPI(title="Model Registry", lifespan=lifespan)

# In-memory store: model_id -> model data. Infrastructure, do not modify.
MODELS: dict[int, dict] = {
    1: {"name": "claude-fable-5", "provider": "anthropic", "max_tokens": 64000},
    2: {"name": "gpt-5", "provider": "openai", "max_tokens": 32000},
}
USD_PER_1K_TOKENS = 3.0
FRANKFURTER_URL = "https://api.frankfurter.dev/v1/latest"
EXPECTED_KEY = os.environ["MODEL_REGISTRY_API_KEY"]

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


async def verify_api_key(key: str | None = Depends(api_key_header)) -> None:

    if key is None:
        raise HTTPException(status_code=401, detail="Missing API key")

    elif not secrets.compare_digest(key, EXPECTED_KEY):
        raise HTTPException(status_code=401, detail="Invalid API key")


class ModelIn(BaseModel):
    """Payload to register a new model."""

    name: str
    provider: str
    max_tokens: int = Field(gt=0)


class CostOut(BaseModel):
    id: int
    name: str
    currency: str
    rate: float
    cost: float


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/models")
async def models() -> list[dict]:
    result = []

    for model_id, value in MODELS.items():
        model_dict = {"id": model_id, **value}
        result.append(model_dict)

    return result


@app.get("/models/{model_id}")
async def get_model(model_id: int) -> dict:

    if model_id not in MODELS:
        raise HTTPException(status_code=404, detail="Model not listed in the database")

    return {"id": model_id, **MODELS[model_id]}


@app.post("/models", status_code=201, dependencies=[Depends(verify_api_key)])
async def create_model(model: ModelIn) -> dict:
    new_id = max(MODELS.keys(), default=0) + 1
    MODELS[new_id] = model.model_dump()
    return {"id": new_id, **model.model_dump()}


@app.delete(
    "/models/{model_id}", status_code=204, dependencies=[Depends(verify_api_key)]
)
async def delete_model(model_id: int) -> None:

    if model_id not in MODELS:
        raise HTTPException(status_code=404, detail="Model not listed in the database")

    del MODELS[model_id]


@app.get("/models/{model_id}/cost")
async def get_cost(
    currency: str,
    model_id: int,
    client: httpx.AsyncClient = Depends(get_client),
) -> dict:
    if model_id not in MODELS.keys():
        raise HTTPException(status_code=404, detail="Model not found")
    try:
        response = await client.get(
            f"{FRANKFURTER_URL}",
            params={"base": "USD", "symbols": currency.upper()},
        )
        response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="Upstream timed out") from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502, detail=f"Upstream error: {exc.response.status_code}"
        ) from exc

    payload = response.json()
    if currency.upper() not in payload["rates"].keys():
        raise HTTPException(status_code=502, detail="Currency not found in upstream")

    if "rates" not in payload.keys():
        raise HTTPException(status_code=502, detail="rates not in upstream")

    cost_usd = MODELS[model_id]["max_tokens"] / 1000 * USD_PER_1K_TOKENS
    cost_out = CostOut(
        id=model_id,
        name=MODELS[model_id]["name"],
        currency=currency.upper(),
        rate=payload["rates"][currency.upper()],
        cost=round(cost_usd * payload["rates"][currency.upper()], 2),
    )
    return cost_out.model_dump()
