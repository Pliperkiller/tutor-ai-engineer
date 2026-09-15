"""SCAFFOLDING (tutor's, do not modify): force a TRANSIENT error on purpose.

Why this file exists: neither `llm_client.py` with a good key (never fails)
nor with a broken key (fails permanently) ever makes the retry loop run.
To SEE the loop we need an error that IS in TRANSIENT_ERRORS.

How: point the client at a TCP port where nothing is listening. The
connection is refused, the SDK raises anthropic.APIConnectionError — which
is the third entry of TRANSIENT_ERRORS. No request reaches Anthropic, no
API key is needed and nothing is billed.

Run:
    uv run python retry_check.py
"""

import anthropic

import llm_client

# `ask()` uses the module-level name `llm_client.client`. Rebinding that name
# here swaps the client WITHOUT touching llm_client.py: the next call to
# ask() resolves `client` to this one.
llm_client.client = anthropic.Anthropic(
    api_key="not-used-no-request-leaves-this-machine",
    base_url="http://127.0.0.1:9",  # port 9 = discard; nothing listens there
    max_retries=0,  # again: OUR loop is the retry mechanism, not the SDK's
    timeout=2.0,
)

print("--- every attempt below will fail with a transient error ---")
result = llm_client.ask_with_retries("This never reaches the API.", max_retries=3)
print("--- the loop finished without raising ---")
print("RETURNED:", repr(result))
