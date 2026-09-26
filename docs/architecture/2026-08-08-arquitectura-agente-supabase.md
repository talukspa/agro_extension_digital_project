# Súper-arquitectura consolidada: Agente WhatsApp + Supabase como fuente única

> Consolida las discusiones **#44** (refactor `agents/` → `core/`, ADK 2.x, planner, calidad) y **#50** (Agente PP en WhatsApp, CU-WA-00…08) bajo una decisión de plataforma de datos: **`agro_extension_digital_app` (Supabase/Postgres) es la fuente única de verdad. Se elimina BigQuery del camino del agente. Los RAG se mantienen en Vertex AI Search.**
>
> Fecha: 2026-08-08 · Estado: propuesta de arquitectura · Reemplaza las "decisiones abiertas" de fuente de datos en #44 y #50.

---

## 0. TL;DR

1. **Dos repos, una frontera limpia.** `agro_extension_digital_project` aloja el **agente + webhook**. `agro_extension_digital_app` aloja la **plataforma de datos (Supabase/Postgres) y la I/O saliente**. Se integran en el borde HTTP/Supabase, no compartiendo código.
2. **Sale BigQuery.** El sub-agente text2sql sobre BQ se reemplaza por **tools que llaman a la capa `/api/agent/*` del app**. El expediente vivo del productor está en Postgres, no en BQ.
3. **Los RAG no se tocan.** Los 4 datastores de Vertex AI Search (estándar AA/PP, guías, FAQ, chileprunes.cl) siguen resolviendo el conocimiento normativo. El plan de calidad RAG de #44 sobrevive intacto.
4. **El aislamiento entre productores lo impone el app, no el prompt ni el agente.** El agente no mintea JWT ni sostiene `service_role`: llama a `/api/agent/*` con un token de servicio pasando el `producer_user_id` resuelto; cada RPC `agent_*` valida acceso con `get_user_business_ids()`. (Decisión P0.5 — §3.1.)
5. **Buena parte de #50 ya existe en el app** (`users.phone_number`, `notifications`, `survey_evidence`, `question_messages`, `lib/services/whatsapp.ts`). El trabajo es **integrar** vía `/api/agent/*`, no reconstruir.

---

## 1. Estado real de los datos (verificado en código)

| Dominio | Dónde vive HOY | Rol en la arquitectura objetivo |
|---|---|---|
| Expediente del productor (negocios, instalaciones, planes, acciones, respuestas, cumplimiento, evidencia, notificaciones, chat auditor↔productor) | **`agro_extension_digital_app` → Supabase/Postgres** (esquema `public`, expuesto vía PostgREST `api`, RLS por JWT) | **Fuente única de verdad.** Todas las lecturas/escrituras del agente. |
| Conocimiento normativo (texto del estándar, guías, FAQ, sitio externo) | **Vertex AI Search** (4 datastores) | Se mantiene. Recuperación semántica. |
| `frontend/` sobre Firestore, `agents/` sobre BigQuery, `data_model/*.json` | Este repo (stack legado/paralelo) | **Se deprecan del camino del agente.** No son fuente de verdad. |

### Tablas Postgres relevantes (esquema `public`)

`businesses`, `business_installations`, `business_team_members`, `users` (con `phone_number`, `is_phone_verified`, `auth_method`), `standards`, `questions`, `certification_criteria`, `certification_processes`, `process_enrollments`, `survey_responses`, `survey_answers` (`standard_code`, `is_compliant`, `answer_score`), `survey_evidence` (`file_path`, `is_verified`, `verified_by`), `implementation_plans` (`progress_percentage`, `baseline_scores`), `implementation_plan_actions` (`question_code`, `verification_method`, `training_resources` jsonb, `due_date`, `completion_evidence`, `evidence_file_paths`), `question_messages` (chat auditor↔productor, `sender_type`), `notifications`, `legal_acceptances` (consentimiento), `action_status_history`, `whatsapp_verifications` (OTP: `otp_code`, `status`, `registration_token`, `expires_at`).

### Lo que #50 proponía construir y **ya existe** en el app

