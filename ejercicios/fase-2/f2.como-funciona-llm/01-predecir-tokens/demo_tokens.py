"""Minimal demo: how a tokenizer splits text into tokens.

Run it with:  uv run python demo_tokens.py
It uses tiktoken (OpenAI's tokenizer library) because it works offline after
the first download and needs no API key. Claude uses a DIFFERENT tokenizer,
so the exact numbers differ, but the mechanism is the same.
"""

import sys

import tiktoken

# Windows consoles sometimes default to a non-UTF-8 encoding; force UTF-8 so
# accented characters (like the "ó" below) print correctly instead of as "?".
sys.stdout.reconfigure(encoding="utf-8")

# A tokenizer is a fixed table: piece of text <-> integer id.
# "o200k_base" is the vocabulary used by the GPT-4o family (~200k entries).
encoding = tiktoken.get_encoding("o200k_base")


def show(text: str) -> None:
    """Print how `text` is split: how many tokens, their ids and their pieces."""
    ids = encoding.encode(text)  # text -> list of integers
    pieces = [encoding.decode([token_id]) for token_id in ids]  # each id -> its text
    print(f"{text!r:32} {len(ids):2} tokens  pieces={pieces}")


print(f"vocabulary size: {encoding.n_vocab}")
print()

show("hello")
show(" hello")  # same word, leading space
show("Hello")  # same word, capital letter
show("Hello, world!")
show("supercalifragilistic")
show("desoxirribonucleico")
show("2024")
show("1234567890")
show("The cat sat on the mat.")
show("El gato se sentó en la alfombra.")

print()
# Round trip: ids -> text gives back exactly the original string.
ids = encoding.encode("El gato se sentó en la alfombra.")
print("ids     :", ids)
print("decoded :", encoding.decode(ids))
