"""Demo 3 — the manual path: create, check, validate, and ONE retry with feedback.

Offline: a fake client replays two scripted answers, so the retry happens
every time, for free. The first answer is valid JSON with the right shape but
breaks a rule the schema cannot express (a date in the future); the second is fine.

Run:
    uv run --with anthropic --with pydantic python demo_manual_retry.py
"""

import json
from types import SimpleNamespace
from typing import Any

import anthropic
from pydantic import ValidationError

from intake import Intake

OUTPUT_CONFIG = {
    "format": {
        "type": "json_schema",
        "schema": anthropic.transform_schema(Intake.model_json_schema()),
    }
}

GOOD = {
    "client_name": "Laura Gomez",
    "case_type": "personal_injury",
    "incident_date": "2026-03-03",
    "summary": "Rear-ended by a delivery truck at a red light.",
    "urgency": "high",
}
BAD = {**GOOD, "incident_date": "2031-03-03"}


def fake_response(text: str, stop_reason: str = "end_turn") -> SimpleNamespace:
    """Build one fake API response, shaped like the SDK's Message."""
    return SimpleNamespace(stop_reason=stop_reason, content=[SimpleNamespace(type="text", text=text)])


class FakeClient:
    """Replays scripted responses and records a snapshot of each request."""

    def __init__(self, responses: list[SimpleNamespace]) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs: Any) -> SimpleNamespace:
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        return self._responses.pop(0)


client = FakeClient([fake_response(json.dumps(BAD)), fake_response(json.dumps(GOOD))])
messages: list[dict[str, Any]] = [
    {"role": "user", "content": "<message>\nHi, my name is Laura Gomez...\n</message>"}
]


def ask() -> str:
    """One call with the schema attached; returns the raw text or raises."""
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        messages=messages,
        output_config=OUTPUT_CONFIG,
    )
    if response.stop_reason != "end_turn":
        raise RuntimeError(f"no usable answer, stop_reason={response.stop_reason}")
    return response.content[0].text


raw = ask()
try:
    intake = Intake.model_validate_json(raw)
except ValidationError as exc:
    print(f"attempt 1 rejected: {exc.errors()[0]['msg']}")
    messages.append({"role": "assistant", "content": raw})
    messages.append(
        {
            "role": "user",
            "content": f"Your JSON failed validation:\n{exc}\nReturn the corrected JSON.",
        }
    )
    raw = ask()
    intake = Intake.model_validate_json(raw)

print(f"accepted:   {intake!r}")
print(f"API calls:  {len(client.calls)}")
print(f"messages sent in each call: {[len(call['messages']) for call in client.calls]}")