| Capacidad #50 | Ya existe en el app | Reusabilidad real (tras contraste con código) |
|---|---|---|
| CU-WA-00 vinculación `wa_id`→usuario | `users.phone_number`/`is_phone_verified`; `whatsapp_verifications` (OTP) | **PARCIAL.** El link persistente es `users.phone_number` (formato E.164 `+569…`), **no** `whatsapp_verifications` (tabla efímera pending→verified→consumed, sin `user_id`, RLS `USING false` para authenticated). El OTP se puede reusar como *mecanismo* de un flujo de pairing nuevo, no como store del vínculo. **Ojo formato:** `wa_id` viene en dígitos `569…` sin `+` → hay que normalizar antes de buscar. Ver §3. |
| CU-WA-05 evidencia | `survey_evidence` + Supabase Storage + `evidence/notify-uploaded` | **SÍ** para el modelo/bucket. La escritura hoy es **insert directo** (navegador → Storage + `.insert()`), no vía RPC. La ruta `notify-uploaded` exige sesión de usuario autenticado (no server-to-server). Ver §5.3. |
| CU-WA-06/07 notificaciones + plantillas Meta | `notifications` + `lib/notifications/service.ts`; primitiva `lib/services/whatsapp.ts` | **PARCIAL.** La ruta `app/api/whatsapp/send-template` está **admin-gated** (sesión Supabase, rol admin/super_admin) — **no** invocable server-to-server. La primitiva reusable es `lib/services/whatsapp.ts`. Falta un endpoint de salida para el agente. Ver §5.4. |
| Escalamiento a humano (decisión abierta 5) | `question_messages` + `lib/notifications/chat-recipients.ts` | SÍ (tabla + recipients). Escritura sujeta a RLS del usuario. |
| CU-WA-03 capacitación ↔ acción | `implementation_plan_actions.training_resources` (jsonb) | SÍ. |
| CU-WA-04 estado del plan | `implementation_plans` + `implementation_plan_actions` | SÍ como tablas. **No existe** RPC `get_plan_status` (era inventado): se lee por SELECT directo (RLS aplica) o se crea una RPC. Ver §5.2. |
| Consentimiento (RN-5) | `legal_acceptances` | SÍ. |

> **Correcciones tras contraste con código (2026-08-08).** Las siguientes suposiciones del borrador resultaron **incorrectas** y ya están corregidas abajo:
> 1. *"whatsapp_verifications resuelve la vinculación."* → No: es OTP efímero sin `user_id`. El link es `users.phone_number` (E.164), con desajuste de formato vs `wa_id`.
> 2. *"El Custom Access Token Hook inyecta claims de negocio que RLS usa."* → No: el hook inyecta **solo `user_role`**. El aislamiento por negocio es vía `auth.uid()` + `get_user_business_ids()` (joins a `business_team_members`/`businesses.owner_id`). ⇒ el JWT debe tener `sub` = **el `auth.users.id` real** del productor.
> 3. *"Mintear un JWT por usuario desde Python es directo."* → **No soportado out-of-the-box**: no hay `SUPABASE_JWT_SECRET` expuesto; GoTrue es el único emisor. Es el **riesgo técnico #1**. Ver §3.1.
> 4. *"El agente lee vía RPC del esquema `api` (`/rest/v1/rpc`)."* → El esquema `api` está **vacío**; PostgREST expone `public` + `graphql_public` (`config.toml`). Las RPC reales viven en `public`.
> 5. *"Reusar RPC `reportes_*`/`derive_scoring_*`."* → Nombres reales: `cm_reportes_stats(p_business_id, p_installation_id, p_season)`, `derive_achieved_year(p_response_id)`, `derive_category_breakdown(p_response_id)`. Son **`SECURITY DEFINER` (bypassan RLS)** y reciben `business_id`/`response_id` por parámetro ⇒ **el aislamiento NO es automático** para esas RPC. Ver §5.2.
> 6. *"Reusar `send-template` para salida."* → Admin-gated; no server-to-server. Ver §5.4.

**Única brecha real de datos:** CU-WA-08 (registro de labores) no tiene tabla destino en Postgres. Ver §7.

---

## 2. Súper-arquitectura

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Productor (WhatsApp)                                                           │
└───────────────┬──────────────────────────────────────────────▲───────────────┘
                │ texto / audio / imagen / documento            │ respuestas + notificaciones
                ▼                                               │
