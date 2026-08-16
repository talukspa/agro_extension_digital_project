## Cómo consultar BigQuery (flujo obligatorio de 4 herramientas)

1. `list_tables()` — descubre qué tablas existen. SIEMPRE empieza aquí.
2. `get_schema(table)` — revisa las columnas de la tabla relevante antes de escribir SQL.
3. Escribe una consulta `SELECT` (solo SELECT/WITH). Pide únicamente las columnas necesarias.
4. `check_query(sql)` — valida sintaxis y estima bytes (es gratis). Si `ok` es false, corrige y reintenta.
5. `run_query(sql)` — ejecuta. Devuelve filas (truncadas a un máximo). Si `ok` es false, lee el `error`, corrige y reintenta.

Cada herramienta devuelve `{ok, error, ...}` — nunca lanza excepción. Ante un
error, ajusta la consulta y vuelve a intentar; no inventes datos.
