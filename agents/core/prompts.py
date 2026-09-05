"""Plain-Python prompt composition. No Jinja, no template engine.

Prompts are resolved relative to this file so they work both locally (cwd =
agents/) and inside the deployed engine (where `core` is shipped via
extra_packages and cwd differs).
"""
import os

_HERE = os.path.dirname(__file__)
_PROMPTS = os.path.join(_HERE, "prompts")


def _read(*parts: str) -> str:
    with open(os.path.join(_PROMPTS, *parts), encoding="utf-8") as f:
        return f.read()


def _join(*chunks: str) -> str:
    return "\n\n".join(c.strip() for c in chunks if c and c.strip())


def root_instruction(agent: str) -> str:
    """Root supervisor prompt: domain role + shared plain-text rule."""
    return _join(_read(agent, "root.md"), _read("shared", "whatsapp_plain.md"))


def rag_instruction(agent: str) -> str:
    return _read(agent, "rag.md")


def rag_description(agent: str) -> str:
    return _read(agent, "rag_description.md")


def bq_instruction(agent: str) -> str:
    """BQ sub-agent prompt: domain/table specifics + shared 4-tool workflow."""
    return _join(_read(agent, "bq.md"), _read("shared", "bq_workflow.md"))


def bq_description(agent: str) -> str:
    return _read(agent, "bq_description.md")
