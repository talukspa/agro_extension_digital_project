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
    # PR-C will add [fuente: ...] citations — the link regex must NOT eat them.
    assert norm("dato [fuente: faq]") == "dato [fuente: faq]"


def test_plain_text_unchanged():
    assert norm("Hola 👋 ¿en qué ayudo?") == "Hola 👋 ¿en qué ayudo?"
