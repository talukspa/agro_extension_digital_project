"""Tests for the LangGraphAgent ADK<->LangGraph bridge.

Covers the ``_content_to_text`` coercion, the ``_get_messages`` /
``_get_*`` event extractors, and the async ``_run_async_impl`` graph flow
driven by a fake CompiledGraph whose ``aget_state`` / ``ainvoke`` are
AsyncMocks returning canned state.

``agent_aa_app`` and ``agent_pp_app`` ship a byte-identical
``utils/langgraph_agent.py`` (verified with ``diff``). We test the aa copy
thoroughly and add one parity call against the pp copy so coverage counts
both files.
"""
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from google.genai import types
from google.adk.events.event import Event
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from agent_aa_app.utils.langgraph_agent import (
    LangGraphAgent,
    _content_to_text,
    _get_last_human_messages,
)


def _user_event(text: str) -> Event:
    return Event(
        invocation_id="i",
        author="user",
        content=types.Content(role="user", parts=[types.Part.from_text(text=text)]),
    )


def _agent_event(author: str, text: str) -> Event:
    return Event(
        invocation_id="i",
        author=author,
        content=types.Content(role="model", parts=[types.Part.from_text(text=text)]),
    )


def _fake_ctx(events, session_id="sess-1"):
    return SimpleNamespace(
        session=SimpleNamespace(id=session_id, events=events),
        invocation_id="inv-1",
        branch="branch-1",
    )


# --------------------------------------------------------------------------
# _content_to_text
# --------------------------------------------------------------------------
def test_content_to_text_none_returns_empty():
    assert _content_to_text(None) == ""


def test_content_to_text_passthrough_str():
    assert _content_to_text("hola") == "hola"


def test_content_to_text_list_of_blocks_concatenates_text_only():
    content = ["a", {"text": "b"}, {"type": "image", "url": "x"}, {"text": ""}]
    # plain str + dict-with-text kept; non-text / empty-text blocks dropped
    assert _content_to_text(content) == "ab"


def test_content_to_text_dict_falls_through_to_str():
    d = {"foo": "bar"}
    assert _content_to_text(d) == str(d)


# --------------------------------------------------------------------------
# event extractors
# --------------------------------------------------------------------------
def test_get_last_human_messages_takes_trailing_user_block():
    events = [
        _user_event("old"),
        _agent_event("bqagent", "reply"),
        _user_event("new"),
    ]
    msgs = _get_last_human_messages(events)
    assert [m.content for m in msgs] == ["new"]
    assert all(isinstance(m, HumanMessage) for m in msgs)


def test_get_last_human_messages_handles_missing_parts_text():
    # event.content.parts[0].text is None -> coerced to ''
    ev = Event(
        invocation_id="i",
        author="user",
        content=types.Content(role="user", parts=[types.Part()]),
    )
    assert _get_last_human_messages([ev]) == [HumanMessage(content="")]


def test_get_conversation_with_agent_interleaves_roles():
    agent = LangGraphAgent(name="bqagent")
    events = [
        _user_event("q1"),
        _agent_event("bqagent", "a1"),
        _agent_event("someone_else", "ignored-author"),
        _user_event("q2"),
    ]
    msgs = agent._get_conversation_with_agent(events)
    # user + own-author events map to Human/AI; other authors are skipped.
    assert [(type(m).__name__, m.content) for m in msgs] == [
        ("HumanMessage", "q1"),
        ("AIMessage", "a1"),
        ("HumanMessage", "q2"),
    ]


# --------------------------------------------------------------------------
# _run_async_impl
# --------------------------------------------------------------------------
def _fake_graph(final_text="RESULT", state_values=None, checkpointer=object()):
    graph = MagicMock(name="CompiledGraph")
    graph.checkpointer = checkpointer
    graph.aget_state = AsyncMock(
        return_value=SimpleNamespace(values=state_values or {})
    )
    graph.ainvoke = AsyncMock(
        return_value={"messages": [AIMessage(content=final_text)]}
    )
    return graph


async def _drain(agent, ctx):
    return [ev async for ev in agent._run_async_impl(ctx)]


