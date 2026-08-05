"""Model Registry API — exercise 01 skeleton.

Run with: uv run fastapi dev main.py
Docs at: http://127.0.0.1:8000/docs
"""

# P1 (before opening /docs): Is expected to have an interactive documentation of the endpoints,
#  with examples of how will the body look and a way for you to run your own requests to the api
# this information comes from fast api when creating the app variable and adding the decorators
# asociated with the endpoints
# after running the manual tests it was correct

# P2 (POST with max_tokens = -5): the issue will be a responsability of the field 
# validator of pydantic and the status code will be 422, unprocessable Entity
# after running the tests it was correct

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Model Registry")

# In-memory store: model_id -> model data. Infrastructure, do not modify.
MODELS: dict[int, dict] = {
    1: {"name": "claude-fable-5", "provider": "anthropic", "max_tokens": 64000},
    2: {"name": "gpt-5", "provider": "openai", "max_tokens": 32000},
}


class ModelIn(BaseModel):
    """Payload to register a new model."""

    # TODO 4a: declare fields name (str), provider (str) and
    # max_tokens (int, strictly positive — Field constraint).
    name: str
    provider: str
    max_tokens: int = Field(gt=0)


# TODO 1: GET /health -> {"status": "ok"}
@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


# TODO 2: GET /models -> list of all models, each including its id.
@app.get("/models")
async def models() -> list[dict]:
    result = []
    
    for model_id in MODELS.keys():
        model_dict = {"id": model_id, **MODELS[model_id]}
        result.append(model_dict)

    return result


# TODO 3: GET /models/{model_id} -> the model (with id) or 404.
# The path parameter is declared as a typed function argument:
#     @app.get("/models/{model_id}")
#     async def get_model(model_id: int) -> dict: ...
# If the id is not in MODELS, raise HTTPException(status_code=404, detail=...).
@app.get("/models/{model_id}")
async def get_model(model_id: int) -> dict:

    if model_id not in MODELS.keys():
        raise HTTPException(status_code=404, detail="Model not listed in the database")

    return {"id": model_id, **MODELS[model_id]}


# TODO 4: POST /models -> validate body as ModelIn, assign the next free id,
# store it in MODELS and return the created model including its id.
# Declare the response code in the decorator: @app.post("/models", status_code=201)

@app.post("/models",status_code=201)
async def create_model(model: ModelIn) -> dict:
    new_id = max(MODELS.keys()) + 1
    MODELS[new_id] = model.model_dump()
    return {"id": new_id, **model.model_dump()}