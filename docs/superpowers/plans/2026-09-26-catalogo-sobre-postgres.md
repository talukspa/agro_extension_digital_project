# El catálogo del estándar sobre Postgres — plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que el sub-agente del catálogo lea el estándar desde el Postgres de Supabase en lugar de la copia desactualizada en BigQuery, y borrar BigQuery del repo.

**Architecture:** El sub-agente `bq` se repunta y se renombra a `catalog`: mismo lugar en el grafo, mismas cuatro tools de SQL, otra fuente. Las tools hablan con Postgres por un rol dedicado con `SELECT` en dos tablas y nada más, así que "sólo lectura" deja de depender del prompt. `bq_tools.py`, sus prompts y la dependencia de BigQuery se borran.

**Tech Stack:** Python 3.12, Google ADK 2.7.0, `psycopg` 3, `pytest`, una migración SQL en el repo del app.

**Spec:** `docs/superpowers/specs/2026-09-26-agentes-contra-endpoints-design.md` §2, §5, §7

**Depende de:** `docs/superpowers/plans/2026-09-26-expediente-en-los-agentes-reales.md`, ya ejecutado. Este plan asume que el root tiene tres sub-agentes.

---

## 1. Por qué, con los números

`estandar_pp` y `estandar_aa` en BigQuery son **una importación de Excel hecha una vez**: el esquema documenta la columna `n` como "el número de la fila en la planilla Excel de origen". No existe job, ETL ni script de carga en ninguno de los dos repos, así que no hay mecanismo que pudiera mantenerlas frescas.

Medido el 2026-09-26, después de que la deduplicación de `questions` se completara:

| | BigQuery | Postgres `questions` |
|---|---|---|
| Producción Primaria | 145 códigos (P001–P145) | **129** (P001–P129, sin huecos) |
| Adecuación Agroindustrial | 135 (A001–A135) | 135 |

**Postgres es la fuente de verdad.** Los P130–P145 que sólo existen en BigQuery son restos del Excel viejo, no preguntas que falte migrar. Esto quedó confirmado con el dueño del dato; no lo vuelvas a abrir.

Postgres además es superconjunto en columnas: `verification_type`, `resources`, `is_active`, `options`, `validation_rules`, `updated_at`. BigQuery no tiene forma de saber que una pregunta se desactivó.

Y el bug que esto ya causa: las acciones del plan del productor salen de `implementation_plan_actions`, que vive en Postgres. Hoy, para el mismo código, el sub-agente del catálogo y el del expediente pueden decirle cosas distintas al mismo productor.

---

## 2. El mapeo de columnas, que es el corazón del cambio

Los prompts del sub-agente nombran columnas de BigQuery en cada ejemplo de SQL. Traducirlos mal es cómo el agente queda escribiendo consultas que fallan.

| BigQuery `estandar_*` | Postgres `questions` | ojo |
|---|---|---|
| `codigo` | `question_number` | |
| `nivel` | `level` | es un enum, no texto libre |
| `puntos` | `points` | |
| `dimension` | `section` | |
| `tema` | `subsection` | |
| `buena_practica` | `good_practice` | |
| `accion` | `question_text` | |
| `medio_de_verificacion` | `verification_detail` | |
| `link` / `link_recursos` | `link` | y además `resources`, que BigQuery no tiene |
| `n` | — | no tiene equivalente ni hace falta |
| — | `verification_type` | nuevo |
| — | `is_active` | nuevo: hay que filtrarlo |
| — | `updated_at` | nuevo |

**Tres cosas verificadas que el implementador tiene que respetar.** Las dos
primeras son trampas —fallan en silencio—; la tercera es una capacidad nueva.

1. **`questions.standard_code` está VACÍO en las 264 filas.** La columna existe pero no se pobló. El estándar se resuelve por `JOIN standards ON standards.id = questions.standard_id` y se filtra por `standards.code`. Escribir `WHERE standard_code = 'PRODUCCION_PRIMARIA'` devuelve cero filas sin error, que es el peor modo de falla posible.

2. **`link` ya está poblado en los dos estándares.** Medido el 2026-09-26, después
   de que se corrigiera:

   ```
   PRODUCCION_PRIMARIA      | total 129 | con_link 129 | con_resources 126
   ADECUACION_AGROINDUSTRIAL| total 135 | con_link 135 | con_resources 135
   ```

   Los 129 de PP son URLs distintas, ninguna repetida. Así que `link` se mapea
   directo desde el `link` de BigQuery, sin rodeos.

   **Pero `resources` sigue siendo más rico y no existe en BigQuery:** trae el
   tipo de recurso, un detalle legible y varias URLs por pregunta (`pdf`, `web`,
   `curso`), mientras `link` es una sola. Recuperar material de apoyo es una de
   las capacidades que el prompt del sub-agente reclama como principal, así que
   el prompt nuevo debería ofrecer las dos: `link` como la referencia directa y
   `resources` para cuando el productor pide material. Las tres preguntas de PP
   sin `resources` tienen `link`, así que ninguna queda sin nada.

