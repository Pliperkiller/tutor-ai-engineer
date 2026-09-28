"""Three real note-taking functions.

Scaffolding — read it, do not change it. Nothing in this file knows that an LLM
exists: these are plain Python functions with type hints, testable on their own.
"""

from pathlib import Path

NOTES_DIR = Path(__file__).parent / "notes"


def list_notes() -> str:
    """Return the name of every available note, one per line."""
    names = sorted(path.stem for path in NOTES_DIR.glob("*.md"))
    return "\n".join(names) if names else "(no notes)"


def read_note(name: str) -> str:
    """Return the full text of one note.

    Raises FileNotFoundError when no note with that name exists.
    """
    return (NOTES_DIR / f"{name}.md").read_text(encoding="utf-8")


def append_to_note(name: str, text: str) -> str:
    """Append one line to an existing note and report what was done.

    Raises FileNotFoundError when no note with that name exists, so that a typo
    never silently creates a second note.
    """
    path = NOTES_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"No note named {name!r}")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"- {text}\n")
    return f"Appended 1 line to {name}"
