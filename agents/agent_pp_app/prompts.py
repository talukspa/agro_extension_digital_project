from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent / "prompts"


def _read(relpath: str) -> str:
    # Resolve prompt files relative to this module, not the CWD, so imports
    # work regardless of where the process was launched from.
    with open(_PROMPTS_DIR / relpath) as f:
        return f.read()


def agent_pp_instruction():
    return _read("agent_pp/instruction.md")


def agent_pp_bq_instruction():
    return _read("agent_pp_bq/instruction.md")


def agent_pp_bq_description():
    return _read("agent_pp_bq/description.md")


def agent_pp_rag_instruction():
    return _read("agent_pp_rag/instruction.md")


def agent_pp_rag_description():
    return _read("agent_pp_rag/description.md")


def text2sql_instruction():
    # Was erroneously loading agent_aa_app's text2sql prompt; use this
    # package's own copy under agent_pp_app/prompts/text2sql/.
    return _read("text2sql/instruction.md")
