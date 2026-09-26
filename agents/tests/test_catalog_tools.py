"""Las cuatro tools del catálogo, sobre Postgres.

Reemplazan a las de BigQuery, que leían una importación de Excel que nada
sincronizaba: 145 códigos de Producción Primaria contra los 129 que tiene
`questions`. La forma de las cuatro tools y el contrato `{ok, error}` se
conservan; lo que cambia es el motor y los nombres de las columnas.

La garantía de sólo lectura NO vive acá: vive en los grants del rol
`agent_catalog_reader`, probados en `supabase/tests/agent_catalog_reader_test.sql`
del repo del app. El filtro de `_is_select` es la segunda capa, y está para dar un
error legible en lugar de un `permission denied` que el modelo no sabe interpretar.
"""
import psycopg
import pytest

from core import catalog_tools


# --------------------------------------------------------------- dobles de psycopg
class FakeColumna:
    """psycopg expone `cursor.description` como objetos con `.name`, no como
    tuplas. Un doble que devuelve tuplas hace fallar el código que SÍ funciona
    contra la base real — me pasó escribiendo estos tests."""

    def __init__(self, name):
        self.name = name


class FakeCursor:
    """Doble del cursor: registra el SQL y devuelve lo que se le programó."""

    def __init__(self, registro, filas=None, descripcion=None, levanta=None):
        self._registro = registro
        self._filas = filas if filas is not None else []
        self.description = ([FakeColumna(c[0]) for c in descripcion]
                            if descripcion else None)
        self._levanta = levanta

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql, params=None):
        self._registro.append((sql, params))
        if self._levanta is not None:
            raise self._levanta

    def fetchall(self):
        return self._filas

    def fetchone(self):
        return self._filas[0] if self._filas else None


class FakeConn:
    def __init__(self, registro, **kwargs):
        self._registro = registro
        self._kwargs = kwargs
        self.autocommit = False

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def cursor(self, **kw):
        return FakeCursor(self._registro, **self._kwargs)


def _stub(monkeypatch, filas=None, descripcion=None, levanta=None,
          levanta_al_conectar=None):
    registro = []

    def conectar():
        if levanta_al_conectar is not None:
            raise levanta_al_conectar
        return FakeConn(registro, filas=filas, descripcion=descripcion,
                        levanta=levanta)

    monkeypatch.setenv("CATALOG_DSN", "postgresql://falso/falso")
    monkeypatch.setattr(catalog_tools, "_connect", conectar)
    return registro


# ------------------------------------------------------------------- el contrato
@pytest.mark.parametrize("sql", [
    "delete from questions",
    "DROP TABLE questions",
    "update questions set points = 0",
    "insert into questions(question_text) values ('x')",
    "truncate questions",
    "grant all on questions to public",
    "  DeLeTe FrOm questions  ",
])
def test_run_query_rechaza_lo_que_no_sea_select(sql):
    r = catalog_tools.run_query(sql)
    assert r["ok"] is False
    assert "SELECT" in r["error"]
    assert r["rows"] == []


@pytest.mark.parametrize("sql", [
    "select 1; drop table questions",
    "select 1;drop table questions",
    "WITH x AS (select 1) select * from x; delete from questions",
])
def test_run_query_rechaza_una_segunda_sentencia(sql):
    """No es decoración: un guard que mira sólo el primer token dejaría pasar el
    DROP. Los grants lo rechazarían igual, pero el error diría otra cosa."""
    assert catalog_tools.run_query(sql)["ok"] is False


@pytest.mark.parametrize("sql", ["select 1", "  SELECT 1  ", "select 1;",
                                 "with x as (select 1) select * from x",
                                 "(select 1)"])
def test_is_select_acepta_un_select_solo(sql):
    assert catalog_tools._is_select(sql) is True


@pytest.mark.parametrize("tool,llaves", [
    ("list_tables", ("ok", "error", "tables")),
    ("get_schema", ("ok", "error", "schema")),
    ("check_query", ("ok", "error", "plan")),
    ("run_query", ("ok", "error", "rows", "truncated")),
])
def test_todas_devuelven_el_contrato_completo(monkeypatch, tool, llaves):
    """El plugin de reintentos lee `ok`; el modelo lee el resto. Una tool que
    omite una llave en el camino de error deja al modelo sin nada que mirar."""
    _stub(monkeypatch, levanta_al_conectar=psycopg.OperationalError("sin ruta"))
    fn = getattr(catalog_tools, tool)
    r = fn("questions") if tool in ("get_schema",) else (
        fn() if tool == "list_tables" else fn("select 1"))
    assert set(llaves) <= set(r)
    assert r["ok"] is False


