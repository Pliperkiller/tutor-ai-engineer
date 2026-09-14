"""SCAFFOLDING — written by the tutor, nothing to complete here. Read it.

Verifies the Part C predictions of 01-predecir-tokens against the real API:
runs the same prompt 5 times under each of 3 sampling configs and counts
distinct answers. Needs your finished ask() from llm_client.py.

NOTE (2026-09-13): temperature and top_p were removed from the Messages API
surface in this SDK version — current models expose `output_config.effort`
instead and manage sampling themselves. They still reach older models
(Haiku 4.5) through the `extra_body` escape hatch, which is what ask() uses.
If the API rejects them outright, that rejection IS a result: write it down
in RESULTADOS.md instead of a distinct-answer count.

Run:
    uv run --env-file .env python sampling_check.py
"""

import anthropic

from llm_client import ask

# Same prompt you predicted over in S26 (it is data, so Spanish is fine here).
PROMPT = (
    "Dame un nombre para una app que recuerda regar las plantas. "
    "Responde solo con el nombre."
)

# top_p goes alone in config 3: temperature already defaults to 1 server-side,
# so this is exactly your "T=1 with top_p=0.1" prediction.
CONFIGS: list[tuple[str, dict[str, float]]] = [
    ("temperature=0", {"temperature": 0.0}),
    ("temperature=1", {"temperature": 1.0}),
    ("top_p=0.1 (temperature at its default of 1)", {"top_p": 0.1}),
]

RUNS = 5

total_cost = 0.0
for label, params in CONFIGS:
    answers: list[str] = []
    try:
        for _ in range(RUNS):
            text, cost = ask(PROMPT, max_tokens=30, **params)
            answers.append(text.strip())
            total_cost += cost
    except anthropic.BadRequestError as exc:
        # A 400 here means the model refuses this sampling knob entirely.
        # Not a crash to debug: it is the answer for this row.
        print(f"\n== {label} ==")
        print(f"  REJECTED by the API: {exc}")
        continue
    # Normalized before counting: "PlantPal" and "plantpal" are the same name.
    distinct = len({a.lower() for a in answers})
    print(f"\n== {label} ==")
    for a in answers:
        print(f"  {a!r}")
    print(f"distinct answers: {distinct}/{RUNS}")

print(f"\ntotal cost of this script: ${total_cost:.6f}")
