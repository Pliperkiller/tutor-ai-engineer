"""Offline tests for the tool-use loop: no network, no tokens spent.

Scaffolding — read it, do not change it. A fake client replays a scripted list
of responses and records every payload the loop sends, which is how the loop
gets checked without an API key.
"""

import inspect
from types import SimpleNamespace
from typing import Any

import pytest

from agent import HANDLERS, TOOLS, chat, run_tool


# --- the fake client --------------------------------------------------------
def text_block(text: str) -> SimpleNamespace:
    """Build a response block of type 'text', like the SDK returns."""
    return SimpleNamespace(type="text", text=text)


def tool_use_block(block_id: str, name: str, tool_input: dict) -> SimpleNamespace:
    """Build a response block of type 'tool_use', like the SDK returns."""
    return SimpleNamespace(type="tool_use", id=block_id, name=name, input=tool_input)


def response(stop_reason: str, content: list) -> SimpleNamespace:
    """Build one fake API response."""
    return SimpleNamespace(stop_reason=stop_reason, content=content)


class FakeClient:
    """Replays scripted responses and records the kwargs it was called with."""

    def __init__(self, responses: list) -> None:
        self._responses = list(responses)
        self.calls: list[dict[str, Any]] = []
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs: Any) -> SimpleNamespace:
        self.calls.append(kwargs)
        if not self._responses:
            raise AssertionError("the loop called the API more times than scripted")
        return self._responses.pop(0)


# --- the declarations -------------------------------------------------------
def test_every_declared_tool_has_a_handler() -> None:
    declared = {tool["name"] for tool in TOOLS}
    assert declared == set(HANDLERS), "TOOLS and HANDLERS must use the same names"
    assert len(declared) == 3, "this agent exposes three tools"


def test_each_schema_matches_the_real_function_signature() -> None:
    assert TOOLS, "declare your tools first"
    for tool in TOOLS:
        schema = tool["input_schema"]
        params = inspect.signature(HANDLERS[tool["name"]]).parameters
        assert schema["type"] == "object", tool["name"]
        assert set(schema["properties"]) == set(params), tool["name"]
        assert set(schema.get("required", [])) == set(params), tool["name"]


def test_each_description_tells_the_model_when_to_use_the_tool() -> None:
    assert TOOLS, "declare your tools first"
    for tool in TOOLS:
        assert len(tool["description"]) > 60, f"{tool['name']}: say WHEN to call it"
        for name, prop in tool["input_schema"]["properties"].items():
            assert prop.get("description"), f"{tool['name']}.{name} needs a description"


# --- the dispatcher ---------------------------------------------------------
def test_run_tool_returns_the_result_and_no_error_on_success() -> None:
    content, is_error = run_tool("list_notes", {})
    assert is_error is False
    assert "groceries" in content


def test_run_tool_turns_a_failing_tool_into_an_error_result() -> None:
    content, is_error = run_tool("read_note", {"name": "does-not-exist"})
    assert is_error is True
    assert "FileNotFoundError" in content, "the model needs the error type, not just a message"


# --- the loop ---------------------------------------------------------------
def test_chat_returns_the_text_when_the_model_asks_for_no_tools() -> None:
    client = FakeClient([response("end_turn", [text_block("Hello.")])])
    assert chat("hi", client=client) == "Hello."
    assert len(client.calls) == 1


def test_chat_passes_the_declarations_on_every_call() -> None:
    client = FakeClient([response("end_turn", [text_block("ok")])])
    chat("hi", client=client)
    assert client.calls[0]["tools"] == TOOLS


def test_chat_sends_back_the_assistant_turn_and_the_tool_result() -> None:
    first = response("tool_use", [tool_use_block("toolu_1", "list_notes", {})])
    second = response("end_turn", [text_block("You have three notes.")])
    client = FakeClient([first, second])

    assert chat("which notes?", client=client) == "You have three notes."

    sent = client.calls[1]["messages"]
    assert sent[1] == {"role": "assistant", "content": first.content}, (
        "the assistant turn must carry response.content whole, not just its text"
    )
    assert sent[2]["role"] == "user"
    result = sent[2]["content"][0]
    assert result["type"] == "tool_result"
    assert result["tool_use_id"] == "toolu_1"
    assert result["is_error"] is False


def test_chat_answers_parallel_tool_calls_in_a_single_user_message() -> None:
    first = response(
        "tool_use",
        [
            tool_use_block("toolu_1", "read_note", {"name": "groceries"}),
            tool_use_block("toolu_2", "read_note", {"name": "books"}),
        ],
    )
    client = FakeClient([first, response("end_turn", [text_block("done")])])

    chat("read both notes", client=client)

    sent = client.calls[1]["messages"]
    assert len(sent) == 3, "both results belong in ONE user message"
    assert [r["tool_use_id"] for r in sent[2]["content"]] == ["toolu_1", "toolu_2"]


def test_chat_keeps_the_conversation_alive_when_a_tool_fails() -> None:
    first = response("tool_use", [tool_use_block("toolu_1", "read_note", {"name": "shopping"})])
    second = response("tool_use", [tool_use_block("toolu_2", "list_notes", {})])
    third = response("end_turn", [text_block("There is no 'shopping' note.")])
    client = FakeClient([first, second, third])

    assert chat("read shopping", client=client) == "There is no 'shopping' note."

    failed = client.calls[1]["messages"][2]["content"][0]
    assert failed["is_error"] is True
    assert "FileNotFoundError" in failed["content"]


def test_chat_raises_instead_of_looping_forever() -> None:
    scripted = [
        response("tool_use", [tool_use_block(f"toolu_{i}", "list_notes", {})])
        for i in range(3)
    ]
    client = FakeClient(scripted)
    with pytest.raises(RuntimeError) as raised:
        chat("keep going", client=client, max_turns=3)

    # NotImplementedError is a subclass of RuntimeError: an unwritten loop
    # must not be mistaken for a loop that gave up on purpose.
    assert not isinstance(raised.value, NotImplementedError)
    assert len(client.calls) == 3, "the loop should use every allowed turn before raising"
