"""Support ticket classifier: load a versioned system prompt, classify one message.

Scaffolding — read it, do not change it. run_eval.py imports both functions.
"""

from pathlib import Path

import anthropic

# Haiku: one-word answers do not need a big model, and the eval makes ~60 calls.
MODEL = "claude-haiku-4-5"

# Default SDK retries stay ON here: retries are not today's topic.
client = anthropic.Anthropic()


def load_prompt(path: str) -> str:
    """Return the full text of a prompt file (the prompt lives in git, not in code)."""
    return Path(path).read_text(encoding="utf-8")


def classify(system_prompt: str, message: str) -> str:
    """Send one message under one system prompt and return the raw text answer.

    The message is ALWAYS wrapped in <message> tags, for every prompt version:
    the only thing that changes between versions is the system prompt, so any
    difference in the results is caused by the prompt (controlled experiment).
    The answer is returned raw — no strip(), no lower(): judging it is the
    evaluator's job, and cleaning it here would hide format errors.
    """
    response = client.messages.create(
        model=MODEL,
        max_tokens=20,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"<message>{message}</message>"},
        ],
    )
    return "".join(block.text for block in response.content if block.type == "text")