def _agent_with_graph(graph, instruction="SYS"):
    # Assign the graph post-construction: the pydantic field is typed
    # Optional[CompiledStateGraph] and rejects a bare MagicMock at __init__,
    # but runtime assignment (mirroring the graph_factory path) is unvalidated.
    agent = LangGraphAgent(name="bqagent", instruction=instruction)
    agent.graph = graph
    return agent


async def test_run_async_impl_yields_model_event_with_final_text():
    graph = _fake_graph("hello world")
    agent = _agent_with_graph(graph)
    ctx = _fake_ctx([_user_event("hi")])

    out = await _drain(agent, ctx)

    assert len(out) == 1
    ev = out[0]
    assert ev.author == "bqagent"
    assert ev.invocation_id == "inv-1"
    assert ev.branch == "branch-1"
    assert ev.content.role == "model"
    assert ev.content.parts[0].text == "hello world"
    # thread_id must be keyed off the session id for checkpointer continuity.
    graph.aget_state.assert_awaited_once()
    cfg = graph.aget_state.await_args.args[0]
    assert cfg == {"configurable": {"thread_id": "sess-1"}}


async def test_run_async_impl_prepends_system_instruction_when_state_empty():
    graph = _fake_graph(state_values={})  # no prior messages -> inject SystemMessage
    agent = _agent_with_graph(graph)
    ctx = _fake_ctx([_user_event("hi")])

    await _drain(agent, ctx)

    sent = graph.ainvoke.await_args.args[0]["messages"]
    assert isinstance(sent[0], SystemMessage)
    assert sent[0].content == "SYS"
    # checkpointer set -> only the trailing human message follows.
    assert isinstance(sent[1], HumanMessage) and sent[1].content == "hi"


async def test_run_async_impl_skips_instruction_when_graph_has_history():
    graph = _fake_graph(state_values={"messages": [HumanMessage(content="prev")]})
    agent = _agent_with_graph(graph)
    ctx = _fake_ctx([_user_event("hi")])

    await _drain(agent, ctx)

    sent = graph.ainvoke.await_args.args[0]["messages"]
    assert not any(isinstance(m, SystemMessage) for m in sent)


async def test_run_async_impl_uses_full_conversation_without_checkpointer():
    graph = _fake_graph(checkpointer=None)
    agent = _agent_with_graph(graph)
    ctx = _fake_ctx([_user_event("q1"), _agent_event("bqagent", "a1")])

    await _drain(agent, ctx)

    sent = graph.ainvoke.await_args.args[0]["messages"]
    # SystemMessage + Human(q1) + AI(a1): full history path exercised.
    assert [type(m).__name__ for m in sent] == [
        "SystemMessage",
        "HumanMessage",
        "AIMessage",
    ]


async def test_run_async_impl_lazily_builds_graph_from_factory():
    graph = _fake_graph()
    factory = MagicMock(return_value=graph)
    agent = LangGraphAgent(name="bqagent", graph=None, graph_factory=factory)
    ctx = _fake_ctx([_user_event("hi")])

    await _drain(agent, ctx)

    factory.assert_called_once()
    assert agent.graph is graph


async def test_run_async_impl_raises_without_graph_or_factory():
    agent = LangGraphAgent(name="bqagent", graph=None, graph_factory=None)
    ctx = _fake_ctx([_user_event("hi")])
    with pytest.raises(ValueError, match="neither `graph` nor `graph_factory`"):
        await _drain(agent, ctx)


# --------------------------------------------------------------------------
# parity: exercise the byte-identical pp copy so coverage counts it too
# --------------------------------------------------------------------------
def test_pp_langgraph_agent_is_importable_and_equivalent():
    from agent_pp_app.utils.langgraph_agent import (
        LangGraphAgent as PPAgent,
        _content_to_text as pp_coerce,
    )

    assert pp_coerce([{"text": "x"}, "y"]) == "xy"
    assert PPAgent(name="bqagent").graph is None


async def test_pp_run_async_impl_flows_end_to_end():
    """Drive the pp copy's _run_async_impl so coverage counts both files."""
    from agent_pp_app.utils.langgraph_agent import LangGraphAgent as PPAgent

    graph = _fake_graph("pp-result")
    agent = PPAgent(name="bqagent", instruction="SYS")
    agent.graph = graph
    ctx = _fake_ctx([_user_event("hola")])

    out = [ev async for ev in agent._run_async_impl(ctx)]
    assert out[0].content.parts[0].text == "pp-result"
