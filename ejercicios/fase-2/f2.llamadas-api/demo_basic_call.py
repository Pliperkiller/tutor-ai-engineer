"""Demo 1 — one complete call to the Anthropic Messages API.

Run (needs ANTHROPIC_API_KEY set in the environment):
    uv run demo_basic_call.py
"""

import anthropic

# Claude Opus 5 prices per MILLION tokens (June 2026).
# Named once at the top: if the price or model changes, one line changes.
PRICE_INPUT_PER_MTOK = 5.00
PRICE_OUTPUT_PER_MTOK = 25.00

# No arguments: the SDK reads the key from the ANTHROPIC_API_KEY env var.
# The key never appears in code — code goes to git, secrets do not.
client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-5",
    max_tokens=200,
    system="You are a concise assistant. Answer in one sentence.",
    messages=[
        {"role": "user", "content": "Why is the sky blue?"},
    ],
)

# response.content is a LIST of blocks — filter by type, never assume [0] is text.
for block in response.content:
    if block.type == "text":
        print(block.text)

print(f"\nstop_reason: {response.stop_reason}")
print(f"input tokens:  {response.usage.input_tokens}")
print(f"output tokens: {response.usage.output_tokens}")

cost = (
    response.usage.input_tokens / 1_000_000 * PRICE_INPUT_PER_MTOK
    + response.usage.output_tokens / 1_000_000 * PRICE_OUTPUT_PER_MTOK
)
print(f"cost: ${cost:.6f}")
