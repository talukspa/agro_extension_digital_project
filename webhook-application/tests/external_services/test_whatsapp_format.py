"""Unit tests for the deterministic WhatsApp Markdown sanitizer."""
from whatsapp_webhook.external_services.whatsapp_format import (
    normalize_whatsapp_markdown as norm,
)


def test_bold_double_asterisk_to_single():
    assert norm("Esto es **importante** ya") == "Esto es *importante* ya"


def test_triple_underscore_italics_to_single():
    assert norm("muy ___sutil___ detalle") == "muy _sutil_ detalle"


def test_markdown_link_to_bare_url():
    assert norm("Mira [la guía](https://x.co/g) aquí") == "Mira https://x.co/g aquí"


def test_heading_hashes_stripped():
    assert norm("# Título\nTexto") == "Título\nTexto"
    assert norm("### Sub\nMás") == "Sub\nMás"


def test_code_fence_language_tag_stripped():
    assert norm("```sql\nSELECT 1\n```") == "```\nSELECT 1\n```"


def test_table_pipes_collapsed_to_text():
    assert norm("| a | b |\n| - | - |\n| 1 | 2 |") == "a b\n1 2"


def test_leading_bullet_dash_kept_as_dash():
    # WhatsApp renders "- " bullets fine; leave them, just normalize "* " to "- "
    assert norm("* uno\n* dos") == "- uno\n- dos"


def test_collapses_excess_blank_lines():
    assert norm("a\n\n\n\nb") == "a\n\nb"


def test_does_not_touch_bare_brackets():
    # The [fuente: ...] citations must survive — the link regex must NOT eat them.
    assert norm("dato [fuente: faq]") == "dato [fuente: faq]"


def test_citation_markers_survive_full_normalization():
    """Guards the PR-C citation contract against every rule in the pipeline."""
    raw = (
        "## Resumen\n"
        "El límite es **4 mg/kg** [fuente: estandar]\n"
        "* Ver [la guía](https://x.co/g) [fuente: guias]\n"
        "Doble origen [fuente: faq][fuente: chileprunes]"
    )
    out = norm(raw)
    for marker in ("[fuente: estandar]", "[fuente: guias]",
                   "[fuente: faq]", "[fuente: chileprunes]"):
        assert marker in out, f"{marker} was destroyed by the sanitizer"
    # ...while the surrounding Markdown is still normalized.
    assert "**" not in out
    assert out.startswith("Resumen")
    assert "https://x.co/g" in out and "](" not in out


def test_citation_after_a_markdown_link_is_not_swallowed():
    # The link rule is non-greedy on ] and requires (http...) — a following
    # bracket group must not be pulled into the match.
    assert norm("[guía](https://x.co/g) [fuente: guias]") == (
        "https://x.co/g [fuente: guias]"
    )


def test_plain_text_unchanged():
    assert norm("Hola 👋 ¿en qué ayudo?") == "Hola 👋 ¿en qué ayudo?"


# --- F4: a pipe in ordinary prose is not a table ----------------------------

def test_pipe_in_prose_is_left_alone():
    """Regression: _detable used to fire on any ' | ' and silently delete it,
    quietly rewriting what the agent said."""
    for prose in [
        "Usa riego por goteo | el surco no sirve",
        "La relacion es 3 | 4 en ese caso",
        "Opciones: A | B | C",
    ]:
        assert norm(prose) == prose


def test_real_table_is_still_flattened():
    # Has a |---|---| separator row, so it IS a table.
    assert norm("| a | b |\n| - | - |\n| 1 | 2 |") == "a b\n1 2"


def test_table_without_separator_row_is_not_mangled():
    # No separator row -> not a markdown table -> leave the text intact.
    src = "resultado | valor"
    assert norm(src) == src
