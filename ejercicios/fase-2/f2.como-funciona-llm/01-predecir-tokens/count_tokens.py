"""Scaffold (given by the tutor): prints the real token count of each text.

Run it with:  uv run python count_tokens.py
Do NOT run it before writing your predictions in RESPUESTAS.md (part A).
You may add your own texts to TEXTS at the end of the exercise (part B.3).
"""

import sys

import tiktoken

sys.stdout.reconfigure(encoding="utf-8")

encoding = tiktoken.get_encoding("o200k_base")

# Part A: order these by token count BEFORE running.
TEXTS: list[str] = [
    "Bogotá",
    "internacionalización",
    "internationalization",
    "3.14159265",
    "🙂🙂🙂",
    "The quick brown fox jumps over the lazy dog.",
]

# Part A: predict whether each pair shares the token COUNT and the token IDS.
PAIRS: list[tuple[str, str]] = [
    ("casa", " casa"),
    ("casa", "CASA"),
    ("perro", "perros"),
]


def describe(text: str) -> str:
    """Return one line: the text, its token count and the pieces it was split into."""
    ids = encoding.encode(text)
    pieces = [encoding.decode([token_id]) for token_id in ids]
    return f"{text!r:48} {len(ids):2} tokens  pieces={pieces}"


print("=== part A.1: token counts (sorted from fewest to most) ===")
for text in sorted(TEXTS, key=lambda t: len(encoding.encode(t))):
    print(describe(text))

print()
print("=== part A.2: pairs ===")
for left, right in PAIRS:
    left_ids = encoding.encode(left)
    right_ids = encoding.encode(right)
    left_pieces = [encoding.decode([token_id]) for token_id in left_ids]
    right_pieces = [encoding.decode([token_id]) for token_id in right_ids]
    print(f"{left!r:10} -> ids={left_ids}  pieces={left_pieces}")
    print(f"{right!r:10} -> ids={right_ids}  pieces={right_pieces}")
    print(
        f"   same count: {len(left_ids) == len(right_ids)}   "
        f"same ids: {left_ids == right_ids}"
    )
