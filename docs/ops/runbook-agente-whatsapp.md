# Runbook — Agente WhatsApp: lado GCP (este repo)

Cómo desplegar/mantener el Agente WhatsApp en GCP (`agro_extension_digital_project`). El lado app (rutas `/api/agent/*`, migraciones, rol de catálogo) está en `agro_extension_digital_app/docs/ops/runbook-agente-whatsapp.md`.

**Arquitectura:** dos deploys. (1) **Agent Engine** (Vertex AI Reasoning Engine) vía `agents/deploy.py`. (2) **Webhook** (Cloud Run `agent-webhook-{env}`). Ambos consumen la app Ciruela y el catálogo Postgres.

**Proyectos:** `agro-extension-digital-npe` (dev), `agro-extension-digital-prd` (prod). Región `us-central1`.

---

## Env vars / secretos (Secret Manager)

El código lee 3 obligatorias (`agents/core/record_tools.py`, `webhook-application/.../identity.py`, `agents/core/catalog_tools.py`):

| Env var | Secret (kebab-case) | Valor |
|---|---|---|
| `CIRUELA_API_BASE` | `ciruela-api-base` | `https://agro-extension-digital-app.vercel.app` |
| `AGENT_SERVICE_TOKEN` | `agent-service-token` | el mismo que está en Vercel Production |
| `CATALOG_DSN` | `catalog-dsn` | DSN del rol `agent_catalog_reader` (ver gotcha abajo) |

Las requeridas por `deploy.py` (`RUNTIME_ENV_KEYS`) son **8**: los 5 `datastore-*` + estas 3. **Ya no** usa `BIGQUERY_DATASET` (el catálogo pasó de BigQuery a Postgres).

### Crear/rotar los secretos — scripts
- **Token (Vercel + GCP):** `scripts/rotate-agent-token.sh` — genera uno nuevo y lo deja en Vercel Production + Secret Manager. Si rotás con el agente ya vivo, **re-deployá Vercel prod** (su build tiene el token baked).
- **Los 3 secretos + IAM + verificación del DSN:** `scripts/setup-agent-gcp.sh` — testea el `CATALOG_DSN` (con fallback automático al user `.ref`), crea los 3 secretos en prd, y concede IAM.

### ⚠️ Gotcha del `CATALOG_DSN` (pooler Supavisor)
El pooler exige el usuario con sufijo del ref:
```
postgresql://agent_catalog_reader.<ref>:<pw>@aws-0-us-west-2.pooler.supabase.com:5432/postgres?sslmode=require
```
(`<ref>` = `svznwftzdbfnxtjwgtfo` para prod). El `<pw>` se fija en el lado app (`ALTER ROLE agent_catalog_reader WITH PASSWORD ...`).

---

## IAM

El deploy de agentes (`.github/workflows/deploy-agents.yml`) lee los secretos **como las SAs runtime** `agent-aa-runtime` / `agent-pp-runtime` (no hay un deployer SA aparte — verificado: a ellas está concedido `datastore-aa-id`). El webhook los lee como `agent-webhook-sa-prd`. Conceder `roles/secretmanager.secretAccessor` sobre los 3 secretos a esas 3 SAs (lo hace `setup-agent-gcp.sh`).

---

## Deploy 1 — Agent Engine

**Normal (CI):** `deploy-agents.yml` es `workflow_dispatch` con input `environment` (npe/prd):
```bash
gh workflow run deploy-agents.yml --repo talukspa/agro_extension_digital_project --ref main -f environment=prd
```
> **Gotcha:** el workflow corre en un **runner self-hosted** (`runs-on: self-hosted`). Si no está online, los runs quedan **en cola para siempre** (no es approval). Verificá runners, o usá el fallback local.

**Fallback local (sin runner):** `scripts/deploy-agents-local.sh` — hace lo mismo desde tu máquina (owner con `gcloud` + `uv`): carga las 8 env vars de Secret Manager y corre `agents/deploy.py --env prd`.
```bash
./scripts/deploy-agents-local.sh          # default prd
```
Resultado esperado: `Agent Engine updated. Resource name: ...` para `agent_aa` y `agent_pp`.

---

## Deploy 2 — Webhook (Cloud Run)

**Normal:** `terragrunt apply` del stack:
```bash
cd cicd/stacks/prd/backend && terragrunt apply
```
El plan debe ser `0 to add, 1 to change, 0 to destroy` (agrega `env AGENT_SERVICE_TOKEN` + `CIRUELA_API_BASE` al servicio `agent-webhook-prd`).

**Alternativa (si no podés correr terragrunt):** setear las env vars directo:
```bash
gcloud run services update agent-webhook-prd --project=agro-extension-digital-prd --region=us-central1 \
  --update-secrets=AGENT_SERVICE_TOKEN=agent-service-token:latest \
  --update-env-vars=CIRUELA_API_BASE=https://agro-extension-digital-app.vercel.app
```
> ⚠️ Esto crea **drift de terraform** (el módulo quiere `AGENT_SERVICE_TOKEN` como valor baked, no secret-ref). El próximo `terragrunt apply` lo reconcilia (mismo valor efectivo), o actualizá el módulo para usar secret-ref.

---

## Verificación

```bash
# auth token GCP↔Vercel: resolve-identity con el token real -> NO 401 (400/404 de lógica)
TOK=$(gcloud secrets versions access latest --secret=agent-service-token --project=agro-extension-digital-prd)
curl -s -o /dev/null -w "con token: %{http_code}\n" -X POST \
  -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" -d '{"waId":"000"}' \
  https://agro-extension-digital-app.vercel.app/api/agent/resolve-identity   # 404 PRODUCER_NOT_FOUND
unset TOK

# e2e real: mensaje de WhatsApp de un productor registrado -> logs del webhook / Agent Engine
#   sin 401/500 contra /api/agent/*, y el catálogo devolviendo filas.
```

### Egress Agent Engine → Supabase
El único hop que no se prueba con curl: el Agent Engine (GCP) alcanzando el pooler de Supabase para el catálogo. El pooler es público (`sslmode=require`), así que normalmente no requiere VPC connector. Se confirma cuando el agente corre su primera query de catálogo (logs). Si falla por red, agregar egress/VPC connector.

---

## Referencias
- Plan completo (dos repos): en `agro_extension_digital_app/docs/superpowers/plans/2026-09-30-agente-whatsapp-produccion.md`
- Scripts: `scripts/rotate-agent-token.sh`, `scripts/setup-agent-gcp.sh`, `scripts/deploy-agents-local.sh`
- Deploy del engine: `agents/deploy.py` · Wiring: `.github/workflows/deploy-agents.yml`, `cicd/modules/backend/`
- Lado app: `agro_extension_digital_app/docs/ops/runbook-agente-whatsapp.md`
