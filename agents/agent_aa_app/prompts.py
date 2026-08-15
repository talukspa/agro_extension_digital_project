from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent / "prompts"


def _read(relpath: str) -> str:
    # Resolve prompt files relative to this module, not the CWD, so imports
    # work regardless of where the process was launched from.
    with open(_PROMPTS_DIR / relpath) as f:
        return f.read()


def agent_aa_instruction():
    return _read("agent_aa/instruction.md")


def agent_aa_bq_instruction():
    return _read("agent_aa_bq/instruction.md")


def agent_aa_bq_description():
    return _read("agent_aa_bq/description.md")


def agent_aa_rag_instruction():
    return _read("agent_aa_rag/instruction.md")


def agent_aa_rag_description():
    return _read("agent_aa_rag/description.md")


def text2sql_instruction():
    return _read("text2sql/instruction.md")
