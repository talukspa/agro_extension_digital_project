"""Planner gating (default OFF) and RAG citation composition."""
from google.adk.planners import BuiltInPlanner

from core import prompts
from core.agent import _planner, build_app


def _root(app):
    return app._tmpl_attrs["agent"]


def _build():
    return build_app(
        name="aa_agent",
        display_name="Adecuación Agroindustrial",
        main_datastore_env="DATASTORE_AA_ID",
    )


# --- planner gate -----------------------------------------------------------

def test_planner_is_off_by_default(monkeypatch):
    monkeypatch.delenv("AGENT_PLANNER", raising=False)
    assert _planner() is None


def test_planner_stays_off_for_unknown_values(monkeypatch):
    monkeypatch.setenv("AGENT_PLANNER", "on")  # only "builtin" enables it
    assert _planner() is None


def test_planner_enabled_by_env(monkeypatch):
    monkeypatch.setenv("AGENT_PLANNER", "builtin")
    monkeypatch.setenv("AGENT_THINK_BUDGET", "512")
    p = _planner()
    assert isinstance(p, BuiltInPlanner)
    assert p.thinking_config.thinking_budget == 512
    assert p.thinking_config.include_thoughts is True


def test_default_build_attaches_no_planner(monkeypatch):
    monkeypatch.delenv("AGENT_PLANNER", raising=False)
    root = _root(_build())
    bq = next(t.agent for t in root.tools if t.agent.name == "aa_agent_bq")
    rag = next(t.agent for t in root.tools if t.agent.name == "aa_agent_rag")
    assert root.planner is None and bq.planner is None and rag.planner is None


def test_enabled_build_plans_on_root_and_bq_but_not_rag(monkeypatch):
    monkeypatch.setenv("AGENT_PLANNER", "builtin")
    root = _root(_build())
    bq = next(t.agent for t in root.tools if t.agent.name == "aa_agent_bq")
    rag = next(t.agent for t in root.tools if t.agent.name == "aa_agent_rag")
    assert isinstance(root.planner, BuiltInPlanner)
    assert isinstance(bq.planner, BuiltInPlanner)
    # RAG is single-step: thinking budget buys nothing there.
    assert rag.planner is None


# --- citations --------------------------------------------------------------

def test_rag_prompt_carries_the_citation_format():
    for agent in ("agent_aa", "agent_pp"):
        text = prompts.rag_instruction(agent)
        assert "[fuente: <nombre>]" in text
        assert "chileprunes" in text


def test_root_prompt_tells_the_supervisor_to_preserve_markers():
    for agent in ("agent_aa", "agent_pp"):
        assert "[fuente: ...]" in prompts.root_instruction(agent)


def test_root_still_carries_the_plain_text_rule():
    # Citations must not have displaced the whatsapp_plain fragment.
    assert "NO uses" in prompts.root_instruction("agent_aa")


# --- F1: the planner must be switchable on a DEPLOYED engine ----------------

def test_planner_knobs_are_shipped_to_the_engine():
    """Ship-dark-then-A/B is meaningless if AGENT_PLANNER never reaches the
    engine. deploy.py must forward both planner knobs."""
    import deploy
    assert "AGENT_PLANNER" in deploy.OPTIONAL_ENV_KEYS
    assert "AGENT_THINK_BUDGET" in deploy.OPTIONAL_ENV_KEYS


def test_planner_knobs_round_trip_through_env_vars_for(monkeypatch):
    import deploy
    for k in deploy.RUNTIME_ENV_KEYS:
        monkeypatch.setenv(k, "x")
    monkeypatch.setenv("AGENT_PLANNER", "builtin")
    monkeypatch.setenv("AGENT_THINK_BUDGET", "1024")
    env = deploy.env_vars_for("agent_aa")
    assert env["AGENT_PLANNER"] == "builtin"
    assert env["AGENT_THINK_BUDGET"] == "1024"
