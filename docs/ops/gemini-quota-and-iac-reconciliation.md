# Gemini 3 quota (429) + reconciliación IaC de la puesta en prod

Dos cosas que quedaron de la puesta en producción del Agente WhatsApp (2026-10): el diagnóstico de la quota de Gemini 3, y el estado de infra-como-código de todo lo que se creó.

---

## 1. Quota de Gemini 3 / `429 RESOURCE_EXHAUSTED`

### Síntoma
Turnos del agente (texto **e** imágenes) que salen vacíos. En logs del Reasoning Engine:
```
google.genai.errors.ClientError: 429 RESOURCE_EXHAUSTED. 'Resource exhausted. Please try again later.'
```

### Qué se verificó (valores reales, proyecto `agro-extension-digital-prd`, endpoint `global`)
Leídos de la API de Service Usage (`consumerQuotaMetrics` de `aiplatform.googleapis.com`):

| Métrica (global) | `gemini-3.7-flash` | `gemini-3.5-flash` |
|---|---|---|
| `global_generate_content_requests_per_minute_per_project_per_base_model` | **sin bucket propio → default = ilimitado** | igual (default ilimitado) |
| `global_generate_content_input_tokens_per_minute_per_base_model` | 50.000.000 (y capa 5.000.000.000) | igual |
| `global_generate_content_output_tokens_per_minute_per_base_model` | **-1 (ilimitado)** | igual |

(Otros preview como `gemini-3.1-pro-preview` / `gemini-3.5-flash-cyber` sí tienen un cap explícito de 250 RPM, pero el `flash` normal no.)

### Conclusión
**No hay ninguna quota de proyecto que esté mordiendo** — los límites de proyecto para `gemini-3.7-flash`/`3.5-flash` en `global` están en ilimitado/altísimo. El `429` viene de la **capacidad COMPARTIDA del modelo preview** del lado de Google (dynamic shared quota), que **no se expone** en la API de quotas y **no se sube** con un "quota increase" self-service. Cambiar de 3.7 a 3.5 **no cambia el mecanismo** (mismo perfil de quota; ambos preview).