┌──────────────────────────────────────────────────────────────┴───────────────┐
│ REPO: agro_extension_digital_project                                          │
│                                                                               │
│  webhook-application/  (FastAPI, Cloud Run)                                   │
│   ├─ ACK inmediato + proceso en background                                    │
│   ├─ IDENTITY RESOLVER  ─────────────►  Supabase (service_role, solo acá):     │
│   │    wa_id → E.164 → users.phone_number verificado → producer_user_id        │
│   ├─ media pipeline (download, transcribe, validate)                          │
│   └─ markdown sanitizer (post-proceso salida)                                 │
│                                                                               │
│  agents/  (ADK, Vertex AI Agent Runtime)                                      │
│   core/  (paquete compartido AA/PP)                                           │
│    ├─ root LlmAgent  +  BuiltInPlanner (routing)                              │
│    │    ├─ sub-agente RAG      → VertexAiSearchTool ×4  (NORMATIVA)           │
│    │    └─ sub-agente EXPEDIENTE → agent_api (cliente HTTP)  (DATO PRODUCTOR)  │
│    └─ prompts/ (shared_rules, identity, scope, few-shot)                      │
└───────────────┬───────────────────────────────────┬──────────────────────────┘
     RAG (lectura)│           /api/agent/* (Bearer AGENT_SERVICE_TOKEN,           │
                  │            body: producer_user_id) ── lectura + escritura ──  │
                  ▼                                   ▼
┌─────────────────────────┐   ┌──────────────────────────────────────────────────┐
│ Vertex AI Search        │   │ REPO: agro_extension_digital_app (Supabase+Next)  │
│ · estándar AA/PP        │   │  /api/agent/*  (token de servicio, NO sesión)     │
│ · guías                 │   │    └─ RPC agent_*(p_user_id): impersona claim sub │
│ · FAQ                   │   │       → get_user_business_ids() → query acotada    │
│ · chileprunes.cl        │   │  Postgres public.*  ·  Storage survey-evidence     │
└─────────────────────────┘   │  lib/services/whatsapp.ts · lib/notifications      │
                              └──────────────────────────────────────────────────┘
                                          ▲
                                          │ triggers salientes (comentario auditor,
                                          │ visita, vencimiento, cambio de nivel)
                              ┌───────────┴───────────┐
                              │ Plataforma (app) →     │
                              │ POST /notify (webhook) │  ← CU-WA-06/07
                              └────────────────────────┘
```

### Principios de la frontera

1. **El agente nunca toca BigQuery ni Firestore.** Solo Vertex AI Search (normativa) y la capa `/api/agent/*` (expediente).
2. **El aislamiento vive en el app, no en el agente.** El filtro por negocio no se "confía" al prompt ni al agente: cada RPC `agent_*` lo impone con `get_user_business_ids()`. El agente solo pasa el `producer_user_id` resuelto.
3. **La I/O saliente se reusa del app.** El agente no reimplementa envío de plantillas Meta ni notificaciones: pasa por `/api/agent/send` sobre `lib/services/whatsapp.ts`.
4. **Un solo `core/` compartido AA/PP** (de #44): las tools son idénticas para ambos estándares; se parametrizan por `main_datastore_env` (RAG) y por el estándar resuelto (Supabase).

---

## 3. Modelo de integración con Supabase

### 3.1 Autenticación e aislamiento (RESUELTO — capa de servicio del app)

**Decisión (P0.5 cerrada): el agente NO se autentica contra Supabase directamente.** No mintea JWT de usuario ni sostiene la `service_role` key. En su lugar, el app expone una **capa de servicio dedicada `/api/agent/*`**, autenticada por un **token de servicio**, que recibe el `producer_user_id` ya resuelto y **hace el chequeo de acceso adentro**, reusando los helpers RLS existentes. El aislamiento vive en código auditado del app, no en "que el agente consiga el token correcto".

**Por qué (verificado, ver §12):** (a) GoTrue es el único emisor de JWT y no hay forma limpia de emitir un token de usuario sin su contraseña; (b) la salida (WhatsApp/notificaciones) y la escritura validada de evidencia **pasan sí o sí por TS del app**, así que igual hace falta una superficie del app; (c) darle `service_role` al agente Python sería el peor blast radius. La capa `/api/agent/*` resuelve las tres de una.

```
wa_id (dígitos, sin +)
  │  1. Identity resolver (webhook)  — normalizar wa_id → E.164 (+56…)
  ▼
users WHERE phone_number = <E.164> AND is_phone_verified   →  producer_user_id (auth.users.id)
  │      (whatsapp_verifications NO sirve de link: efímero, sin user_id, RLS USING false)
  │  2. producer_user_id viaja en el session state de ADK
  ▼
Tool del agente (cliente HTTP)  → POST /api/agent/*  (Bearer AGENT_SERVICE_TOKEN)
  │  3. el app autentica el token de servicio (timingSafeEqual)
  ▼
RPC SECURITY DEFINER agent_*(p_user_id) → inyecta claim sub=p_user_id →
  reusa get_user_business_ids() → query acotada al negocio del productor
  ▼
Solo el expediente del negocio del que ese usuario es dueño/miembro.
```

- **Sin vínculo verificado → el webhook no manda `producer_user_id` → el agente solo puede enrolar.** Materializa RN-3.
- **`service_role` vive SOLO en el app** (dentro de `/api/agent/*`), nunca en el agente Python ni en el webhook conversacional.
- **El agente Python no tiene cliente Supabase.** Sus tools son clientes HTTP delgados contra `/api/agent/*` (ver §5).

**El truco de aislamiento DRY:** una RPC `SECURITY DEFINER` inyecta el claim `sub` en la transacción, de modo que `auth.uid()` devuelve el productor y **los helpers existentes (`get_user_business_ids()`, `can_access_business()`) funcionan sin cambios** — no se reimplementa la lógica owner/team-member:

```sql
CREATE FUNCTION public.agent_get_plan_status(p_user_id uuid)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path=public AS $$
BEGIN
  PERFORM set_config('request.jwt.claims',
    json_build_object('sub', p_user_id, 'role','authenticated')::text, true);
  RETURN (SELECT to_jsonb(p) FROM (
    SELECT ip.id, ip.progress_percentage, ip.completed_actions, ip.total_actions
    FROM implementation_plans ip
    WHERE ip.is_active
      AND ip.business_id IN (SELECT get_user_business_ids())   -- helper existente
  ) p);
END; $$;
```

### 3.2 Superficie de acceso (corregido)

- **Toda operación del agente = una ruta `/api/agent/*` nombrada.** No hay SQL libre ni PostgREST directo desde el agente. El contrato de endpoints está en §12.
- **Lecturas** → RPC `agent_*(p_user_id)` con el patrón de arriba (impersonación + `get_user_business_ids()`). Las RPC de reporte existentes (`cm_reportes_stats`, `derive_achieved_year`, `derive_category_breakdown`) son `SECURITY DEFINER` y reciben `business_id`/`response_id` por parámetro; se llaman **solo desde dentro** de una `agent_*` que ya validó el acceso, nunca con ids crudos del modelo.
- **`get_plan_status` no existe** como RPC pública (era inventado): se materializa como `agent_get_plan_status` (arriba).
- **Escrituras** → ruta `/api/agent/evidence` que valida (MIME/50 MB) y hace el insert con `service_role` **tras** confirmar acceso; replica la validación que hoy hace el frontend. El agente nunca inserta directo.
- **Esquema:** las RPC viven en `public` (PostgREST expone `public`, no `api` que está vacío) — pero el agente ni siquiera las toca por PostgREST; entra por `/api/agent/*`.

---

## 4. Contrato de datos: Postgres vs RAG

Regla de oro para el root agent al sintetizar:

| Pregunta del productor | Fuente | Por qué |
|---|---|---|
| "¿Cuál es mi avance / mis acciones pendientes / mi cumplimiento?" | **Supabase** | Dato transaccional del expediente. |
| "¿Qué código de pregunta es / en qué nivel estoy?" | **Supabase** | `question_code`, `standard_code`, `answer_score` viven en Postgres. **CU-WA-01 "citar el código" es Postgres, no RAG.** |
| "¿Qué exige el estándar sobre X / cómo cumplo esta acción?" | **RAG** | Interpretación narrativa del estándar. |
| "¿Qué guía/curso corresponde a esta acción?" | **Postgres selecciona (`training_resources`) + RAG recupera contenido** | Complementario. |
| "¿Cómo es el proceso de certificación?" | **RAG** (+ contexto de etapa desde Postgres) | Normativa + personalización. |

**Sincronización a vigilar:** el estándar existe estructurado en Postgres (`questions`, `seed_standards.sql`) y como documento en el datastore RAG. Postgres manda para lo normativo-estructurado (códigos, scoring, validaciones); RAG para lo narrativo. No duplicar el mismo hecho como fuente de verdad en ambos.

**Consolidación futura (fuera de alcance):** pgvector en Supabase podría absorber el RAG y eliminar Vertex AI Search, unificando todo en una plataforma. Se descarta por ahora — Vertex AI Search aporta chunking/ranking/grounding gestionados y el datastore web (chileprunes.cl) no encaja en Postgres. Decisión aparte.

---

## 5. Catálogo de tools

Ubicación: `agents/core/`. Los módulos nuevos reemplazan `bq_tools.py`. **El agente NO tiene cliente Supabase**: cada tool es un cliente HTTP delgado contra la capa `/api/agent/*` del app (§3.1). Todas las tools:
- toman el **`producer_user_id` del `ToolContext`/session state** (no como argumento del modelo) y lo mandan en el body;
- devuelven `{"ok": bool, "error": str | None, ...}` (nunca levantan — el modelo se recupera con el loop error→fix→retry del prompt);
- confían el aislamiento al app; el `business_id`/`user_id` **no** son argumentos manipulables por el modelo.

### 5.1 `core/agent_api.py` — cliente HTTP de la capa de servicio

```python
# Único punto de acceso al app. Sin service_role, sin JWT de usuario, sin Supabase.
def _call(ctx: ToolContext, path: str, payload: dict) -> dict:
    r = httpx.post(
        f"{APP_AGENT_URL}{path}",
        headers={"Authorization": f"Bearer {AGENT_SERVICE_TOKEN}"},
        json={"producerUserId": ctx.state["producer_user_id"], **payload},
        timeout=APP_AGENT_TIMEOUT,
    )
    if r.status_code != 200:
        return {"ok": False, "error": f"{r.status_code}: {r.text[:200]}"}
    return r.json()
```

### 5.2 `core/expediente_tools.py` — lectura del expediente (reemplaza text2sql/BQ)

Cada tool llama a una ruta `/api/agent/*`, respaldada por una RPC `agent_*(p_user_id)` en el app (§3.1). El aislamiento lo garantiza esa RPC (impersonación + `get_user_business_ids()`); el agente no ve `business_id`.

| Tool | Ruta `/api/agent/*` | RPC en el app | CU |
|---|---|---|---|
| `get_business_profile` | `POST /business-profile` | `agent_get_business_profile(p_user_id)` | CU-WA-02 |
| `get_plan_status` | `POST /plan-status` | `agent_get_plan_status(p_user_id)` | CU-WA-04 |
| `list_pending_actions` | `POST /pending-actions` | `agent_list_pending_actions(p_user_id, p_limit)` | CU-WA-04 |
| `get_action` | `POST /action` | `agent_get_action(p_user_id, p_question_code)` | CU-WA-03/04 |
| `get_compliance` | `POST /compliance` | `agent_get_compliance(p_user_id, p_standard_code)` → envuelve `cm_reportes_stats` | CU-WA-04 |
| `get_certification_level` | `POST /certification-level` | `agent_get_certification_level(p_user_id)` → envuelve `derive_achieved_year` | CU-WA-07 |

```python
def get_plan_status(ctx: ToolContext) -> dict:
    """Avance del plan del negocio del productor vinculado.
    Aislamiento garantizado por la RPC agent_get_plan_status en el app;
    el business_id NO es argumento del modelo."""
    return _call(ctx, "/plan-status", {})          # producer_user_id lo agrega _call
```

### 5.3 `core/expediente_write_tools.py` — escritura (requiere confirmación)

Las escrituras también pasan por `/api/agent/*`; la ruta del app valida y hace el insert con `service_role` **tras** confirmar acceso. El webhook sube el binario a Storage `survey-evidence` (o lo manda a la ruta), y la ruta crea la fila.

| Tool | Ruta `/api/agent/*` | Destino | CU | Regla |
|---|---|---|---|---|
| `stage_evidence` | `POST /evidence` | Storage `survey-evidence` + `survey_evidence` (`is_verified=false`) | CU-WA-05 | RN-1: siempre ligada a una acción; si no, pregunta. RN-4: `source="whatsapp_agent"`. La ruta valida MIME/tamaño y `verification_type` (§5.3.1). |
| `confirm_and_write_log` | `POST /labor-log` | tabla de labores (§7) | CU-WA-08 | Confirmación obligatoria antes de persistir (paso 4 del doc). |
| `send_message_to_auditor` | `POST /auditor-message` | `question_messages` (`sender_type="user"`) | escalamiento 3a | Deriva al chat humano. |

```python
def stage_evidence(ctx, question_code: str, media_ref: str,
                   file_name: str, mime_type: str, description: str = "") -> dict:
    """Sube evidencia (foto O documento) vía /api/agent/evidence.
    La ruta del app valida y crea survey_evidence no-verificado.
    NUNCA final: queda pending para el auditor."""
    return _call(ctx, "/evidence", {
        "questionCode": question_code, "mediaRef": media_ref,
        "fileName": file_name, "mimeType": mime_type, "description": description,
    })
```

### 5.3.1 Documentos como evidencia (requisito explícito)

Los productores necesitan adjuntar **documentos** (PDF, Word, Excel, CSV), no solo fotos. En la capa de datos ya está soportado; el trabajo es en el camino de WhatsApp.

**Restricciones reales (fuente de verdad, no el stack Firestore viejo):**

| Aspecto | Valor | Dónde se define |
|---|---|---|
| Tipos permitidos | `application/pdf`, `application/msword`, `…wordprocessingml.document`, `application/vnd.ms-excel`, `…spreadsheetml.sheet`, `text/csv`, imágenes (`jpeg/png/gif/webp/heic/heif`), video (`mp4/quicktime/x-msvideo`) | Bucket `survey-evidence.allowed_mime_types` + `ciruela-certificada/lib/evidence/file-types.ts` |
| Tamaño máximo | **50 MB** (no 10 MB) | `storage.buckets.file_size_limit` del bucket `survey-evidence` |
| Validación de servidor | El bucket `allowed_mime_types` la impone en Storage sin importar el cliente | migración `…survey_evidence_allow_photos_and_office.sql` |

**Diferencia con el web:** en el frontend la subida va **navegador → Storage directo** (el bucket es la validación). En WhatsApp, el archivo va **Meta → webhook → Storage**; el webhook debe **pre-validar** MIME y tamaño para dar un mensaje útil (flujo 5a) antes de que Storage rechace. La lista de MIME se replica desde `file-types.ts` (o se consulta), no se re-inventa. WhatsApp entrega el `document` con `filename` y `mime_type`; ambos se propagan a `stage_evidence`.

**Coincidencia con `verification_type`:** cada pregunta/acción declara `questions.verification_type` (`document | image | log`). Antes de subir, el agente compara el tipo entrante con el esperado:
- productor manda **documento** y la acción pide `document` → OK.
- productor manda **foto** y la acción pide `document` (o viceversa) → flujo 5a: el agente explica qué medio de verificación corresponde y no sube algo que el auditor rechazaría.

**Destino (decidido):** el flujo de evidencia por WhatsApp escribe **siempre en `survey_evidence`** — el medio de verificación ligado a una pregunta/acción. Es el objetivo de CU-WA-05 y el destino único de "subir un documento para la evidencia".

`business_documents` (documentos de empresa con ciclo `review_status: pending | needs_correction`) queda **fuera de alcance** del agente WhatsApp por ahora: es otro canal, con otra UX de revisión, y el agente no lo toca a menos que se defina un caso de uso propio más adelante.

### 5.4 `core/notify_tools.py` — I/O saliente (corregido)

La ruta `app/api/whatsapp/send-template` **no es reusable server-to-server**: está admin-gated (sesión Supabase + rol admin/super_admin). La primitiva real de envío es `lib/services/whatsapp.ts` (que el propio flujo OTP usa directo). Por tanto la salida del agente necesita **una vía nueva**, no reusar la ruta admin.

| Pieza | Qué hacer | CU |
|---|---|---|
| Envío de plantilla Meta | Ruta `/api/agent/send` (mismo token de servicio) que envuelve `lib/services/whatsapp.ts` (`sendWhatsAppTemplate`). No reusar `send-template` (admin-gated). | CU-WA-06/07 |
| Webhook entrante `POST /notify` | Nuevo, autenticado por token de servicio; lo dispara la plataforma (comentario auditor, visita, vencimiento, cambio de nivel). | CU-WA-06/07 |
| Notificación post-evidencia | La ruta `/api/agent/evidence` dispara la notificación al crear la fila (reusa `lib/notifications`), o vía trigger en `survey_evidence`. No depende de `notify-uploaded` (session-bound). | CU-WA-05 |

### 5.5 RAG — sin cambios

`VertexAiSearchTool` ×4 se mantiene. Solo se aplica el plan de calidad de #44 Commit 5 (citas `[fuente: …]`, few-shot de routing, curación de Memory Bank).

---

## 6. Cómo se integran las tools (mecánica end-to-end)

```
1. Meta → POST webhook            (webhook-application)
2. ACK inmediato; background:
3.   resolver identidad           wa_id → E.164 → users.phone_number verificado → producer_user_id
4.     sin vínculo → responder enrolamiento (OTP) y CORTAR
5.   procesar media               texto | audio→transcribe | imagen/documento→download+validar
                                    (documento: propagar filename+mime_type; validar contra
                                     survey-evidence.allowed_mime_types y 50 MB)
6.   create_agent_session(state={ "producer_user_id", "standard": "aa|pp", ... })  # sin JWT
7.   run agent:
        root (BuiltInPlanner) decide RAG vs Expediente vs ambos
          · RAG tools        → Vertex AI Search
          · Expediente tools → POST /api/agent/* (Bearer AGENT_SERVICE_TOKEN)
                                 → app: RPC agent_*(producer_user_id) → RLS vía impersonación
          · Write tools      → POST /api/agent/{evidence,labor-log,...}; no-final (pending auditor)
8.   sanitizar salida markdown→WhatsApp (post-proceso, regex)
9.   enviar respuesta; escrituras trazadas "Vía Agente WhatsApp"
```

**Cambio mínimo habilitante:** hoy `agent_client.py` manda un `state` hardcodeado. P2 lo reemplaza por `{producer_user_id, standard}`. El agente **no** necesita JWT ni cliente Supabase — el aislamiento vive en `/api/agent/*`.

---

## 7. CU-WA-08: diseño del registro de labores (brecha real)

No hay tabla de "labores" en Postgres. Opciones, en orden de preferencia:

1. **Nueva tabla `labor_logs`** en el app (migración Supabase): `id, business_id, installation_id, standard_code, question_code, payload jsonb, source ('whatsapp_audio'|'whatsapp_text'), status ('pending'), created_by, created_at`, con RLS análoga a `survey_evidence`. Alimenta una o varias acciones. Es lo más limpio y respeta el modelo del app.
2. Mapear a `survey_answers` + `action_status_history` si el "log" siempre corresponde a una respuesta/acción existente. Menos flexible para bitácora libre.

**Flujo (Fase 3):** transcribir → extracción estructurada contra el esquema del `standard_code` → **estado conversacional "pendiente de confirmación"** (no existe hoy en el webhook; se guarda en session state y debe resistir mensajes intercalados) → `confirm_and_write_log`. Nunca registra a medias (flujo 6b: si falta cuartel/producto/dosis, pregunta).

---

## 8. Plan por fases consolidado

Combina el eje "calidad del agente" (#44) con el eje "capacidad + plataforma" (#50). Cada fase ≈ un PR atómico, sobre `main`, **después** de que #43 mergee y soakée (Rodrigo R1).

| Fase | Contenido | Origen | Depende de |
|---|---|---|---|
| **P0 · core/ + sanitizer** | Refactor a `core/`, matar `LangGraphAgent`, sanitizer markdown. **Borra las 4 tools BQ** (no se endurecen: se reemplazan). ADK 1.35. | #44 Commit 1+4 (mod.) | #43 merged |
| **Pa · Capa `/api/agent/*` en el app** (repo `agro_extension_digital_app`) | Middleware de token de servicio (`timingSafeEqual`); RPC `agent_*(p_user_id)` con impersonación + `get_user_business_ids()` (§3.1, §12); rutas de lectura (§5.2). Resuelve P0.5 a favor de la capa de servicio. | nuevo (contraste) | — |
| **P1 · Read tools (agente)** | `core/agent_api.py` + `expediente_tools` (§5.2): clientes HTTP contra `/api/agent/*`. Reemplaza el sub-agente text2sql. Sin cliente Supabase en Python. | nuevo (este doc) | P0, Pa |
| **P2 · Identidad + vínculo** | Identity resolver en webhook: normalizar `wa_id`→E.164, buscar `users.phone_number` verificado → `producer_user_id`; persistir el vínculo (`whatsapp_verifications` es solo OTP, no link); reemplazar el stub de `state` por `{producer_user_id, standard}`; enrolamiento con OTP nuevo. | #50 Fase 0 (mod.) | P1 |
| **P3 · ADK 2.x bump** | Bump aislado, su propio merge boundary. Auditar `except Exception` vs retry 2.0. | #44 Commit 2 | P0 (indep. de P1/P2) |
| **P4 · Evidencia entrante (fotos + documentos)** | Ruta `/api/agent/evidence` en el app: valida MIME/50 MB contra `file-types.ts` + `verification_type` (§5.3.1) e inserta `survey_evidence` con `service_role`. Webhook: aceptar `image` **y** `document` (hoy rechazados; el modelo `WhatsAppDocumentContent` con `filename`/`mime` **ya existe**, solo falta enrutar). Notificación post-subida en la misma ruta o por trigger (no `notify-uploaded`). | #50 Fase 2 (mod.) | Pa, P2 |
| **P5 · Registro de labores** | Tabla `labor_logs` (§7), extracción estructurada, confirmación, `confirm_and_write_log`. Fix audio: `long_running_recognize`/Chirp. | #50 Fase 3 | P2 |
| **P6 · Planner + calidad RAG** | `BuiltInPlanner`, citas `[fuente:]`, few-shot, Memory Bank curado. **Eval harness primero.** | #44 Commit 3+5 | P0; eval harness |
| **P7 · Proactividad** | `POST /notify` autenticado por token de servicio; ruta `/api/agent/send` sobre `lib/services/whatsapp.ts` (no `send-template`, admin-gated); set de plantillas Meta. | #50 Fase 5 | Pa, P2 |

**Notas de secuencia:**
- **Pa vive en el repo `agro_extension_digital_app`, no en este.** Es prerequisito de P1/P4/P7 y cruza la frontera de repos: la coordinación entre equipos es parte del plan. Contrato en §12.
- El **eval harness va antes de P6**, no después (los cambios de calidad se mergean a ciegas sin él).
- P3 (bump 2.x) es independiente del eje de datos; puede correr en paralelo a P1/P2 pero con su propio boundary de merge.
- Instrumentar métricas (§métricas de #50) desde P1.

---

## 9. Qué cambia respecto de #44 y #50

**Sobrevive de #44 (independiente de la fuente de datos):** `core/` compartido, matar `LangGraphAgent`, sanitizer markdown, ADK 2.x, planner, **plan de calidad RAG completo**.

**Muere/se rehace de #44:** las 4 tools de BigQuery y el sub-agente text2sql → reemplazados por tools Supabase (§5). El endurecimiento de tools BQ (Commit 4) no aplica: no se endurece lo que se bota. La decisión "BQ→Supabase" precede a cualquier inversión en tools de datos.

**Se resuelven las decisiones abiertas de #50:**
1. Fuente de verdad → **Supabase/Postgres** (ni Firestore ni BQ).
2. Vinculación del número → **código de emparejamiento, ya existe** (`whatsapp_verifications`). Reusar, no crear `whatsapp_links`.
3. Un agente o dos → dos entradas (webhooks AA/PP), un `core/` compartido.
4. Plantillas Meta → administradas por el app; el agente las invoca.
5. Escalamiento → `question_messages` (canal existente).
6. Retención/consentimiento → `legal_acceptances` + política de media a definir.

---

## 10. Riesgos y decisiones a cerrar

1. **[RESUELTO — era el #1] Obtención del token de usuario.** GoTrue es el único emisor y no hay forma limpia de emitir token de usuario sin contraseña. **Decisión: capa de servicio `/api/agent/*`** (§3.1, §12) — el agente no mintea tokens ni sostiene `service_role`. Queda como trabajo, no como riesgo abierto.
2. **[confirmado] El hook solo inyecta `user_role`.** El aislamiento por negocio es `auth.uid()` + `get_user_business_ids()`. La capa `/api/agent/*` lo reusa vía impersonación (`set_config('request.jwt.claims', …)`) dentro de RPC `SECURITY DEFINER`.
3. **[confirmado] RPC de reporte `SECURITY DEFINER` bypassan RLS.** `cm_reportes_stats`/`derive_*` reciben `business_id`/`response_id` por parámetro; se llaman **solo desde dentro** de una `agent_*` que ya validó acceso, nunca con ids crudos del modelo (§3.2).
4. **[confirmado] Desajuste de formato de teléfono.** `users.phone_number` es E.164 (`+56…`); `wa_id` viene en dígitos (`56…`). Normalizar antes de la búsqueda o el vínculo nunca calza.
5. **[confirmado] `whatsapp_verifications` no es store de vínculo.** Efímera, sin `user_id`, RLS `USING false`. Reusable como mecanismo OTP; el vínculo persistente hay que resolverlo aparte.
6. **[confirmado] Salida server-to-server.** `send-template` es admin-gated y `notify-uploaded` es session-bound: ninguna es invocable por el agente. Hace falta un endpoint de servicio nuevo o envío directo a Meta (§5.4).
7. **[confirmado] Esquema `api` vacío.** PostgREST expone `public`; el agente pega a `public`, no a `api`.
8. **CU-WA-08 sin destino:** decidir `labor_logs` (nueva tabla) vs mapeo, antes de prometer la funcionalidad.
9. **Doble modelo de dominio entre repos:** declarar el app como fuente única y deprecar `data_model/*.json` + Firestore del project, o conviven dos verdades.
10. **Escrituras del agente:** ninguna final sin paso por auditor (`survey_evidence.is_verified=false`, `labor_logs.status='pending'`). Idealmente un test que lo garantice como invariante.
11. **Fuga de lectura menor:** política `businesses_public_search` deja a cualquier `authenticated` ver metadata de negocios activos+verificados (no el expediente). Confirmar que no filtra nada sensible para el token del agente.
12. **Latencia:** cada turn suma resolución de identidad + obtención/validación de token + posible RAG + SELECT/RPC. Medir contra la ventana de WhatsApp.

---

## 11. Variables de entorno nuevas

**Agente / webhook (este repo):**

| Var | Rol |
|---|---|
| `APP_AGENT_URL` | base de la capa `/api/agent/*` del app |
| `AGENT_SERVICE_TOKEN` | token de servicio para autenticar contra `/api/agent/*` (único secreto que sostiene el agente) |
| `APP_AGENT_TIMEOUT` | timeout HTTP de las tools |
| `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` | **solo webhook**, solo para resolver identidad (`users.phone_number`) y OTP de enrolamiento; nunca en las tools del agente |

**App (repo `agro_extension_digital_app`):**

| Var | Rol |
|---|---|
| `AGENT_SERVICE_TOKEN` | mismo valor; el middleware `/api/agent/*` lo compara con `timingSafeEqual` |
| `WHATSAPP_ACCESS_TOKEN` / `WHATSAPP_PHONE_NUMBER_ID` | ya existen; los usa `lib/services/whatsapp.ts` para `/api/agent/send` |

---

## 12. Contrato de la capa `/api/agent/*` (trabajo en el repo del app)

Namespace nuevo en `agro_extension_digital_app`, autenticado por `AGENT_SERVICE_TOKEN` (constante, `timingSafeEqual`), nunca por sesión de navegador. Todas reciben `producerUserId` y lo pasan a una RPC `agent_*(p_user_id)` que impersona vía `set_config('request.jwt.claims', …)` y reusa `get_user_business_ids()`.

**Middleware** (`lib/auth/require-agent-service.ts`): valida el token; rechaza 401 si no calza.

| Ruta | Body | RPC / servicio | Devuelve |
|---|---|---|---|
| `POST /api/agent/business-profile` | `{producerUserId}` | `agent_get_business_profile` | perfil + instalaciones |
| `POST /api/agent/plan-status` | `{producerUserId}` | `agent_get_plan_status` | avance del plan |
| `POST /api/agent/pending-actions` | `{producerUserId, limit?}` | `agent_list_pending_actions` | acciones pendientes |
| `POST /api/agent/action` | `{producerUserId, questionCode}` | `agent_get_action` | acción + `training_resources` |
| `POST /api/agent/compliance` | `{producerUserId, standardCode?}` | `agent_get_compliance` → `cm_reportes_stats` | cumplimiento |
| `POST /api/agent/certification-level` | `{producerUserId}` | `agent_get_certification_level` → `derive_achieved_year` | nivel proyectado |
| `POST /api/agent/evidence` | `{producerUserId, questionCode, mediaRef, fileName, mimeType, description}` | valida MIME/50 MB + insert `survey_evidence` (`is_verified=false`) + notifica | `{evidenceId, status}` |
| `POST /api/agent/labor-log` | `{producerUserId, standardCode, questionCode?, payload}` | insert `labor_logs` (`status='pending'`) | `{logId}` |
| `POST /api/agent/auditor-message` | `{producerUserId, responseId, text}` | insert `question_messages` (`sender_type='user'`) | `{messageId}` |
| `POST /api/agent/send` | `{producerUserId, templateName, parameters[]}` | `sendWhatsAppTemplate` (`lib/services/whatsapp.ts`) | `{messageId}` |

**Invariante de seguridad:** cada RPC `agent_*` valida acceso con `get_user_business_ids()` antes de leer/escribir; ninguna acepta `business_id` como argumento. Ideal: un test que falle si una ruta `/api/agent/*` toca datos fuera del negocio del `producerUserId`.

---

## Referencias

- Discusión **#44** — refactor `agents/` → `core/`, ADK 2.x, planner, calidad (+ review de RodrigoVasquez).
- Discusión **#50** — Agente PP en WhatsApp, CU-WA-00…08.
- `docs/superpowers/plans/2026-06-25-agents-core-refactor.md` — PR-A (core/ + sanitizer), base de P0.
- Repo `agro_extension_digital_app` — Supabase: `supabase/migrations/*` (RLS `get_user_business_ids`, `can_access_business`, hook `custom_access_token_hook`), `ciruela-certificada/lib/services/whatsapp.ts`, `lib/notifications/*`, `lib/evidence/file-types.ts`, `app/api/auth/register/*` (patrón GoTrue).