3. **`is_active` existe y hay que usarlo.** BigQuery no podía saber que una pregunta se desactivó; ahora sí se puede, y una consulta que no lo filtra le muestra al productor requisitos derogados.

---

## 3. Estructura de archivos

| archivo | qué pasa |
|---|---|
| `agro_extension_digital_app/supabase/migrations/<ts>_agent_catalog_reader.sql` | **nuevo, en el otro repo**: el rol de sólo lectura |
| `agents/core/catalog_tools.py` | nuevo, de `bq_tools.py`: mismas 4 tools, psycopg |
| `agents/core/agent.py` | `bq` → `catalog`; se borra el import de `bq_tools` |
| `agents/core/prompts/agent_{pp,aa}/catalog.md` | de `bq.md`, con el mapeo de §2 aplicado |
| `agents/core/prompts/agent_{pp,aa}/catalog_description.md` | de `bq_description.md` |
| `agents/core/prompts/agent_{pp,aa}/root.md` | "BQ" → "CATÁLOGO" en la regla de enrutamiento |
| `agents/deploy.py` | `CATALOG_DSN` entra; `BIGQUERY_DATASET`, `BQ_MAX_BYTES`, `BQ_MAX_ROWS` y `google-cloud-bigquery` salen |
| `agents/pyproject.toml` | `psycopg[binary]` entra, `google-cloud-bigquery` sale |
| `agents/tests/conftest.py` | siembra `CATALOG_DSN`, deja de sembrar `BIGQUERY_DATASET` |

### Se borra

`agents/core/bq_tools.py`, `agents/tests/test_bq_tools.py`, `agents/core/prompts/agent_{pp,aa}/bq.md`, `agents/core/prompts/agent_{pp,aa}/bq_description.md`.

### Sobre el nombre

El sub-agente se llama `bq` y el prompt del root dice "BQ". Cuando lea Postgres eso es mentira, y es la clase de cosa que confunde a quien abra el código en seis meses. Se renombra a `catalog` en el mismo cambio, no después: un rename diferido no se hace nunca.

---

## Task 0: preparar y medir la línea base

**Files:** ninguno

- [ ] **Step 1: Confirmar la línea base de tests**

```bash
cd /Users/rsolar/repos/agro_extension_digital_project/.worktrees/agents-endpoints/agents
env -i PATH=/usr/bin:/bin HOME=$HOME .venv/bin/python -m pytest -q
```

Esperado: `189 passed`. **No sourcees `.env`**: trae el proyecto y el dataset reales, y dos tests de BigQuery fallan por eso — los mismos dos que este plan va a borrar.

- [ ] **Step 2: Guardar el enrutamiento de hoy, para poder comparar**

```bash
cd agents
set -a && . ./.env
. /Users/rsolar/repos/agro_extension_digital_app/.worktrees/agent-layer-pa5/ciruela-certificada/.env.local
export CIRUELA_API_BASE=http://localhost:3100
set +a
.venv/bin/python scripts/measure_routing.py 3
```

La última corrida dio **36/36**. Anota el número que te dé: es la única forma de sostener después que el rename y los prompts nuevos no empeoraron el enrutamiento. Si te da menos de 36/36 **antes** de tocar nada, dilo y no sigas: el punto de partida no es el que dice este plan.

Si aparece `429 RESOURCE_EXHAUSTED`, es cuota de Vertex, no un fallo: el script reintenta solo.

---

## Task 1: el rol de sólo lectura, en el repo del app

**Files:**
- Create: `agro_extension_digital_app/supabase/migrations/<timestamp>_agent_catalog_reader.sql`
- Test: `agro_extension_digital_app/supabase/tests/agent_catalog_reader_test.sql`

Esta es la única pieza que no vive en este repo. Trabaja en
`/Users/rsolar/repos/agro_extension_digital_app/.worktrees/agent-layer-pa5`.

- [ ] **Step 1: Escribir el test que falla**

Sigue el patrón de los tests que ya están en `supabase/tests/`: una transacción envuelta en `BEGIN … ROLLBACK` con `RAISE EXCEPTION` como aserción, de modo que no deje nada escrito.