def test_ninguna_tool_levanta_hacia_el_modelo(monkeypatch):
    """core/retry_plugin.py está construido sobre "nunca levantar": un raise acá
    invierte el contrato justo cuando el modelo ya está en problemas."""
    _stub(monkeypatch, levanta=psycopg.errors.UndefinedTable("no existe"))
    assert catalog_tools.run_query("select 1")["ok"] is False
    assert catalog_tools.check_query("select 1")["ok"] is False
    assert catalog_tools.get_schema("questions")["ok"] is False


def test_una_excepcion_que_no_es_de_psycopg_tampoco_levanta(monkeypatch):
    """El `except` es ancho a propósito. Verificado que los cinco casos de DSN
    malo SÍ heredan de psycopg.Error, así que acá no hay una trampa como la de
    httpx.InvalidURL — pero el except ancho se queda igual, porque el costo de
    equivocarse es que se caiga el turno del productor."""
    _stub(monkeypatch, levanta=RuntimeError("algo raro del driver"))
    assert catalog_tools.run_query("select 1")["ok"] is False


def test_sin_dsn_no_intenta_conectar(monkeypatch):
    intentos = []
    monkeypatch.delenv("CATALOG_DSN", raising=False)
    monkeypatch.setattr(catalog_tools, "_connect",
                        lambda: intentos.append(1))
    r = catalog_tools.run_query("select 1")
    assert r["ok"] is False
    assert "CATALOG_DSN" in r["error"]
    assert intentos == []


# ------------------------------------------------------ leído por llamada, no al importar
def test_el_dsn_se_lee_por_llamada(monkeypatch):
    """Misma razón que los topes de bq_tools y las bases de record_tools: una
    lectura en el import es intesteable por monkeypatch y se come el override por
    engine."""
    monkeypatch.setenv("CATALOG_DSN", "postgresql://primero/d")
    assert catalog_tools._dsn() == "postgresql://primero/d"
    monkeypatch.setenv("CATALOG_DSN", "postgresql://segundo/d")
    assert catalog_tools._dsn() == "postgresql://segundo/d"


def test_el_tope_de_filas_se_lee_por_llamada(monkeypatch):
    monkeypatch.setenv("CATALOG_MAX_ROWS", "7")
    assert catalog_tools._max_rows() == 7
    monkeypatch.setenv("CATALOG_MAX_ROWS", "9")
    assert catalog_tools._max_rows() == 9


def test_el_tope_acota_lo_que_el_modelo_pidio(monkeypatch):
    """El tope es un techo sobre lo que pidió el modelo, no un valor por defecto."""
    filas = [(i,) for i in range(50)]
    _stub(monkeypatch, filas=filas, descripcion=[("n",)])
    monkeypatch.setenv("CATALOG_MAX_ROWS", "5")
    r = catalog_tools.run_query("select n from questions", max_rows=40)
    assert len(r["rows"]) == 5
    assert r["truncated"] is True


# ---------------------------------------------------------------- las cuatro tools
def test_list_tables_solo_ofrece_las_del_catalogo(monkeypatch):
    """El modelo escribe SQL con lo que esta tool le dice que existe: ofrecerle
    una tabla que el rol no puede leer es regalarle un permission denied."""
    _stub(monkeypatch, filas=[("questions",), ("standards",)],
          descripcion=[("table_name",)])
    r = catalog_tools.list_tables()
    assert r["ok"] is True
    assert set(r["tables"]) == {"questions", "standards"}


def test_get_schema_rechaza_una_tabla_fuera_del_catalogo(monkeypatch):
    """`users` no es del catálogo. Mejor un error claro acá que un permission
    denied que el modelo traduce a "la plataforma está caída"."""
    _stub(monkeypatch)
    r = catalog_tools.get_schema("users")
    assert r["ok"] is False
    assert "questions" in r["error"] and "standards" in r["error"]


def test_check_query_no_ejecuta_la_consulta(monkeypatch):
    """BigQuery tenía dry-run gratis; Postgres no. EXPLAIN planifica sin ejecutar
    el cuerpo — verificado: un EXPLAIN de pg_sleep(3) tarda 0.00s."""
    registro = _stub(monkeypatch, filas=[("Seq Scan on questions",)],
                     descripcion=[("QUERY PLAN",)])
    r = catalog_tools.check_query("select count(*) from questions")
    assert r["ok"] is True
    assert registro[0][0].upper().startswith("EXPLAIN")


