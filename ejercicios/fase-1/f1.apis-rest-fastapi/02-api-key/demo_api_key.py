"""Minimal API key demo — READ THIS, then adapt the idea to your main.py.

This file is a complete, runnable toy example. It is NOT your exercise:
here the key is hardcoded and compared with `==`; in your exercise the key
comes from an environment variable and is compared with secrets.compare_digest.

Try it (from this folder, it only needs fastapi installed):
    uv run --with "fastapi[standard]" fastapi dev demo_api_key.py
Then:
    curl -i http://127.0.0.1:8000/public                      # 200, no key needed
    curl -i -X POST http://127.0.0.1:8000/protected           # 401, no key
    curl -i -X POST http://127.0.0.1:8000/protected -H "X-API-Key: demo-key"   # 200
"""

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import APIKeyHeader

app = FastAPI(title="API key demo")

EXPECTED_KEY = "demo-key"  # in your exercise: read from os.environ instead

# Piece 1: header extractor. Does NOT validate anything — it only pulls the
# value of the X-API-Key header out of the request. Missing header -> None
# (that is what auto_error=False means).
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# Piece 2: the gatekeeper. `= Depends(api_key_header)` tells FastAPI:
# "before calling me, run piece 1 and put its result in `key`".
async def verify_api_key(key: str | None = Depends(api_key_header)) -> None:
    # Piece 3: plain Python. Wrong or missing key -> raise; otherwise just return.
    if key != EXPECTED_KEY:  # in your exercise: None-check + compare_digest
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/public")
async def public() -> dict:
    return {"anyone": "can read this"}


# The gatekeeper is attached in the decorator: if verify_api_key raises,
# this function never runs.
@app.post("/protected", dependencies=[Depends(verify_api_key)])
async def protected() -> dict:
    return {"secret": "only key holders see this"}
