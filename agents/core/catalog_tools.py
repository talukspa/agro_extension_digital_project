"""Tools del catálogo del estándar, sobre el Postgres de Supabase.

Reemplazan a las de BigQuery. `estandar_pp` y `estandar_aa` eran una importación
de Excel hecha una vez —el esquema documentaba la columna `n` como "el número de
la fila en la planilla Excel de origen"— y nada las sincronizaba: 145 códigos de
Producción Primaria contra los 129 que tiene `questions`. Como las acciones del
plan del productor ya salen de Postgres, el agente podía decirle dos cosas
distintas sobre el mismo código.

LA GARANTÍA DE SÓLO LECTURA NO VIVE ACÁ. Vive en los grants del rol
`agent_catalog_reader`: `SELECT` en dos tablas y nada más, sin acceso a ninguna
tabla del expediente, con `default_transaction_read_only`. Verificado conectándose
como el rol y apagando esa última capa a mano — los grants aguantan solos. El
filtro de `_is_select` de acá es la segunda capa, y está sobre todo para dar un
error legible en lugar de un `permission denied` que el modelo traduce a "la
plataforma está caída".

Y el rol filtra `is_active` en su política, así que el agente **no puede** mostrar
requisitos derogados, no sólo "no debería". BigQuery no tenía forma de saberlo.

Los topes y el DSN se leen POR LLAMADA, nunca ligados al import: misma razón que
los de core/bq_tools.py y core/record_tools.py — una lectura en el import es
intesteable por monkeypatch y se come el override por engine.
"""
from __future__ import annotations

import os
from typing import Any

import psycopg

# Las dos únicas tablas que el rol puede leer. La lista se usa para rechazar una
# tabla fuera del catálogo con un error propio: el modelo escribe SQL con lo que
# `list_tables` le dice que existe, y pedirle `users` tiene que dar un mensaje
# que él entienda, no el `permission denied` de Postgres.
TABLAS = ("questions", "standards")

_DEFAULT_MAX_ROWS = 100
CONNECT_TIMEOUT = 10

# Descripciones para el modelo. Postgres no tiene comentarios en estas columnas,
# y el `get_schema` de BigQuery sí traía descripciones — eran parte del prompt del
# que el modelo saca cómo consultar. Se escriben acá para no perder eso.
#
# Las dos primeras líneas de `standard_id` y `standard_code` son la trampa más
# cara del cambio: `standard_code` existe y está VACÍA en las 264 filas, así que
# `WHERE standard_code = 'PRODUCCION_PRIMARIA'` devuelve cero filas SIN error.
_DESCRIPCIONES: dict[str, dict[str, str]] = {
    "questions": {
        "question_number": "Código de la acción, por ejemplo 'P001' o 'A001'.",
        "standard_id": (
            "FK a standards.id. El estándar SIEMPRE se resuelve por este JOIN."
        ),
        "standard_code": (
            "NO LA USES: la columna existe pero está vacía en todas las filas, "
            "así que filtrar por ella devuelve cero filas sin ningún error. "
            "El código del estándar sale de standards.code por el JOIN."
        ),
        "question_text": "La acción concreta que debe ejecutar el predio o la planta.",
        "good_practice": "El enunciado general de la buena práctica.",
        "verification_detail": (
            "El medio de verificación: qué evidencia hay que presentar."
        ),
        "verification_type": "Tipo de verificación esperada.",
        "level": "Nivel de exigencia: Fundamental, Básico, Intermedio, Avanzado.",
        "points": "Puntaje asignado a la acción.",
        "section": "Dimensión: Ambiente, Calidad, Gestión, Social, Ética.",
        "subsection": "Temática dentro de la dimensión: Agua, Suelo, Residuos, etc.",
        "link": "URL de la guía o normativa asociada.",
        "resources": (
            "jsonb con el material de apoyo: una lista de "
            "{type, detail, urls{pdf,web,curso}}. Más rico que `link`, que trae "
            "una sola URL. Úsalo cuando el productor pida material."
        ),
        "is_active": (
            "Si la acción sigue vigente. El rol del agente sólo ve las activas, "
            "así que no hace falta filtrarlo, pero tampoco molesta."
        ),
        "options": "jsonb con las opciones de respuesta, si la pregunta las tiene.",
        "validation_rules": "jsonb con reglas de validación de la respuesta.",
        "updated_at": "Cuándo se modificó la fila por última vez.",
    },
    "standards": {
        "code": "PRODUCCION_PRIMARIA o ADECUACION_AGROINDUSTRIAL.",
        "name": "El nombre del estándar como se le muestra al productor.",
        "version": "Versión del estándar.",
        "category": "Categoría del estándar.",
        "is_active": "Si el estándar sigue vigente.",
    },
}


def _dsn() -> str:
    return os.environ.get("CATALOG_DSN", "")


def _max_rows() -> int:
    return int(os.environ.get("CATALOG_MAX_ROWS", str(_DEFAULT_MAX_ROWS)))


def _connect() -> psycopg.Connection:
    """Conexión nueva por llamada, no cacheada.

    Misma razón que el `_client()` de core/bq_tools.py: el AdkApp se deepcopy'a al
    crear el engine, y una conexión cacheada guarda referencias a módulos que no
    se pueden picklear.
    """
    return psycopg.connect(_dsn(), connect_timeout=CONNECT_TIMEOUT,
                           autocommit=True)


