"""Anthropic API client: cost tracking + retries with exponential backoff.

Exercise: complete the three TODO functions, in order.
Everything that is already written is scaffolding — read it, do not change it.

Run (needs ANTHROPIC_API_KEY set in the environment):
    uv run python llm_client.py
"""

import random
import time

import anthropic

# Prices in USD per MILLION tokens: (input, output). Checked June 2026.
# Named once at the top, like in demo_basic_call.py: if a price changes,
# one line changes.
PRICES_PER_MTOK: dict[str, tuple[float, float]] = {
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-opus-5": (5.00, 25.00),
}

# Haiku by default: this exercise makes ~20 requests and Haiku is 5x cheaper.
DEFAULT_MODEL = "claude-haiku-4-5"

# Errors worth retrying: the same request MAY succeed if sent again.
# Anything else (401 bad key, 400 malformed request...) is permanent:
# retrying it 5 times produces the same error 5 times, only slower.
TRANSIENT_ERRORS = (
    anthropic.RateLimitError,  # 429: too many requests right now
    anthropic.InternalServerError,  # 500/529: their problem, usually brief
    anthropic.APIConnectionError,  # network died mid-request (timeouts included)
)

# max_retries=0 turns OFF the SDK's built-in retry loop: today WE are the
# retry mechanism, and two stacked retry layers multiply the waits
# (and hide whether ours actually works).
client = anthropic.Anthropic(max_retries=0)


def cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    """Return the cost in USD of one request.

    Contract:
    - look up the model's prices in PRICES_PER_MTOK (remember: the prices
      are per MILLION tokens).
    - an unknown model must raise KeyError on its own — do NOT catch it:
      silently charging $0 for an unknown model is a lie in the books.
    """
    cost_per_m = PRICES_PER_MTOK[model]
    cost_in = input_tokens * cost_per_m[0] / 1_000_000
    cost_out = output_tokens * cost_per_m[1] / 1_000_000
    return cost_in + cost_out


def ask(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 100,
    temperature: float | None = None,
    top_p: float | None = None,
) -> tuple[str, float]:
    """One non-streaming call. Returns (text, cost_in_usd).

    Contract:
    - system prompt: "Answer with the bare minimum. No explanations."
    - the response text is the concatenation of the TEXT blocks only —
      demo_basic_call.py shows why you never assume content[0] is text.
    - compute the cost with cost_usd() and response.usage.
    - RETURN (text, cost). This function must not print: sampling_check.py
      needs the string back to compare answers across runs.
    - sampling: `temperature` and `top_p` are NOT parameters of
      messages.create() in this SDK version — they were removed from the
      Messages API surface. Pass whichever is not None through the
      `extra_body` escape hatch instead:
          extra_body={"temperature": 0.0}
      Send at most one of the two, never both. Build that dict with a
      couple of ifs before the call and pass it once.
    """
    sampling = (
        {"temperature": temperature}
        if temperature is not None
        else {"top_p": top_p}
        if top_p is not None
        else None
    )

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system="Answer with the bare minimum. No explanations.",
        messages=[
            {"role": "user", "content": prompt},
        ],
        extra_body=sampling,
    )

    out_text = " ".join(
        block.text for block in response.content if block.type == "text"
    )

    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens

    cost = cost_usd(model=model, input_tokens=input_tokens, output_tokens=output_tokens)
    return (out_text, cost)


def ask_with_retries(
    prompt: str,
    *,
    max_retries: int = 5,
    **ask_kwargs: object,
) -> tuple[str, float]:
    """Call ask(); on a TRANSIENT error, wait and try again.

    Contract:
    - attempt 0 runs immediately, no wait.
    - after a transient failure on attempt N, sleep
      2**N + random.uniform(0, 1) seconds (1, 2, 4, 8, 16... plus jitter),
      then try again.
    - an error NOT in TRANSIENT_ERRORS must escape immediately, untouched.
    - if the last allowed attempt also fails, re-raise the last error:
      this function never swallows failures (your S9 rule: else -> raise).
    - before each sleep, print one line with: attempt number, error class
      name (type(exc).__name__) and the wait in seconds — an invisible
      retry is undebuggable.
    """

    retry_no = 0
    sleep_time = 0
    while retry_no < max_retries:
        try:
            out, cost = ask(prompt, **ask_kwargs)
            return (out, cost)
        except TRANSIENT_ERRORS as exc:
            if retry_no == max_retries - 1:
                raise
            sleep_time = 2**retry_no + random.uniform(0, 1)
            print(
                f"Attemp no: {retry_no}",
                f"Error type : {type(exc).__name__}",
                f"Wait time: {sleep_time}",
                sep="\n",
            )
            time.sleep(sleep_time)
            retry_no += 1


if __name__ == "__main__":
    answer, cost = ask_with_retries("Name the two moons of Mars.")
    print(answer)
    print(f"cost: ${cost:.6f}")