```sql
-- supabase/tests/agent_catalog_reader_test.sql
--
-- El rol del catálogo: puede leer las dos tablas del estándar y NADA más.
-- Lo importante no es que lea, es lo que NO puede hacer: la garantía de "sólo
-- lectura" tiene que vivir en los grants, no en el prompt del agente.
BEGIN;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'agent_catalog_reader') THEN
    RAISE EXCEPTION 'falta el rol agent_catalog_reader';
  END IF;
END $$;

-- lee las dos que necesita
DO $$
BEGIN
  IF NOT has_table_privilege('agent_catalog_reader', 'public.questions', 'SELECT') THEN
    RAISE EXCEPTION 'agent_catalog_reader no puede leer questions';
  END IF;
  IF NOT has_table_privilege('agent_catalog_reader', 'public.standards', 'SELECT') THEN
    RAISE EXCEPTION 'agent_catalog_reader no puede leer standards';
  END IF;
END $$;

-- NO escribe ninguna de las dos
DO $$
DECLARE
  t text;
  p text;
BEGIN
  FOREACH t IN ARRAY ARRAY['public.questions', 'public.standards'] LOOP
    FOREACH p IN ARRAY ARRAY['INSERT', 'UPDATE', 'DELETE', 'TRUNCATE'] LOOP
      IF has_table_privilege('agent_catalog_reader', t, p) THEN
        RAISE EXCEPTION 'agent_catalog_reader puede % sobre %', p, t;
      END IF;
    END LOOP;
  END LOOP;
END $$;

-- NO alcanza nada del expediente del productor: ésa es la línea que separa el
-- catálogo (dato público del estándar) de los datos de una persona.
DO $$
DECLARE
  t text;
BEGIN
  FOREACH t IN ARRAY ARRAY['public.users', 'public.businesses', 'public.labor_logs',
                           'public.implementation_plans', 'public.implementation_plan_actions',
                           'public.survey_evidence', 'public.question_messages',
                           'public.whatsapp_consent_events'] LOOP
    IF has_table_privilege('agent_catalog_reader', t, 'SELECT') THEN
      RAISE EXCEPTION 'agent_catalog_reader puede leer %, que es del expediente', t;
    END IF;
  END LOOP;
END $$;

-- tiene un statement_timeout: una consulta mala no puede colgar el turno de
-- WhatsApp del productor
DO $$
DECLARE
  cfg text[];
BEGIN
  SELECT rolconfig INTO cfg FROM pg_roles WHERE rolname = 'agent_catalog_reader';
  IF cfg IS NULL OR NOT EXISTS (
    SELECT 1 FROM unnest(cfg) c WHERE c LIKE 'statement_timeout=%'
  ) THEN
    RAISE EXCEPTION 'agent_catalog_reader no tiene statement_timeout';
  END IF;
END $$;

-- y no hereda nada por ser miembro de otro rol
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM pg_auth_members m
    JOIN pg_roles r ON r.oid = m.roleid
    JOIN pg_roles g ON g.oid = m.member
    WHERE g.rolname = 'agent_catalog_reader'
  ) THEN
    RAISE EXCEPTION 'agent_catalog_reader es miembro de otro rol; hereda permisos';
  END IF;
END $$;

SELECT 'ok' AS resultado;
ROLLBACK;
```

- [ ] **Step 2: Correr el test contra la base local y verlo fallar**

```bash
psql "postgresql://postgres:postgres@127.0.0.1:54322/postgres" \
  -f supabase/tests/agent_catalog_reader_test.sql
```

Esperado: `ERROR: falta el rol agent_catalog_reader`.

- [ ] **Step 3: Escribir la migración**

```sql
-- supabase/migrations/<timestamp>_agent_catalog_reader.sql
--
-- Un rol para que el agente lea el catálogo del estándar, y nada más.
--
-- POR QUÉ UN ROL Y NO UN ENDPOINT: el catálogo es de sólo lectura y no tiene
-- ninguna columna por usuario ni por empresa (verificado: 0 columnas con "user"
-- o "business" en `questions` y `standards`), así que no hay aislamiento que un
-- endpoint pueda imponer y un rol no. Y un conjunto fijo de endpoints contesta
-- sólo lo que alguien anticipó, mientras el sub-agente del catálogo existe para
-- contestar lo que nadie enumeró: agregados, filtros por dimensión y tema,
-- búsquedas por concepto.
--
-- POR QUÉ ES MÁS FUERTE QUE LO QUE REEMPLAZA: hoy en BigQuery el "sólo lectura"
-- lo impone `run_query` filtrando la consulta por string. Acá lo impone la
-- ausencia de grants: aunque el modelo escriba un DELETE, Postgres lo rechaza.
--
-- La contraseña NO va acá. Se fija fuera de la migración (ver el runbook), para
-- que el archivo pueda vivir en git.

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'agent_catalog_reader') THEN
    CREATE ROLE agent_catalog_reader WITH LOGIN NOINHERIT;
  END IF;
END $$;

-- Nada por defecto: se parte de cero y se concede sólo lo necesario.
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM agent_catalog_reader;
REVOKE ALL ON SCHEMA public FROM agent_catalog_reader;

GRANT USAGE ON SCHEMA public TO agent_catalog_reader;
GRANT SELECT ON public.questions TO agent_catalog_reader;
GRANT SELECT ON public.standards TO agent_catalog_reader;

-- Una consulta mala no puede colgar el turno de WhatsApp del productor.
ALTER ROLE agent_catalog_reader SET statement_timeout = '10s';
-- Ni dejar una transacción abierta ocupando una conexión del pooler.
ALTER ROLE agent_catalog_reader SET idle_in_transaction_session_timeout = '30s';

-- Las tablas del catálogo tienen RLS activo con políticas pensadas para los
-- roles de la app. Este rol no las necesita: lee el catálogo completo, que es
-- público. Se le concede el bypass explícitamente en lugar de agregarle una
-- política, para que quede en un solo lugar auditable.
--
-- OJO: esto es lo que hay que revisar si alguien alguna vez agrega una columna
-- por productor a `questions`. Hoy no hay ninguna.
ALTER TABLE public.questions FORCE ROW LEVEL SECURITY;
CREATE POLICY agent_catalog_reader_lee_todo ON public.questions
  FOR SELECT TO agent_catalog_reader USING (true);
CREATE POLICY agent_catalog_reader_lee_standards ON public.standards
  FOR SELECT TO agent_catalog_reader USING (true);
```

