# Los agentes reales contra los endpoints del app

Fecha: 2026-09-26 · Reemplaza parcialmente a `docs/architecture/2026-08-08-arquitectura-agente-supabase.md` (ver §7)

## 1. El problema

Los agentes `agent_pp_app` y `agent_aa_app` responden sobre el estándar pero no
saben nada del productor que les escribe: no pueden decirle cómo va, qué le
falta, ni recibirle una foto. La capa `/api/agent/*` del app ya existe y expone
todo eso; ningún agente la llama.

Y el catálogo que sí consultan está desactualizado. El sub-agente text2sql lee
`estandar_pp` / `estandar_aa` en BigQuery, que son **una importación de Excel
hecha una vez** — el esquema documenta la columna `n` como "el número de la fila
en la planilla Excel de origen". No existe job, ETL ni script de carga en ninguno
de los dos repos.

Medido el 2026-09-26 contra la Supabase local:

| | BigQuery | Postgres `questions` |
|---|---|---|
| Producción Primaria | 145 códigos (P001–P145) | 129 distintos (258 filas, duplicadas) |
| Adecuación Agroindustrial | 135 (A001–A135) | 135 |
| última modificación | importación única | `updated_at` = hoy |

Postgres es además superconjunto en columnas: `verification_type`,
`resources jsonb`, `is_active`, `options`, `validation_rules`, `updated_at`.
BigQuery no tiene forma de saber que una pregunta se desactivó.

**El bug que esto ya causa:** las acciones del plan del productor salen de
`implementation_plan_actions`, que vive en Postgres. Para el mismo código, el
sub-agente de BigQuery y el expediente pueden decirle cosas distintas al mismo
productor. No es un riesgo futuro: es la situación actual con dos fuentes.

La duplicación de filas de PP se está corrigiendo por separado y este diseño no
depende de ella.

## 2. Decisión

**El app es la única fuente.** Los dos agentes leen el catálogo desde el Postgres
de Supabase y el expediente desde `/api/agent/*`. BigQuery se borra.

Lo que se descartó, y por qué:

- **Sincronizar BigQuery con un job.** Abarata mantener el duplicado en lugar de
  eliminarlo. El espejo siempre va atrás y el modo de falla de las dos respuestas
  contradictorias sigue existiendo, sólo con menos ventana.
- **Que RAG absorba el catálogo.** Los datastores de Vertex AI Search tienen el
  mismo problema —se armaron de documentos y tampoco los sincroniza nada— y no
  pueden hacer filtros exactos ni agregados. Sería cambiar una fuente vieja por
  otra, perdiendo precisión.
- **Endpoints de catálogo en el app.** Cualquier conjunto fijo de endpoints
  contesta sólo lo que alguien anticipó; el text2sql contesta lo que nadie
  enumeró. Como el catálogo es de sólo lectura y no tiene ninguna columna por
  usuario ni por empresa (verificado: 0 columnas `%user%`/`%business%` en
  `questions` y `standards`), no hay nada que un endpoint proteja que un rol de
  Postgres restringido no proteja mejor.

## 3. Topología

`root` enruta entre tres sub-agentes:

| sub-agente | fuente | estado |
|---|---|---|
| RAG | Vertex AI Search ×4 | sin cambios |
| CATÁLOGO | Postgres `questions`, `standards` | es el sub-agente BQ, repuntado |
| EXPEDIENTE | `/api/agent/*` | nuevo |

El catálogo hereda al sub-agente de BigQuery: mismo lugar en el grafo, mismas 4
tools, mismo prompt con las tablas y los nombres de columna cambiados. Es un
repunte, no un sub-agente nuevo.

## 4. Identidad del productor

`/api/agent/*` necesita un `producerUserId`. Hoy no existe: el webhook llama
`send_message_to_agent(phone, app_name, phone, transcript)` — teléfono como
`user_id` y como `session_id`.

**El webhook resuelve la identidad y manda el uuid como `user_id`.** Llama a
`/api/agent/resolve-identity` con el `wa_id`, recibe el `producerUserId` y lo pasa
a `async_stream_query(user_id=<uuid>, session_id=<phone>, ...)`. Las tools lo leen
de `tool_context.user_id`.

Verificado en el ADK instalado (2026-09-26):

```
tool_context.user_id         = c1d1ebe1-5c05-45ce-a9c1-fd4315850baa
tool_context.session.user_id = c1d1ebe1-5c05-45ce-a9c1-fd4315850baa
```

**No se usa el session state**, contra lo que dice el documento de agosto. El
state se fija en `create_session`, y el webhook cachea el `AlreadyExists` para
caer en `async_get_session`: de la segunda vuelta en adelante no se vuelve a
fijar. Si el productor verifica su teléfono a mitad de conversación, el state
queda viejo. `user_id` viaja fresco en cada llamada y no tiene ese modo de falla.

