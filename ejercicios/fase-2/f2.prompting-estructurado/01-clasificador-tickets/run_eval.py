"""Compare system prompt versions against the same test cases.

Exercise: complete TODO(1) and TODO(2). Everything else is scaffolding.

Run (needs a .env file with ANTHROPIC_API_KEY in this folder):
    uv run --env-file .env python run_eval.py                              # all versions
    uv run --env-file .env python run_eval.py prompts/classifier_v1.txt    # just one
"""

import json
import sys
from pathlib import Path

from classifier import classify, load_prompt

# The contract downstream code relies on: the answer is exactly one of these.
CATEGORIES = {"billing", "bug", "account", "other"}

# The model is not deterministic: one run per case proves nothing.
RUNS_PER_CASE = 3

DEFAULT_PROMPT_FILES = ["prompts/classifier_v1.txt", "prompts/classifier_v2.txt"]
CASES_FILE = Path("cases.json")


def is_valid_format(output: str) -> bool:
    """TODO(1): True only if `output` is EXACTLY one of CATEGORIES.

    Contract:
    - exact, character by character: "bug" is valid; "bug\\n", " bug",
      "Bug" and "bug." are NOT.
    - do not clean the output before checking (no strip(), no lower()):
      the code that consumes this answer does `if category == "bug"`,
      and that comparison does not clean anything either.
    """
    return output in CATEGORIES


def evaluate(system_prompt: str, cases: list[dict]) -> dict[str, dict[str, int]]:
    """TODO(2): run every case RUNS_PER_CASE times; count results per family.

    Each case is a dict like {"family": "...", "message": "...", "expected": "..."}.

    Contract:
    - call classify(system_prompt, case["message"]) RUNS_PER_CASE times per case.
    - return one counter dict per family, keyed by the family name:
          {"happy": {"runs": 12, "format_errors": 0, "wrong": 1}, ...}
      - "runs": how many runs of that family were executed.
      - "format_errors": runs whose output fails is_valid_format().
      - "wrong": runs whose output != case["expected"]. A format error is
        also wrong (a malformed answer is never the expected one), so
        wrong >= format_errors always.
    - for every WRONG run, print one line with the family, the message,
      the expected category and the output — the last three with !r, so
      hidden whitespace and newlines are visible.
    - this function does not print the summary: print_summary() does.
    """
    evaluate_summary = {}
    structure = {
        "runs": 0,
        "format_errors": 0,
        "wrong": 0,
    }
    for i in range(RUNS_PER_CASE):
        for case in cases:
            if case["family"] not in evaluate_summary:
                evaluate_summary[case["family"]] = structure.copy()

            output = classify(system_prompt, case["message"])
            evaluate_summary[case["family"]]["runs"] += 1
            if not is_valid_format(output):
                evaluate_summary[case["family"]]["format_errors"] += 1
                evaluate_summary[case["family"]]["wrong"] += 1
                print(
                    f"\n case : {case['family']!r} \n message : {case['message']!r} \n expected : {case['expected']!r} \n output : {output!r}"
                )
            elif output != case["expected"]:
                evaluate_summary[case["family"]]["wrong"] += 1

                print(
                    f"\n case : {case['family']!r} \n message : {case['message']!r} \n expected : {case['expected']!r} \n output : {output!r}"
                )
    return evaluate_summary


def print_summary(results: dict[str, dict[str, int]]) -> None:
    """Print one row per family plus a TOTAL row."""
    print(f"{'family':<12}{'runs':>6}{'format_err':>12}{'wrong':>8}")
    totals = {"runs": 0, "format_errors": 0, "wrong": 0}
    for family, counts in sorted(results.items()):
        print(
            f"{family:<12}{counts['runs']:>6}"
            f"{counts['format_errors']:>12}{counts['wrong']:>8}"
        )
        for key in totals:
            totals[key] += counts[key]
    print(
        f"{'TOTAL':<12}{totals['runs']:>6}"
        f"{totals['format_errors']:>12}{totals['wrong']:>8}"
    )


def main() -> None:
    cases = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    # sys.argv[1:] = the file names typed after the script; none -> run all.
    prompt_files = sys.argv[1:] or DEFAULT_PROMPT_FILES
    for prompt_file in prompt_files:
        print(f"\n=== {prompt_file} ===")
        results = evaluate(load_prompt(prompt_file), cases)
        print_summary(results)


if __name__ == "__main__":
    main()