**Antes de escribirla, verifica el estado real de RLS en las dos tablas:**

```bash
psql "postgresql://postgres:postgres@127.0.0.1:54322/postgres" -c \
  "select relname, relrowsecurity, relforcerowsecurity from pg_class
   where relname in ('questions','standards');"
psql "postgresql://postgres:postgres@127.0.0.1:54322/postgres" -c \
  "select tablename, policyname, roles, cmd from pg_policies
   where tablename in ('questions','standards');"
```

Las dos tienen RLS activo y dos políticas cada una. **Mira qué dicen esas políticas antes de agregar las tuyas**: si alguna ya permite leer a cualquier rol, la política nueva es de más, y agregar una política redundante confunde a quien audite. Ajusta la migración a lo que encuentres y explica en un comentario por qué la forma que elegiste es la correcta.

- [ ] **Step 4: Aplicar y correr el test**

```bash
psql "postgresql://postgres:postgres@127.0.0.1:54322/postgres" \
  -f supabase/migrations/<timestamp>_agent_catalog_reader.sql
psql "postgresql://postgres:postgres@127.0.0.1:54322/postgres" \
  -f supabase/tests/agent_catalog_reader_test.sql
```

Esperado: `ok`.

- [ ] **Step 5: Comprobar en vivo que el rol no puede escribir**

Los `has_table_privilege` prueban los grants; esto prueba el comportamiento. Fija una contraseña local, conéctate **como el rol** e intenta escribir:

```bash
psql "postgresql://postgres:postgres@127.0.0.1:54322/postgres" -c \
  "ALTER ROLE agent_catalog_reader WITH PASSWORD 'local-solo-para-probar';"

D="postgresql://agent_catalog_reader:local-solo-para-probar@127.0.0.1:54322/postgres"
psql "$D" -c "select count(*) from questions;"            # debe funcionar
psql "$D" -c "select count(*) from users;"                 # debe fallar: permiso denegado
psql "$D" -c "update questions set points = 0;"            # debe fallar
psql "$D" -c "delete from standards;"                      # debe fallar
psql "$D" -c "create table colado (x int);"                # debe fallar
```

**Reporta la salida de las cinco.** Si alguna de las cuatro últimas funciona, el rol está mal y no sigas.

- [ ] **Step 6: Commit en el repo del app**

```bash
cd /Users/rsolar/repos/agro_extension_digital_app/.worktrees/agent-layer-pa5
git add supabase/migrations/<timestamp>_agent_catalog_reader.sql supabase/tests/agent_catalog_reader_test.sql
git commit -m "feat(agent): rol de sólo lectura para el catálogo del estándar"
```

---

## Task 2: el driver de Postgres

**Files:**
- Modify: `agents/pyproject.toml`
- Modify: `agents/deploy.py`
- Test: `agents/tests/test_deploy.py`

No hay ningún driver de Postgres en el venv de agents — verificado: `psycopg`, `psycopg2` y `asyncpg` no están.

- [ ] **Step 1: Escribir los tests que fallan**

```python
def test_psycopg_va_en_los_requirements_del_engine():
    """core/catalog_tools.py lo importa; si falta, el engine no arranca."""
    import deploy
    assert any(r.startswith("psycopg") for r in deploy.REQUIREMENTS)


def test_el_pin_de_psycopg_coincide_con_el_lockfile():
    import deploy
    pin = next(r for r in deploy.REQUIREMENTS if r.startswith("psycopg"))
    version = pin.split("==", 1)[1]
    assert version == _version_en_el_lockfile("psycopg")
```

Reusa el helper `_version_de_httpx_en_el_lockfile` que ya está en ese archivo: generalízalo a `_version_en_el_lockfile(nombre)` en lugar de escribir un segundo lector del lockfile. Si lo generalizas, el test de `httpx` tiene que seguir pasando.

- [ ] **Step 2: Correr para verificar que fallan**

