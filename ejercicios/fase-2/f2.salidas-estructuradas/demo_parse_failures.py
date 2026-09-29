"""Demo 1 — why "please answer in JSON" is not enough.

Offline: no API key, no network, no tokens. The strings below are the kind of
text a model returns when the ONLY thing asking for JSON is the prompt.

Run:
    uv run --with pydantic python demo_parse_failures.py
"""

import json

from pydantic import ValidationError

from intake import Intake

BASE = {
    "client_name": "Laura Gomez",
    "case_type": "personal_injury",
    "incident_date": "2026-03-03",
    "summary": "Rear-ended by a delivery truck at a red light.",
    "urgency": "high",
}
CLEAN = json.dumps(BASE)

RAW_OUTPUTS = {
    "clean": CLEAN,
    "code fence": f"```json\n{CLEAN}\n```",
    "preamble": f"Here is the extracted data:\n{CLEAN}",
    "truncated": CLEAN[:60],
    "wrong category": json.dumps({**BASE, "case_type": "car accident"}),
    "missing field": json.dumps({k: v for k, v in BASE.items() if k != "urgency"}),
    "future date": json.dumps({**BASE, "incident_date": "2031-01-15"}),
}

for label, raw in RAW_OUTPUTS.items():
    print(f"--- {label}")

    # Layer 1 — syntax: is this text JSON at all?
    try:
        json.loads(raw)
        print("  json.loads -> OK")
    except json.JSONDecodeError as exc:
        print(f"  json.loads -> JSONDecodeError: {exc.msg}")

    # Layer 2 — contract: does it have the fields, types and rules of Intake?
    try:
        intake = Intake.model_validate_json(raw)
        print(f"  Intake     -> OK: {intake.case_type}, {intake.incident_date}")
    except ValidationError as exc:
        first = exc.errors()[0]
        print(f"  Intake     -> ValidationError [{first['type']}] {first['loc']}: {first['msg']}")
