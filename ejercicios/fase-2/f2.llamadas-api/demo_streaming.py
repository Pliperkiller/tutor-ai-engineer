"""Demo 2 — the same call, streamed token by token.

Run (needs ANTHROPIC_API_KEY set in the environment):
    uv run demo_streaming.py
"""

import anthropic

client = anthropic.Anthropic()

# Context manager: there is an open connection that must be closed
# no matter what — same reason as `async with httpx.AsyncClient()`.
with client.messages.stream(
    model="claude-opus-5",
    max_tokens=500,
    messages=[
        {"role": "user", "content": "Write a 4-line poem about the ocean."},
    ],
) as stream:
    # Each iteration yields the next chunk of text AS the model generates it.
    # end="" because chunks are word fragments, not lines.
    # flush=True forces each chunk onto the screen immediately —
    # without it Python buffers the output and the streaming effect disappears.
    for text in stream.text_stream:
        print(text, end="", flush=True)
    # usage can only exist at the END: while the model generates,
    # nobody knows yet how many tokens will come out.
    final_message = stream.get_final_message()

print(f"\n\noutput tokens: {final_message.usage.output_tokens}")