```bash
cd agents && env -i PATH=/usr/bin:/bin HOME=$HOME .venv/bin/python -m pytest tests/test_deploy.py -q
```

- [ ] **Step 3: Agregar la dependencia**

En `agents/pyproject.toml`, en `dependencies`:

```toml
    "psycopg[binary]>=3.1,<4.0",
```

`[binary]` a propósito: trae las ruedas precompiladas de libpq, así que el engine no necesita compilar nada ni tener `libpq-dev`. Un `psycopg` sin extra falla al instalarse en un contenedor pelado.

Después regenera el lockfile — es la única task de este plan donde corresponde:

```bash
cd agents && uv lock && uv sync
```

- [ ] **Step 4: Agregar el pin a `REQUIREMENTS`**

Léelo del lockfile, no lo inventes:

```bash
cd agents && awk '/^name = "psycopg"$/{f=1} f&&/^version = /{print $3; exit}' uv.lock
```

```python
    # core/catalog_tools.py lo importa. [binary] trae las ruedas de libpq, así
    # que el engine no compila nada.
    "psycopg[binary]==<la versión del lockfile>",
```

- [ ] **Step 5: Correr los tests**

```bash
cd agents && env -i PATH=/usr/bin:/bin HOME=$HOME .venv/bin/python -m pytest -q
```

- [ ] **Step 6: Commit**

```bash
git add agents/pyproject.toml agents/uv.lock agents/deploy.py agents/tests/test_deploy.py
git commit -m "build(agents): psycopg para leer el catálogo desde Postgres"
```

---

## Task 3: `catalog_tools.py`

**Files:**
- Create: `agents/core/catalog_tools.py`
- Test: `agents/tests/test_catalog_tools.py`

Lee `agents/core/bq_tools.py` completo antes de empezar. Las cuatro tools y el contrato se conservan; cambia el motor. Los comentarios de ese archivo documentan decisiones costosas —los topes leídos por llamada, el memoize de sólo los éxitos, el `default_dataset`— y cada una tiene su equivalente acá.

- [ ] **Step 1: Escribir los tests que fallan**

Cubre, como mínimo:

```python
"""Las cuatro tools del catálogo, sobre Postgres.

Reemplazan a las de BigQuery, que leían una importación de Excel sin sincronizar.
El contrato {ok, error} y la forma de las cuatro tools se conservan: lo que cambia
es el motor y los nombres de las columnas.
"""

# --- el contrato, igual que en bq_tools
async def test_run_query_rechaza_lo_que_no_sea_select(): ...
async def test_run_query_rechaza_select_con_punto_y_coma_y_segunda_sentencia(): ...
async def test_ninguna_tool_levanta_hacia_el_modelo(): ...
async def test_el_tope_de_filas_se_lee_por_llamada(): ...
async def test_sin_dsn_devuelve_un_error_claro_y_no_conecta(): ...

# --- lo propio de Postgres
async def test_list_tables_sólo_ofrece_las_dos_del_catalogo(): ...
async def test_get_schema_nombra_las_columnas_reales(): ...
async def test_check_query_no_ejecuta_la_consulta(): ...
```

**El de "no ejecuta" merece atención.** En BigQuery, `check_query` era un dry-run gratis del servicio. Postgres no tiene dry-run: lo más cercano es `EXPLAIN`, que **planifica** sin ejecutar el cuerpo pero sí abre la consulta. Decide cómo implementarlo y escribe el test que pruebe que no ejecuta — por ejemplo que un `SELECT` sobre una tabla a la que el rol no tiene acceso falle en `check_query` igual que fallaría en `run_query`, o que un `pg_sleep` no cueste el tiempo. Argumenta tu elección: si `EXPLAIN` no da la garantía, decir que `check_query` desaparece también es una respuesta válida, y en ese caso hay que quitarla del prompt y de la lista de tools.

- [ ] **Step 2: Correr para verificar que fallan**

```bash
cd agents && env -i PATH=/usr/bin:/bin HOME=$HOME .venv/bin/python -m pytest tests/test_catalog_tools.py -q
```

Esperado: `ModuleNotFoundError: No module named 'core.catalog_tools'`.

- [ ] **Step 3: Escribir el módulo**

La forma la dicta `bq_tools.py`. Lo que tiene que resolver:

