"""Deterministic Markdown -> WhatsApp text normalizer (pure regex, no LLM).

The agent prompt already asks for plain text; this is belt-and-suspenders for
the ~5-10% of replies where Markdown leaks through. Order matters: links before
emphasis (so a URL's punctuation isn't treated as emphasis), emphasis before
whitespace collapse.

NOTE for PR-C: the markdown-link rule only matches the full `[text](url)` form,
so bare `[fuente: ...]` citation markers introduced later are left intact (see
test_does_not_touch_bare_brackets).
"""
import re

_MD_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
_CODE_FENCE_LANG = re.compile(r"```[^\S\n]*[A-Za-z0-9_+-]+[^\S\n]*\n")
_HEADING = re.compile(r"^\s{0,3}#{1,6}\s+", re.MULTILINE)
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC3 = re.compile(r"___([^_]+)___")
_ITALIC2 = re.compile(r"__([^_]+)__")
_BULLET = re.compile(r"^(\s*)\*\s+", re.MULTILINE)
_TABLE_SEP = re.compile(r"^\s*\|?[\s:|-]*-[\s:|-]*\|?\s*$", re.MULTILINE)
_BLANKS = re.compile(r"\n{3,}")


def _detable(text: str) -> str:
    """Flatten markdown tables, leaving ordinary prose alone.

    A markdown table is only a table if it carries a |---|---| separator row.
    Requiring one is what keeps a pipe used as ordinary punctuation intact:
    the old rule also fired on any line containing " | ", which silently
    deleted the pipe from sentences like
    "Usa riego por goteo | el surco no sirve" -> "Usa riego por goteo el surco
    no sirve", quietly changing what the agent said.
    """
    lines = text.split("\n")
    if not any(_TABLE_SEP.match(ln) for ln in lines):
        return text
    out = []
    for line in lines:
        if _TABLE_SEP.match(line):
            continue  # drop the |---|---| separator row entirely
        if line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            out.append(" ".join(c for c in cells if c))
        else:
            out.append(line)
    return "\n".join(out)


def normalize_whatsapp_markdown(text: str) -> str:
    if not text:
        return text
    text = _MD_LINK.sub(r"\2", text)          # [t](url) -> url
    text = _CODE_FENCE_LANG.sub("```\n", text)  # ```sql\n -> ```\n
    text = _HEADING.sub("", text)             # strip leading #'s
    text = _BOLD.sub(r"*\1*", text)           # **b** -> *b*
    text = _ITALIC3.sub(r"_\1_", text)        # ___i___ -> _i_
    text = _ITALIC2.sub(r"_\1_", text)        # __i__ -> _i_
    text = _BULLET.sub(r"\1- ", text)         # "* item" -> "- item"
    text = _detable(text)                     # | a | b | -> a b
    text = _BLANKS.sub("\n\n", text)          # collapse 3+ blank lines
    return text.strip()