**El `producerUserId` sí va en el body HTTP y no se puede sacar.** El
`AGENT_SERVICE_TOKEN` es uno solo y compartido: dice "soy el agente", no "soy
este productor". Las RPC hacen `set_config('request.jwt.claims', {'sub':
p_user_id})`, así que ese token alcanza a cualquier productor y el campo del body
es lo que elige a cuál. La protección real es que **`producerUserId` nunca es un
parámetro visible para el modelo**: se inyecta desde el `ToolContext` y no
aparece en el schema que ve Gemini.

La alternativa que sí eliminaría el campo —un token corto con alcance a un solo
productor— obligaría a meter un bearer token en el session store de Agent Engine
y en los traces. Un uuid en un body es mejor lugar para eso que un secreto en el
store de sesiones.

**Teléfono sin vincular:** `resolve-identity` responde 404 y el webhook no tiene
uuid, así que manda el teléfono. Las tools del expediente verifican forma de uuid
y se niegan; el agente le pide completar su registro. RAG y catálogo siguen
funcionando: son datos públicos del estándar.

## 5. Acceso al catálogo

Un rol de Postgres dedicado, con `SELECT` en `questions` y `standards` y nada
más. Sin grants de escritura, "sólo lectura" deja de depender de que el modelo se
porte bien — hoy en BigQuery `run_query` lo filtra por string, que es más débil.

El rol lleva `statement_timeout`: una consulta mala no puede colgar el turno de
WhatsApp.

La conexión sale por el pooler de Supabase (6543). La credencial va en Secret
Manager, inyectada al engine igual que las demás.

**Esto es lo único que toca el otro repo:** crear el rol y sus grants es una
migración en `agro_extension_digital_app/supabase/migrations`. Es la única pieza
de este diseño que no vive acá, y son ~15 líneas de SQL: `CREATE ROLE`,
`GRANT SELECT` en dos tablas, `ALTER ROLE SET statement_timeout`. Ninguna función,
ningún endpoint.

## 6. Archivos

```
core/catalog_tools.py          de bq_tools.py; psycopg en lugar de BigQuery
core/record_tools.py           de la rama feat/agente-wa-expediente
core/agent.py                  tercer sub-agente; se borra el de BigQuery
core/prompts/agent_pp/catalog.md, catalog_description.md
core/prompts/agent_pp/record.md, record_description.md
core/prompts/agent_aa/…        idem
core/prompts/agent_{pp,aa}/root.md   regla de enrutamiento del expediente
deploy.py                      CIRUELA_API_BASE, AGENT_SERVICE_TOKEN, DSN del catálogo
webhook: external_services/agent_client.py, messages.py
```

Convención: nombres de archivo y de funciones en inglés; docstrings,
descripciones y prompts en español.

**Nombres de tools.** Las del expediente quedan en español —`adjuntar_evidencia`,
`obtener_cumplimiento`— porque son vocabulario del dominio y el modelo las lee
como parte del prompt, junto a las palabras que usa el productor. Las 4 del
catálogo quedan en inglés —`list_tables`, `get_schema`, `check_query`,
`run_query`— porque no son dominio sino SQL.

### Se borra

`core/bq_tools.py`, `core/prompts/*/bq.md`, `core/prompts/*/bq_description.md`,
`tests/test_bq_tools.py`, la dependencia `google-cloud-bigquery`, y las variables
`BIGQUERY_DATASET`, `BQ_MAX_BYTES`, `BQ_MAX_ROWS`.

## 7. Qué queda obsoleto del documento de agosto

`docs/architecture/2026-08-08-arquitectura-agente-supabase.md` sigue vigente en
lo esencial —la capa `/api/agent/*`, la impersonación en las RPC, un `core/`
compartido— pero dos cosas no:

1. *"Sale BigQuery: el sub-agente text2sql se reemplaza por tools que llaman a
   `/api/agent/*`."* El expediente **no reemplaza** al text2sql: no sabe nada del
   catálogo. Lo que reemplaza a BigQuery es el mismo text2sql apuntado a
   Postgres. El documento mezcló dos decisiones.
2. *"El `producer_user_id` viaja en el session state de ADK."* Va en `user_id`
   (§4).

## 8. Errores

Las tools nunca levantan excepción hacia el modelo: devuelven `{ok, error}`, que
es el contrato que `OkContractRetryPlugin` ya entiende.

Con una excepción deliberada, aprendida midiendo el prototipo: **la ambigüedad de
alcance no es un error**. Cuando `/api/agent/*` responde `{ambiguous, kind,
candidates[]}` —dos empresas, tres instalaciones, un código en los dos
estándares— la tool devuelve `ok: True` con los candidatos. Si devolviera
`ok: False`, el plugin gastaría reintentos en algo que sólo una persona puede
resolver.

## 9. Pruebas

Lo determinista, en `pytest`, sin modelo ni red:

- `catalog_tools`: refuso de no-SELECT, tope de filas, timeout, el `{ok, error}`
- `record_tools`: que `producerUserId` **no** aparezca en el schema de ninguna
  tool; que se inyecte desde el `ToolContext`; que un `user_id` sin forma de uuid
  se niegue; el cuerpo exacto de cada llamada
- `agent.py`: que los tres sub-agentes estén registrados y que no quede ninguna
  tool de BigQuery

Lo del modelo, con el arnés que ya existe: un stub estricto de `/api/agent/*` que
replica la validación real (400 `ID_INVALID`, 404, ambigüedad 200 sin envolver) y
escenarios con repeticiones. Midiendo el prototipo así aparecieron seis defectos
que ninguna revisión de código habría encontrado — entre ellos que el agente
inventaba ids y que confirmaba una baja legal sin registrarla.

**El riesgo a medir primero es el enrutamiento.** Hoy el root elige entre dos
sub-agentes con una regla de una línea cada uno. Con tres hay que comprobar que
una pregunta del productor sobre su propio plan va al expediente y no al
catálogo, y que una sobre el estándar en abstracto va al catálogo. Eso se mide,
no se supone.

## 10. Orden

1. La migración del rol en el repo del app (~15 líneas) y `catalog_tools.py`
   acá. Deja el agente con catálogo fresco y permite borrar BigQuery de
   inmediato.
2. Identidad en el webhook.
3. `record_tools.py` y el sub-agente EXPEDIENTE.
4. Medir el enrutamiento entre los tres.

Cada paso deja el agente funcionando.