- **El DSN** en `CATALOG_DSN`, leído **por llamada**, nunca ligado al import. Misma razón que en `bq_tools.py` y en `record_tools.py`: una lectura en el import es intesteable por `monkeypatch` y se come el override por engine.
- **Sólo `SELECT`**, y no por confianza: el rol no tiene grants de escritura, así que el filtro del prompt es la segunda capa, no la primera. Igual conviene rechazar lo que no sea `SELECT` para dar un error legible en lugar de un `permission denied` de Postgres.
- **Una sola sentencia.** Rechaza el `;` seguido de más SQL: un `SELECT 1; DROP TABLE x` fallaría por permisos, pero el error sería confuso.
- **Tope de filas**, leído por llamada, con el mismo espíritu que `BQ_MAX_ROWS`.
- **`{ok, error}` y nunca levantar.** Acuérdate del `except` ancho: en `record_tools.py` hubo que ensancharlo porque `httpx.InvalidURL` no hereda de `HTTPError`. Averigua si psycopg tiene una trampa análoga —una excepción de conexión que no descienda de `psycopg.Error`— y documenta lo que encuentres en el comentario del `except`.
- **`list_tables` ofrece sólo `questions` y `standards`.** El modelo escribe SQL con lo que esta tool le dice que existe; ofrecerle una tabla que el rol no puede leer es regalarle un `permission denied`.
- **`get_schema` tiene que nombrar las columnas reales** con una descripción útil, como hace la de BigQuery. Es el prompt del que el modelo saca los nombres.

- [ ] **Step 4: Correr los tests y probar contra la base de verdad**

```bash
cd agents && env -i PATH=/usr/bin:/bin HOME=$HOME .venv/bin/python -m pytest tests/test_catalog_tools.py -q
```

Y una comprobación en vivo, cuya salida quiero en el reporte:

```bash
cd agents
CATALOG_DSN="postgresql://agent_catalog_reader:local-solo-para-probar@127.0.0.1:54322/postgres" \
  .venv/bin/python -c "
import asyncio
from core import catalog_tools as C
async def main():
    print(await C.list_tables())
    print((await C.get_schema('questions'))['schema'][:400])
    print(await C.run_query(\"select count(*) from questions\"))
    print(await C.run_query(\"select s.code, count(*) from questions q join standards s on s.id=q.standard_id where q.is_active group by 1\"))
    print(await C.run_query(\"delete from questions\"))
asyncio.run(main())
"
```

La última tiene que volver como `{ok: False, ...}` con un error legible, no como una excepción.

- [ ] **Step 5: Commit**

```bash
git add agents/core/catalog_tools.py agents/tests/test_catalog_tools.py
git commit -m "feat(agents): las cuatro tools del catálogo, sobre Postgres"
```

---

## Task 4: los prompts del catálogo

**Files:**
- Create: `agents/core/prompts/agent_{pp,aa}/catalog.md`, `catalog_description.md`
- Modify: `agents/core/prompts.py`
- Test: `agents/tests/test_prompts_catalog.py`

Parte de `bq.md` y `bq_description.md` de cada agente y aplica el mapeo de §2. **Estos prompts están escritos con emoji y secciones de "Cambios Clave y Justificación" que no aportan ninguna regla de decisión** — una revisión anterior lo notó y contribuye a la única duda de enrutamiento que quedaba (RAG contra el catálogo para "¿qué es la huella hídrica?"). Aprovecha el rescribido para dejar reglas y no adorno.

- [ ] **Step 1: Escribir los tests que fallan**

Un test por cada trampa de §2, porque son las que rompen en silencio:

```python
@pytest.mark.parametrize("agente", ["agent_pp", "agent_aa"])
def test_no_menciona_ninguna_columna_de_bigquery(agente):
    """Un ejemplo de SQL con los nombres viejos le enseña al modelo a escribir
    consultas que fallan."""
    texto = prompts.catalog_instruction(agente)
    for vieja in ("estandar_pp", "estandar_aa", "buena_practica", "medio_de_verificacion",
                  "link_recursos", "dimension", "tema", "codigo", "puntos", "nivel"):
        assert vieja not in texto, vieja


@pytest.mark.parametrize("agente", ["agent_pp", "agent_aa"])
def test_el_estandar_se_resuelve_por_el_join_no_por_standard_code(agente):
    """questions.standard_code está VACÍO en las 264 filas: filtrar por esa
    columna devuelve cero filas sin error."""
    texto = prompts.catalog_instruction(agente)
    assert "standards" in texto and "standard_id" in texto
    assert "WHERE standard_code" not in texto
    assert "standard_code =" not in texto


@pytest.mark.parametrize("agente", ["agent_pp", "agent_aa"])
def test_ofrece_las_dos_fuentes_de_material_de_apoyo(agente):
    """`link` es una URL por pregunta; `resources` trae tipo, detalle y varias
    (pdf, web, curso). BigQuery sólo tenía la primera, así que el prompt viejo
    no podía nombrar la segunda."""
    texto = prompts.catalog_instruction(agente)
    assert "resources" in texto
    assert "link" in texto


@pytest.mark.parametrize("agente", ["agent_pp", "agent_aa"])
def test_filtra_las_preguntas_desactivadas(agente):
    assert "is_active" in prompts.catalog_instruction(agente)
```

**Invierte cada uno antes de darlos por buenos.** En el plan del expediente los diez tests de prompt resultaron invertibles: afirmaban la presencia de una frase que sobrevivía dentro de su propia negación. Reescribe el `.md` diciendo lo contrario de cada regla, corre, y confirma que el test lo detecta. Reporta cuáles detectan y cuáles no.