def _is_select(sql: str) -> bool:
    """True sólo para UNA sentencia de lectura.

    El chequeo de una sola sentencia no es decoración: un guard que mira sólo el
    primer token dejaría pasar el DROP de `SELECT 1; DROP TABLE t`. Los grants del
    rol lo rechazarían igual, pero un error que dice "sólo se permiten consultas
    SELECT" no debería afirmar más de lo que impone.

    Un punto y coma dentro de un literal también se rechaza. Es un falso negativo
    deliberado: errar hacia el rechazo le cuesta al modelo una reescritura, errar
    al otro lado cuesta una sentencia que nunca quisimos permitir.
    """
    limpio = sql.strip().rstrip(";").strip()
    if ";" in limpio:
        return False
    cabeza = limpio.lstrip("(").lstrip().upper()
    return cabeza.startswith("SELECT") or cabeza.startswith("WITH")


def _sin_dsn(extra: dict[str, Any]) -> dict[str, Any]:
    """El error de configuración, con el nombre de la variable que falta.

    Se nombra la variable y no su valor: el DSN lleva la contraseña del rol.
    """
    return {"ok": False,
            "error": "CATALOG_DSN no está configurada en este engine.",
            **extra}


def _filas_como_dicts(cur, max_rows: int) -> tuple[list[dict], bool]:
    columnas = [c.name for c in (cur.description or [])]
    filas, truncado = [], False
    for i, fila in enumerate(cur.fetchall()):
        if i >= max_rows:
            truncado = True
            break
        filas.append(dict(zip(columnas, fila)))
    return filas, truncado


def list_tables() -> dict:
    """Lista las tablas del catálogo del estándar que se pueden consultar."""
    if not _dsn():
        return _sin_dsn({"tables": []})
    try:
        with _connect() as conn, conn.cursor() as cur:
            # Se consulta information_schema en lugar de devolver la constante:
            # así la lista refleja lo que el rol REALMENTE alcanza. Si alguien le
            # quita un grant, el modelo deja de ver la tabla en vez de pedirla y
            # recibir un permission denied.
            cur.execute(
                "select table_name from information_schema.tables "
                "where table_schema = 'public' and table_name = any(%s) "
                "order by table_name",
                (list(TABLAS),),
            )
            return {"ok": True, "error": None,
                    "tables": [f[0] for f in cur.fetchall()]}
    except Exception as e:  # noqa: BLE001 — que lo vea el modelo, nunca crashear
        return {"ok": False, "error": str(e), "tables": []}


def get_schema(table: str) -> dict:
    """Devuelve las columnas de una tabla del catálogo, con qué significa cada una."""
    if table not in TABLAS:
        return {"ok": False, "schema": "",
                "error": (f"'{table}' no es del catálogo. Las tablas disponibles "
                          f"son: {', '.join(TABLAS)}.")}
    if not _dsn():
        return _sin_dsn({"schema": ""})
    try:
        with _connect() as conn, conn.cursor() as cur:
            cur.execute(
                "select column_name, data_type from information_schema.columns "
                "where table_schema = 'public' and table_name = %s "
                "order by ordinal_position",
                (table,),
            )
            descripciones = _DESCRIPCIONES.get(table, {})
            lineas = []
            for nombre, tipo in cur.fetchall():
                desc = descripciones.get(nombre)
                lineas.append(f"{nombre} {tipo}" + (f" — {desc}" if desc else ""))
            return {"ok": True, "error": None, "schema": "\n".join(lineas)}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e), "schema": ""}


def check_query(sql: str) -> dict:
    """Valida una consulta sin ejecutarla, y devuelve su plan.

    BigQuery tenía un dry-run gratis del servicio; Postgres no. `EXPLAIN` es el
    equivalente: planifica sin ejecutar el cuerpo —verificado, un EXPLAIN de
    `pg_sleep(3)` tarda 0.00s— y detecta los tres errores que el modelo comete
    escribiendo SQL: tabla inexistente, columna inexistente y falta de permiso.
    """
    if not _is_select(sql):
        return {"ok": False, "plan": "",
                "error": "Sólo se permiten consultas SELECT o WITH, y una sola."}
    if not _dsn():
        return _sin_dsn({"plan": ""})
    try:
        with _connect() as conn, conn.cursor() as cur:
            cur.execute("EXPLAIN " + sql)
            filas = cur.fetchall()
            return {"ok": True, "error": None,
                    "plan": "\n".join(str(f[0]) for f in filas)}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e), "plan": ""}


def run_query(sql: str, max_rows: int = 100) -> dict:
    """Ejecuta una consulta de lectura y devuelve hasta max_rows filas."""
    if not _is_select(sql):
        return {"ok": False, "rows": [], "truncated": False,
                "error": "Sólo se permiten consultas SELECT o WITH, y una sola."}
    if not _dsn():
        return _sin_dsn({"rows": [], "truncated": False})
    # El tope del entorno es un techo sobre lo que pidió el modelo, no un valor
    # por defecto. Un modelo que pide 1000 filas recibe el techo, no un error.
    max_rows = min(max_rows, _max_rows())
    try:
        with _connect() as conn, conn.cursor() as cur:
            cur.execute(sql)
            filas, truncado = _filas_como_dicts(cur, max_rows)
            return {"ok": True, "error": None, "rows": filas,
                    "truncated": truncado}
    except Exception as e:  # noqa: BLE001
        # Ancho a propósito. Los cinco casos de DSN malo que probé SÍ heredan de
        # psycopg.Error, así que acá no hay una trampa como la de
        # httpx.InvalidURL en record_tools.py — pero el except se queda ancho
        # igual: el costo de equivocarse es que se caiga el turno del productor.
        return {"ok": False, "error": str(e), "rows": [], "truncated": False}


TOOLS = [list_tables, get_schema, check_query, run_query]