def test_check_query_rechaza_lo_que_no_sea_select():
    assert catalog_tools.check_query("delete from questions")["ok"] is False


def test_run_query_devuelve_dicts_con_los_nombres_de_columna(monkeypatch):
    _stub(monkeypatch, filas=[("P001", 5)], descripcion=[("question_number",), ("points",)])
    r = catalog_tools.run_query("select question_number, points from questions")
    assert r["ok"] is True
    assert r["rows"] == [{"question_number": "P001", "points": 5}]


# ------------------------------------------- contra la base de verdad, si está
DSN_LOCAL = ("postgresql://agent_catalog_reader:local-solo-para-probar"
             "@127.0.0.1:54322/postgres")


def _hay_base_local() -> bool:
    try:
        with psycopg.connect(DSN_LOCAL, connect_timeout=2):
            return True
    except Exception:  # noqa: BLE001
        return False


sin_base = pytest.mark.skipif(
    not _hay_base_local(),
    reason="necesita la Supabase local con el rol agent_catalog_reader")


@sin_base
def test_contra_la_base_real_el_catalogo_tiene_los_dos_estandares(monkeypatch):
    monkeypatch.setenv("CATALOG_DSN", DSN_LOCAL)
    r = catalog_tools.run_query(
        "select s.code, count(*) n from questions q "
        "join standards s on s.id = q.standard_id group by 1 order by 1")
    assert r["ok"] is True
    codigos = {f["code"]: f["n"] for f in r["rows"]}
    assert set(codigos) == {"PRODUCCION_PRIMARIA", "ADECUACION_AGROINDUSTRIAL"}
    assert sum(codigos.values()) > 200


@sin_base
def test_contra_la_base_real_no_alcanza_el_expediente(monkeypatch):
    """La línea que separa el catálogo de los datos de una persona. El rol la
    impone; esto comprueba que la tool la reporta legible en lugar de levantar."""
    monkeypatch.setenv("CATALOG_DSN", DSN_LOCAL)
    r = catalog_tools.run_query("select count(*) from users")
    assert r["ok"] is False
    assert "permission denied" in r["error"].lower()


@sin_base
def test_contra_la_base_real_una_escritura_no_pasa(monkeypatch):
    monkeypatch.setenv("CATALOG_DSN", DSN_LOCAL)
    assert catalog_tools.run_query("delete from questions")["ok"] is False


@sin_base
def test_contra_la_base_real_get_schema_nombra_las_columnas(monkeypatch):
    """Es el prompt del que el modelo saca los nombres: si falta una columna,
    el modelo no la usa nunca."""
    monkeypatch.setenv("CATALOG_DSN", DSN_LOCAL)
    r = catalog_tools.get_schema("questions")
    assert r["ok"] is True
    for columna in ("question_number", "level", "points", "section", "subsection",
                    "good_practice", "question_text", "verification_detail",
                    "link", "resources", "is_active", "standard_id"):
        assert columna in r["schema"], columna


@sin_base
def test_contra_la_base_real_el_schema_avisa_de_las_dos_trampas(monkeypatch):
    """standard_code está vacío en las 264 filas y filtrar por ahí devuelve cero
    filas SIN error. Y el estándar sale del JOIN. Si el schema no lo dice, el
    modelo lo descubre escribiendo una consulta que "funciona" y no trae nada."""
    monkeypatch.setenv("CATALOG_DSN", DSN_LOCAL)
    schema = catalog_tools.get_schema("questions")["schema"]
    assert "standard_id" in schema
    assert "vacía" in schema or "vacio" in schema.lower()


@sin_base
def test_contra_la_base_real_check_query_detecta_una_columna_inexistente(monkeypatch):
    monkeypatch.setenv("CATALOG_DSN", DSN_LOCAL)
    r = catalog_tools.check_query("select no_existe from questions")
    assert r["ok"] is False


@sin_base
def test_contra_la_base_real_check_query_no_gasta_el_tiempo_de_la_consulta(monkeypatch):
    """pg_sleep(3) bajo EXPLAIN no se ejecuta. Si algún día check_query pasara a
    ejecutar de verdad, esto lo delata."""
    import time
    monkeypatch.setenv("CATALOG_DSN", DSN_LOCAL)
    t = time.time()
    catalog_tools.check_query("select pg_sleep(3)")
    assert time.time() - t < 2