- [ ] **Step 2 a 4:** escribir los cuatro `.md`, agregar `catalog_instruction` y `catalog_description` a `prompts.py` siguiendo el patrón de `record_instruction`, y correr.

- [ ] **Step 5: Commit**

```bash
git add agents/core/prompts.py agents/core/prompts/agent_pp/catalog*.md agents/core/prompts/agent_aa/catalog*.md agents/tests/test_prompts_catalog.py
git commit -m "feat(agents): el prompt del catálogo, con las columnas de Postgres"
```

---

## Task 5: el rename en el grafo, y borrar BigQuery

**Files:**
- Modify: `agents/core/agent.py`, `agents/core/prompts/agent_{pp,aa}/root.md`, `agents/deploy.py`, `agents/tests/conftest.py`, `agents/tests/test_core_agent.py`
- Delete: `agents/core/bq_tools.py`, `agents/tests/test_bq_tools.py`, `agents/core/prompts/agent_{pp,aa}/bq.md`, `bq_description.md`

- [ ] **Step 1: Escribir los tests que fallan**

```python
def test_el_root_tiene_rag_catalogo_y_expediente():
    from core.agent import build_app
    app = build_app(name="pp_agent", display_name="PP",
                    main_datastore_env="DATASTORE_PP_ID")
    nombres = {t.agent.name for t in app._tmpl_attrs["agent"].tools}
    assert nombres == {"pp_agent_rag", "pp_agent_catalog", "pp_agent_record"}


def test_no_queda_nada_de_bigquery_en_el_paquete():
    """El rename a medias es peor que ninguno: un `bq` que lee Postgres miente."""
    from pathlib import Path
    raiz = Path(__file__).resolve().parents[1]
    assert not (raiz / "core" / "bq_tools.py").exists()
    for patron in ("bq_tools", "bigquery", "BIGQUERY_DATASET", "BQ_MAX_BYTES"):
        golpes = [
            p for p in raiz.rglob("*.py")
            if ".venv" not in str(p) and patron.lower() in p.read_text().lower()
        ]
        assert not golpes, f"{patron} sigue en {golpes}"


def test_el_root_nombra_al_catalogo_no_a_bq():
    from core import prompts
    for agente in ("agent_pp", "agent_aa"):
        texto = prompts.root_instruction(agente)
        assert "CATÁLOGO" in texto
        assert "BigQuery" not in texto
```

- [ ] **Step 2: Correr y verlos fallar**

- [ ] **Step 3: Hacer el cambio**

En `agent.py`: el import de `bq_tools` pasa a `catalog_tools`, la variable `bq` a `catalog`, el sub-agente a `f"{name}_catalog"`, `BQ_MODEL` a `CATALOG_MODEL`. **Conserva el comentario que explica por qué RAG no lleva planner y el catálogo sí** — sigue siendo cierto: cuatro tools de SQL son un plan.

En los dos `root.md`: "BQ" a "CATÁLOGO" en la regla de enrutamiento y en la frase de rol. Acuérdate de que la frase de rol ya se actualizó una vez a "tres subagentes"; revisa que quede coherente.

En `deploy.py`: `CATALOG_DSN` entra a `RUNTIME_ENV_KEYS`; `BIGQUERY_DATASET` sale de ahí; `BQ_MAX_BYTES` y `BQ_MAX_ROWS` salen de los knobs opcionales; `google-cloud-bigquery` sale de `REQUIREMENTS`; y también de `pyproject.toml`, con `uv lock`.

En `conftest.py`: siembra `CATALOG_DSN`, deja de sembrar `BIGQUERY_DATASET`.

Borra los cuatro archivos.

- [ ] **Step 4: Correr toda la suite**

```bash
cd agents && env -i PATH=/usr/bin:/bin HOME=$HOME .venv/bin/python -m pytest -q
```

Van a desaparecer los tests de `test_bq_tools.py`, así que el total **baja** respecto a los 189 de la línea base. Eso es correcto: anota cuántos eran los de BigQuery y comprueba que la diferencia cuadra. Si desaparece alguno que no era de BigQuery, algo se rompió.

**Y los dos tests que hoy fallan al sourcear `.env`** —`test_query_jobs_set_a_default_dataset` y `test_datastore_builds_full_resource_name`— tienen que dejar de existir el primero. Verifica que sourcear `.env` ya no rompa nada de BigQuery:

```bash
cd agents && set -a && . ./.env && set +a && .venv/bin/python -m pytest -q
```

- [ ] **Step 5: Commit**

```bash
git add -A agents/
git commit -m "refactor(agents): el catálogo lee Postgres; se borra BigQuery"
```

---

## Task 6: medir que no se rompió el enrutamiento

**Files:**
- Modify: `agents/scripts/measure_routing.py`

- [ ] **Step 1: Ajustar el medidor al nombre nuevo**

