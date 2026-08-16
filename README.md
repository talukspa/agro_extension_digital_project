# AgroExtensión Digital 🌱

Asistentes conversacionales por WhatsApp para extensión agrícola: dos agentes de IA especializados en la certificación de ciruela, servidos a través de un webhook de WhatsApp Cloud API.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-green)
![Vertex%20AI](https://img.shields.io/badge/Vertex%20AI-Agent%20Runtime-4285F4)
![Terraform](https://img.shields.io/badge/Terraform-1.5+-purple)

## 🏗️ Arquitectura

```
WhatsApp Cloud API
        │  POST /estandar_{aa,pp}_webhook  (firmado con X-Hub-Signature-256)
        ▼
  agent-webhook-{npe,prd}          ← Cloud Run (FastAPI)
        │  google-cloud-aiplatform SDK
        ▼
  reasoningEngines/{id}            ← Vertex AI Agent Runtime (ADK)
        │
        ├── Vertex AI Search        (5 datastores: aa, pp, guías, faq, chileprunes)
        └── BigQuery                (estandar_{aa,pp}, recursos_{aa,pp})
```

Los agentes **no** corren en Cloud Run. Viven en Vertex AI Agent Runtime como *reasoning engines*; el webhook los invoca por SDK y resuelve el `resource_name` desde Secret Manager (`engine-aa-resource-name` / `engine-pp-resource-name`), con caché TTL para tolerar rotaciones sin redeploy.

Ambientes: `agro-extension-digital-npe` (stack `dev`) y `agro-extension-digital-prd` (stack `prd`), ambos en `us-central1`.

## 📂 Estructura

| Directorio | Qué es |
|---|---|
| `agents/` | Los dos agentes ADK + `deploy.py`, que crea o actualiza los engines en Agent Runtime |
| `webhook-application/` | Webhook FastAPI de WhatsApp desplegado en Cloud Run |
| `cicd/` | IaC: `modules/` (Terraform) y `stacks/{dev,prd}/{backend,database}` (Terragrunt) |
| `scripts/local-deploy/` | Despliegue manual paso a paso, numerado en orden de ejecución |
| `docs/superpowers/` | Runbook de despliegue, planes y specs |

### `agents/`

Dos aplicaciones ADK con la misma forma (`agent.py`, `prompts.py`, `tools.py`, `agent_engine_app.py`):

- **`agent_aa_app/`** — *Adecuación Agroindustrial*
- **`agent_pp_app/`** — *Producción Primaria*

`deploy.py --env {npe|prd}` empaqueta cada app, la despliega con `min_instances=0, max_instances=3` bajo su propia service account (`agent-{aa,pp}-runtime@…`), y guarda el `resource_name` resultante en Secret Manager. La idempotencia se basa en ese secreto, no en el `display_name`: si existe, actualiza el engine; si no, lo crea.

Las versiones de dependencias están fijadas en `REQUIREMENTS` dentro de `deploy.py` y deben mantenerse en sincronía con `agents/pyproject.toml` + `agents/uv.lock`.

### `webhook-application/`

```
whatsapp_webhook/
├── api/webhooks.py        # Rutas + validación de firma X-Hub-Signature-256
├── external_services/     # Cliente de Agent Runtime, cliente de WhatsApp
├── models/                # Modelos de dominio Pydantic v2
├── utils/app_config.py    # Config desde variables de entorno
├── messages.py            # Orquestación: sesión → consulta al agente → respuesta
└── app.py                 # Factory de FastAPI
```

**Endpoints** (uno por agente, ambos en el mismo servicio):

| Método | Ruta | Para qué |
|---|---|---|
| `GET` | `/estandar_aa_webhook`, `/estandar_pp_webhook` | Handshake de suscripción de Meta (`hub.mode`, `hub.verify_token`, `hub.challenge`) |
| `POST` | `/estandar_aa_webhook`, `/estandar_pp_webhook` | Recepción de mensajes |
| `GET` | `/health` | Health check |

Un POST sin firma válida se rechaza con **403 antes** de agendar cualquier trabajo. La validación es *fail-closed*: si `WHATSAPP_APP_SECRET` no está seteado, se rechaza todo. Una vez validada la firma, WhatsApp nunca ve un 5xx (evita reintentos): los errores del handler se registran y se responde 200.

El `session_id` del agente es el número de WhatsApp del remitente, así que la conversación persiste entre mensajes.

## 🔐 Secretos

Cuatro secretos deben existir en Secret Manager **antes** del primer `terragrunt plan` — el stack los lee con `run_cmd` al *evaluar* la configuración, así que uno faltante es un fallo de plan, no un problema en runtime:

| Secreto | Para qué |
|---|---|
| `whatsapp-app-secret` | Clave HMAC de la firma entrante. Los números AA y PP cuelgan de la misma app de Meta, así que un solo secreto valida ambos endpoints |
| `webhook-verify-token` | El string del handshake GET |
| `wsp-token-aa`, `wsp-token-pp` | Access tokens de salida. Estos **sí** son por número: el token de uno da 401 contra el número del otro |

Créalos con `scripts/local-deploy/05-create-app-secrets.sh <env>`. Terraform crea el resto (`datastore-*`, `engine-*`, `bigquery-dataset`).

Los tres tipos de valor no son intercambiables: App Secret (HMAC entrante) ≠ access token (Bearer saliente) ≠ verify token (handshake).

## 🚀 Despliegue

El camino manual está en `scripts/local-deploy/`, numerado en orden. Cada script imprime el proyecto y el stack objetivo antes de tocar nada, y exige confirmación escrita para prd:

```bash
scripts/local-deploy/00-preflight.sh   dev   # verifica todo, no cambia nada
scripts/local-deploy/05-create-app-secrets.sh dev
scripts/local-deploy/10-build-push.sh  dev   # imagen del webhook
scripts/local-deploy/20-infra.sh       dev   # terragrunt plan / apply
scripts/local-deploy/30-agents.sh      dev   # deploy.py de los engines
scripts/local-deploy/40-redeploy-webhook.sh dev
```

Ojo con los tres nombres del mismo ambiente:

| stack dir | GCP project | `deploy.py --env` |
|---|---|---|
| `dev` | `agro-extension-digital-npe` | `npe` |
| `prd` | `agro-extension-digital-prd` | `prd` |

Las imágenes de contenedor viven en el proyecto **npe** para ambos ambientes. Nunca publiques en el registry de prd — nadie lo consume.

Para el procedimiento completo, incluyendo rollback, ver [`docs/superpowers/runbook-agent-runtime-deploy.md`](docs/superpowers/runbook-agent-runtime-deploy.md).

### GitHub Actions

| Workflow | Se dispara con |
|---|---|
| `ci.yml` | Pull requests y push a `main`/`develop` |
| `build-and-push.yml` | Push a `main`, ramas `feature/*` y tags `v*.*.*` |
| `deploy-agents.yml` | Manual (`workflow_dispatch`), elige `npe` o `prd` |
| `deploy.yaml` | Manual (`workflow_dispatch`) |

Los despliegues son manuales a propósito. Un dispatch a `prd` corre bajo el GitHub Environment `prd`, que puede configurarse con revisores obligatorios.

## 🛠️ Desarrollo

Requisitos: Python 3.12, [`uv`](https://docs.astral.sh/uv/), `gcloud` autenticado (incluyendo `gcloud auth application-default login`, que es aparte y es lo que usa `deploy.py`). Para infraestructura además `terraform` 1.5+ y `terragrunt` 0.78+. Hay un Dev Container en `.devcontainer/` con todo preinstalado.

```bash
# Webhook
cd webhook-application
uv sync
uv run --extra dev pytest -q

# Agents
cd agents
uv sync
uv run pytest -q
```

Terraform:

```bash
cd cicd/modules/backend
terraform init -backend=false
terraform test          # requiere terraform 1.6+; corre offline
```

Terragrunt se ejecuta desde el directorio de la unidad, no desde la raíz:

```bash
cd cicd/stacks/dev/backend
terragrunt plan
```

### Convenciones

- Pydantic v2 para toda validación de datos, type hints en todo el código nuevo.
- Commits convencionales: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `ci:`.
- Los tests acompañan al cambio en el mismo PR.

## 📊 Observabilidad

Todo va a Google Cloud Logging. El nivel se controla con `LOG_LEVEL` por ambiente (`DEBUG` en dev, `INFO` en prd).

```bash
# Errores del webhook
gcloud logging read \
  'resource.type="cloud_run_revision"
   AND resource.labels.service_name="agent-webhook-prd"
   AND severity>=ERROR' \
  --project=agro-extension-digital-prd --limit=20 --freshness=1h

# Logs de un engine
gcloud logging read \
  'resource.type="aiplatform.googleapis.com/ReasoningEngine"
   AND resource.labels.reasoning_engine_id="<id>"' \
  --project=agro-extension-digital-prd --limit=50 --freshness=1h
```

Los engines corren con `min_instances=0`. Ver el contenedor apagándose tras un período sin tráfico es scale-to-zero normal, no una caída — pero implica que el primer mensaje tras estar idle paga cold start (~44s medido), y por eso `AGENT_SESSION_TIMEOUT` está en 120s.

Telemetría OTEL habilitada vía `GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY`. La captura del contenido de los mensajes está **apagada** en prd a propósito: el cuerpo de un mensaje de WhatsApp suele traer PII (nombres, teléfonos, ubicaciones), y cualquiera con `roles/logging.viewer` vería el texto literal.

## 🔧 Troubleshooting

**Los mensajes de un agente dan 403 y nunca llegan.** Firma inválida. Si el log dice `No Meta App Secret configured`, falta la variable; si dice `signature validation failed`, el valor no coincide con el App Secret de Meta. El valor va incrustado en la revisión de Cloud Run, así que actualizar el secreto no basta: hay que aplicar terragrunt para generar una revisión nueva.

**El webhook responde pero el agente nunca contesta.** Mira los logs del engine. Un `InvalidArgument: 400 Reasoning Engine Execution failed` esconde el error real en el mensaje anidado.

**`terragrunt plan` falla al evaluar la config.** Falta alguno de los cuatro secretos preexistentes. Corre `00-preflight.sh`.

**Errores de autenticación en GCP.** `gcloud auth login` y `gcloud auth application-default login` son cosas distintas; `deploy.py` usa la segunda.

---

Repositorio: [talukspa/agro_extension_digital_project](https://github.com/talukspa/agro_extension_digital_project)
