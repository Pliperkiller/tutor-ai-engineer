"""Demo 2 — structured outputs: the API constrains the answer to a schema.

Needs ANTHROPIC_API_KEY. One call to Haiku 4.5, well under one cent.

Run:
    uv run --with anthropic --with pydantic --env-file .env python demo_structured_parse.py
"""

import json
from datetime import date

import anthropic

from intake import Intake

MESSAGE = (
    "Hi, my name is Laura Gomez. On March 3rd a delivery truck rear-ended my car "
    "at a red light and my neck has hurt ever since. The trucking company's insurer "
    "keeps calling me for a recorded statement. Should I give it?"
)

# What travels to the API: Pydantic writes the JSON Schema, the SDK adapts it.
schema = anthropic.transform_schema(Intake.model_json_schema())
print("summary, as the API sees it:")
print(json.dumps(schema["properties"]["summary"], indent=2))

client = anthropic.Anthropic()

# parse() = create() + schema from the class + validation of the answer.
# If the answer breaks the contract it raises pydantic.ValidationError.
response = client.messages.parse(
    model="claude-haiku-4-5",
    max_tokens=1024,
    system=f"You extract intake data for a law firm. Today is {date.today().isoformat()}.",
    messages=[{"role": "user", "content": f"<message>\n{MESSAGE}\n</message>"}],
    output_format=Intake,
)

intake = response.parsed_output
print(f"\nraw text:   {response.content[0].text}")
print(f"parsed:     {intake!r}")
print(f"date type:  {type(intake.incident_date).__name__}")
print(f"stop_reason={response.stop_reason}  in={response.usage.input_tokens}  out={response.usage.output_tokens}")