`_elegidos()` busca los sufijos `("record", "bq", "rag")`. Cambia `bq` por `catalog` y los casos esperados también. Si te olvidas, el medidor reporta que el catálogo nunca se llama y parece una catástrofe que no existe.

- [ ] **Step 2: Medir**

```bash
cd agents
set -a && . ./.env
. /Users/rsolar/repos/agro_extension_digital_app/.worktrees/agent-layer-pa5/ciruela-certificada/.env.local
export CIRUELA_API_BASE=http://localhost:3100
export CATALOG_DSN="postgresql://agent_catalog_reader:<la de tu base local>@127.0.0.1:54322/postgres"
set +a
.venv/bin/python scripts/measure_routing.py 3
```

Compara contra el número de la Task 0. Los tres casos del catálogo son los que pueden moverse, porque su descripción se reescribió entera:

```
"cuántos puntos vale la dimensión Ética?"
"lístame las acciones de Ambiente, tema Agua"
"qué pide la acción P001?"
```

Si el enrutamiento empeoró, **el prompt nuevo es la causa más probable** y hay que afinarlo antes de cerrar. Si mejoró, dilo: reescribir esos prompts sacándoles el adorno era una hipótesis, y confirmarla vale.

- [ ] **Step 3: Comprobar que las respuestas del catálogo ahora son las correctas**

Esto es el punto de todo el plan y no lo cubre ningún test: que el agente conteste con el dato fresco. Pregúntale algo donde BigQuery y Postgres difieran y comprueba la respuesta.

El caso más limpio son los códigos que sólo existen en BigQuery: **P130 a P145**. Antes el agente los habría descrito como si existieran; ahora tiene que decir que no los encuentra.

```bash
cd agents
# con el entorno del Step 2 cargado
.venv/bin/python -c "
import asyncio, logging
logging.getLogger('google.adk').setLevel(logging.CRITICAL)
from google.adk.runners import InMemoryRunner
from google.genai import types
from agent_pp_app.agent_engine_app import app
root = app._tmpl_attrs['agent']
async def preguntar(texto):
    r = InMemoryRunner(agent=root, app_name='cat')
    await r.session_service.create_session(app_name='cat', user_id='c1d1ebe1-5c05-45ce-a9c1-fd4315850baa', session_id='s')
    salida = []
    async for ev in r.run_async(user_id='c1d1ebe1-5c05-45ce-a9c1-fd4315850baa', session_id='s',
                                new_message=types.Content(role='user', parts=[types.Part(text=texto)])):
        for p in (ev.content.parts if ev.content else []) or []:
            if getattr(p, 'text', None): salida.append(p.text)
    print(f'>> {texto}\n{\"\".join(salida)[:400]}\n')
asyncio.run(preguntar('qué pide la acción P140?'))
asyncio.run(preguntar('cuántas acciones tiene el estándar en total?'))
asyncio.run(preguntar('cuántos puntos vale la dimensión Ética?'))
"
```

Lo que esperas: que P140 **no** exista, que el total sea 129 y no 145, y que el puntaje de Ética salga de Postgres.

**Reporta las tres respuestas textuales.** Si el agente sigue describiendo P140, el catálogo no cambió de fuente y hay que averiguar por qué antes de cerrar.

- [ ] **Step 4: Commit**

```bash
git add agents/scripts/measure_routing.py
git commit -F - <<'MSG'
test(agents): el medidor de enrutamiento con el catálogo sobre Postgres

Enrutamiento antes del cambio: <el número de la Task 0>
Después:                       <el número de la Task 6>

Y la comprobación que ningún test cubre — que el agente conteste con el dato
fresco: P140 sólo existía en la copia de BigQuery.

  >> qué pide la acción P140?
  <la respuesta>
MSG
```

---

## 4. Lo que queda fuera, a propósito

- **La contraseña del rol y su rotación.** La migración crea el rol sin contraseña; fijarla es del runbook de despliegue, no de git. El `CATALOG_DSN` de producción sale de Secret Manager como las demás.
- **El egress desde Agent Engine a Supabase.** El diseño lo nombra (pooler, puerto 6543) pero configurarlo es de infraestructura, y este plan se puede ejecutar y probar entero contra la base local.
- **Las tablas `recursos_pp` / `recursos_aa` de BigQuery** (532 y 472 filas). `questions.resources` cubre 126 de 129 en PP y 135 de 135 en AA. Las tres de PP sin recursos hay que mirarlas, pero no bloquean: son tres preguntas sin material de apoyo, no un camino roto. Si al revisarlas resulta que el contenido de `recursos_*` es más rico que el de `resources`, eso es una migración de datos en el repo del app, no un cambio de agente.
- **El sub-agente RAG.** Sus datastores de Vertex AI Search tienen el mismo problema de frescura y nada los sincroniza. Es una decisión aparte y más grande: ahí el contenido son documentos, no filas.
