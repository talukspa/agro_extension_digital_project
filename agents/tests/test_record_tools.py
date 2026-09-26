"""Las tools del expediente: contrato, identidad y cuerpos exactos."""
import pytest

from core import record_tools


class FakeToolContext:
    """Lo mínimo que las tools leen de un ToolContext real: user_id."""

    def __init__(self, user_id):
        self.user_id = user_id


PRODUCTOR = "c1d1ebe1-5c05-45ce-a9c1-fd4315850baa"


async def test_sin_uuid_la_tool_se_niega_y_no_llama_a_nadie(monkeypatch):
    """Un teléfono sin vincular llega como user_id: no es un productor."""
    llamadas = []
    monkeypatch.setattr(record_tools.httpx, "AsyncClient",
                        lambda *a, **k: llamadas.append(1))
    r = await record_tools.obtener_perfil_empresa(FakeToolContext("56912345678"))
    assert r == {"ok": False, "error": "SESSION_WITHOUT_PRODUCER"}
    assert llamadas == []


async def test_producer_user_id_no_es_parametro_de_ninguna_tool():
    """La propiedad de seguridad: el modelo no puede elegir de quién es el expediente."""
    import inspect
    for fn in record_tools.TOOLS:
        params = set(inspect.signature(fn).parameters)
        assert "producer_user_id" not in params, fn.__name__
        assert "producerUserId" not in params, fn.__name__
        assert "productor" not in params, fn.__name__
