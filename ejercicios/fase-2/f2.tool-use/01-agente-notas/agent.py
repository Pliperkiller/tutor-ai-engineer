"""A note assistant driven by a hand-written tool-use loop.

You write four things: TOOLS, HANDLERS, run_tool() and chat().
Everything marked GIVEN is scaffolding: leave it exactly as it is.
"""

from tabnanny import verbose
from typing import Any

from note_tools import append_to_note, list_notes, read_note

# GIVEN — Haiku is plenty for this and keeps the exercise under a cent.
MODEL = "claude-haiku-4-5"
MAX_TOKENS = 1024


# --- 1. The declarations the model sees -------------------------------------
# TODO: one entry per tool (list_notes, read_note, append_to_note).
# Each entry needs "name", "description" and "input_schema".
# The tests check that the schema of each tool matches the signature of the
# real function in note_tools.py, and that every description is specific
# enough to tell the model WHEN to reach for that tool.
TOOLS: list[dict[str, Any]] = [
    {
        "name": "list_notes",
        "description": (
            "Get the list of all the notes, one per line. "
            "Call this whenever the user asks for the list of all notes available. "
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "read_note",
        "description": (
            "Get the full text of one asked note. "
            "Call this whenever the user asks for the text of one note. "
            "will return FileNotFoundError when no note with that name exists. "
            "only add the name of the note without the .md, "
            "for example: if you want to read groceries.md, use only the name groceries"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "name of the note you want to read. ",
                }
            },
            "required": ["name"],
        },
    },
    {
        "name": "append_to_note",
        "description": (
            "Appends the provided text to an specific note. "
            "Returns a text notifying what was done to the note. "
            "Raises FileNotFoundError when no note with that name exists,"
            "so that a typo never silently creates a second note. "
            "only add the name of the note without the .md, "
            "for example: if you want to read groceries.md, use only the name groceries"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "name of the note you want append text to.",
                },
                "text": {
                    "type": "string",
                    "description": "text you want to append in the new line of the note. ",
                },
            },
            "required": ["name", "text"],
        },
    },
]


# --- 2. The dispatcher ------------------------------------------------------
# TODO: map each tool name to the real function that implements it.
HANDLERS: dict[str, Any] = {
    "list_notes": list_notes,
    "read_note": read_note,
    "append_to_note": append_to_note,
}


def run_tool(
    name: str, tool_input: dict[str, Any], verbose: bool = True
) -> tuple[str, bool]:
    """Execute one tool call.

    Returns (content, is_error): the text that goes back to the model, and
    whether that text describes a failure instead of a result.
    """
    try:
        if verbose:
            print(f"Calling tool : {name}")
        return HANDLERS[name](**tool_input), False
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}", True


# --- 3. The agentic loop ----------------------------------------------------
def chat(
    user_input: str, *, client: Any, max_turns: int = 5, verbose: bool = False
) -> str:
    """Talk to the model until it stops asking for tools; return its final text.

    `client` is injected (GIVEN) instead of being a module-level global so the
    tests can drive this loop with a fake client and spend zero tokens;
    __main__ passes the real anthropic.Anthropic().

    Must raise RuntimeError if the model is still asking for tools after
    max_turns rounds.
    """
    messages = [{"role": "user", "content": user_input}]
    for _ in range(max_turns):
        response = client.messages.create(
            model=MODEL, max_tokens=MAX_TOKENS, tools=TOOLS, messages=messages
        )
        if response.stop_reason != "tool_use":
            return " ".join(b.text for b in response.content if b.type == "text")
        messages.append({"role": "assistant", "content": response.content})

        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            content, is_error = run_tool(block.name, block.input, verbose)
            print(
                f"  [tool] {block.name}({block.input}) -> {content!r} error={is_error}"
            )
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": content,
                    "is_error": is_error,
                }
            )
        messages.append({"role": "user", "content": results})
    raise RuntimeError(f"tool loop did not finish in {max_turns} turns")


# GIVEN — the live acceptance run.
if __name__ == "__main__":
    import anthropic

    real_client = anthropic.Anthropic()
    questions = [
        "Which notes do I have?",
        "Read my note called 'shopping' and tell me what is in it.",
        "Add 'buy oat milk' to my groceries note, then read it back to me.",
    ]
    for question in questions:
        print(f"\n> {question}")
        print(chat(question, client=real_client, verbose=True))