### Decisión
Se usa **Gemini 3** (`gemini-3.7-flash` root/catalog/record, `gemini-3.1-flash-lite` RAG, `GEMINI_LOCATION=global`). Un intento previo de bajar a GA 2.5 para esquivar el 429 se **revirtió** (PR #74 → #75) por decisión del owner: se prioriza la calidad de Gemini 3.

### Cómo eliminar el 429 manteniendo Gemini 3
1. **Provisioned Throughput** (recomendado): Console → *Vertex AI → Provisioned Throughput* → comprar GSUs para `gemini-3.7-flash`. Capacidad reservada = cero 429. Es el mecanismo diseñado para preview/alto volumen.
2. **Caso con Google / TAM** para subir el cap de capacidad del preview en el proyecto.
3. Esperar a **GA** del modelo (ahí obtiene quota de proyecto propia y aumentable).

Mientras tanto, el 429 es **intermitente** (no permanente): muchos turnos completan igual.

### Para volver a un modelo distinto
Es sólo cambiar las constantes en `agents/core/agent.py` (`ROOT_MODEL`/`CATALOG_MODEL`/`RECORD_MODEL`/`RAG_MODEL`) y `GEMINI_LOCATION` (env del deploy): `global` para 3.x preview, `us-central1` para GA 2.x; luego redeploy del Agent Engine (`scripts/deploy-agents-local.sh`).

---

## 2. Reconciliación IaC

Durante la puesta en prod, varios recursos se crearon por `gcloud`/CLI (el runner self-hosted de los workflows estaba offline y el `terragrunt apply` estaba bloqueado en el entorno de trabajo). Acá el inventario y qué falta para que el **state** de terraform matchee la realidad (si no, un `terragrunt apply` futuro choca con "already exists").

### A) En código Y aplicado por `gcloud` → requieren `terraform import` (drift de state)
El código de estos recursos ya está en `cicd/modules/backend/main.tf` (PRs #65/#73), pero se crearon fuera de terraform. Importarlos al state del stack `cicd/stacks/prd/backend`:

```bash
cd cicd/stacks/prd/backend
PROJ=agro-extension-digital-prd; BUCKET=${PROJ}-wsp-media

terragrunt import 'google_storage_bucket.wsp_media' "$BUCKET"
terragrunt import 'google_storage_bucket_iam_member.webhook_writes_media' \
  "b/$BUCKET roles/storage.objectCreator serviceAccount:agent-webhook-sa-prd@${PROJ}.iam.gserviceaccount.com"
terragrunt import 'google_storage_bucket_iam_member.runtime_reads_media["aa"]' \
  "b/$BUCKET roles/storage.objectViewer serviceAccount:agent-aa-runtime@${PROJ}.iam.gserviceaccount.com"
terragrunt import 'google_storage_bucket_iam_member.runtime_reads_media["pp"]' \
  "b/$BUCKET roles/storage.objectViewer serviceAccount:agent-pp-runtime@${PROJ}.iam.gserviceaccount.com"
```
Después, `terragrunt plan` debe dar **no changes** sobre estos recursos (confirma que el código == la realidad, sin drift).

> El `WSP_MEDIA_BUCKET` env del webhook Cloud Run también está en código (`main.tf`) pero se seteó por `gcloud run services update`. Se reconcilia solo en el próximo `terragrunt apply` del webhook (terraform lo re-pone igual; mismo valor). No necesita import.

### B) Out-of-band POR DISEÑO (convención del repo) → NO van como recurso terraform
Son secretos confidenciales. El repo los **lee** con `run_cmd(gcloud secrets ...)` en terragrunt (igual que `wsp-token-aa`, `whatsapp-app-secret-*`) y NO los crea en terraform, para no meter el valor en el state/vars. Creados a mano (vía `scripts/setup-agent-gcp.sh` / `rotate-agent-token.sh`):

| Secreto (Secret Manager, `-prd`) | Valor | Lo lee |
|---|---|---|
| `agent-service-token` | token de servicio app↔agente (= el de Vercel) | webhook (terragrunt run_cmd) + Agent Engine (deploy-agents.yml) |
| `ciruela-api-base` | `https://agro-extension-digital-app.vercel.app` | webhook + Agent Engine |
| `catalog-dsn` | DSN de `agent_catalog_reader` (pooler Supabase, user con sufijo `.ref`) | Agent Engine (deploy-agents.yml) |

Esto es intencional; documentado en el comentario del `runtime_config` / terragrunt. **Acción:** ninguna (quedan out-of-band). Si se decide gestionarlos por terraform, habría que agregarlos a `local.runtime_config_secrets` — pero eso pone el valor confidencial en el state, en contra de la convención actual.

### C) Gap de IAM a codificar (opcional pero recomendado)
El `secretAccessor` sobre los 3 secretos de (B) para las SAs runtime (`agent-aa/pp-runtime`) se concedió por `gcloud` (`setup-agent-gcp.sh`) y **no está en terraform** (el `runtime_reads_config` de `main.tf` sólo cubre los 6 `runtime_config_secrets` datastore/bigquery). Para que quede en código, extender ese binding —o agregar uno paralelo— que incluya `agent-service-token`, `ciruela-api-base`, `catalog-dsn`. (Hoy funciona porque el grant existe en vivo; falta codificarlo para reproducibilidad.)

### D) Operacional (env del Agent Engine, no es terraform)
- `GEMINI_LOCATION` (`global`) se inyecta al Agent Engine vía `deploy.py`/`deploy-agents-local.sh` (es `OPTIONAL_ENV_KEYS`), no por terraform. Para fijarlo reproducible sin depender del export del deploy, crear un secreto `gemini-location` (lo carga el loop de `deploy-agents.yml`) o cambiar el default en `agents/core/llm_global.py`.
- La imagen del webhook se despliega con `gcloud run services update --image` (runner offline); terraform la referencia como `:latest` (`gar_image_location_webhook`). Un `terragrunt apply` la reconcilia a `:latest`.

### Lado Ciruela (`agro_extension_digital_app`) — ya en código
- Rol `agent_catalog_reader`: migración forward `supabase/migrations/20260930000000_agent_catalog_reader_role.sql` (en código). Su **contraseña** se fija out-of-band en prod (no va en git) — por diseño.
- Env de Vercel (`AGENT_SERVICE_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `CIRUELA_API_BASE`): gestionadas en Vercel (no en este repo).

---

## Resumen de acciones pendientes para "todo en código, sin drift"
1. **`terraform import`** del bucket `wsp_media` + sus 3 IAM members (sección A) → state == código.
2. (Opcional) **codificar el IAM** `secretAccessor` de los 3 secretos para las runtime SAs (sección C).
3. (Opcional) **fijar `GEMINI_LOCATION`** como secreto/código (sección D).
4. Secretos confidenciales (sección B): **se quedan out-of-band** por convención — no hay acción.

Las corren quien administra el state de terraform (roberto); el `terragrunt apply`/`import` requiere acceso al backend GCS del state.
