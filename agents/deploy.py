"""Deploy or update agent_aa and agent_pp on Vertex AI Agent Runtime.

Usage:
    uv run python agents/deploy.py --env npe        # or prd
"""
import argparse
import os
from importlib import import_module
from typing import Optional

import vertexai
from google.api_core import exceptions as gax
from google.cloud import secretmanager
from vertexai import agent_engines

# Pinned to the versions resolved in agents/uv.lock so the deployed engine
# runs the exact dependency set we test against locally. KEEP THIS LIST IN
# SYNC with agents/pyproject.toml + agents/uv.lock — bump these pins whenever
# the lockfile is regenerated.
REQUIREMENTS = [
    "google-cloud-aiplatform[adk,agent_engines]==1.157.0",
    "google-adk==1.35.0",
    "google-cloud-bigquery==3.33.0",
    "google-cloud-discoveryengine==0.13.12",
]

AGENTS = {
    "agent_aa": {
        # module_path is relative to CWD at deploy time; the workflow + the
        # local run both invoke from agents/, so the package dir is just
        # the leaf name.
        "module_path": "agent_aa_app",
        "app_module": "agent_aa_app.agent_engine_app",
        "display_name": "Adecuación Agroindustrial",
        "secret_id": "engine-aa-resource-name",
    },
    "agent_pp": {
        "module_path": "agent_pp_app",
        "app_module": "agent_pp_app.agent_engine_app",
        "display_name": "Producción Primaria",
        "secret_id": "engine-pp-resource-name",
    },
}

RUNTIME_ENV_KEYS = [
    "DATASTORE_AA_ID", "DATASTORE_PP_ID", "DATASTORE_GUIDES_ID",
    "DATASTORE_FAQ_ID", "DATASTORE_CHILEPRUNES_CL_ID", "BIGQUERY_DATASET",
]

# Telemetry env vars required post-ADK 1.18 to actually export traces.
# See https://github.com/google/adk-python/issues/3498.
#
# OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT defaults to "false"
# because the WhatsApp message body usually contains PII (names, phone
# numbers, locations, business detail). Anyone with roles/logging.viewer
# on Cloud Trace would see verbatim user text. Operators can flip it to
# "true" per-env via OTEL_CAPTURE_MESSAGE_CONTENT before running deploy.py
# (e.g. on a debug-only deploy in npe), but it must stay off in prd.
TELEMETRY_ENV = {
    "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
    "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": os.environ.get(
        "OTEL_CAPTURE_MESSAGE_CONTENT", "false"
    ),
}


# Force the google-genai client onto Vertex AI. Carried over from the old
# Cloud Run deploy (deploy-agent.sh set GOOGLE_GENAI_USE_VERTEXAI=TRUE);
# defensive, since every model already constructs genai.Client(vertexai=True).
STATIC_ENV = {"GOOGLE_GENAI_USE_VERTEXAI": "true"}


def env_vars_for(agent_key: str) -> dict[str, str]:
    # Do NOT set GOOGLE_CLOUD_PROJECT / GOOGLE_CLOUD_LOCATION here: Agent Engine
    # reserves those names and rejects create() if they appear in
    # deployment_spec.env ("Environment variable name '...' is reserved"). The
    # runtime injects them automatically — which is exactly what tools.py /
    # llm_global.py read via os.environ at runtime. (An earlier change shipped
    # GOOGLE_CLOUD_PROJECT explicitly; that broke real deploys, so it's gone.)
    base = {k: os.environ[k] for k in RUNTIME_ENV_KEYS}
    return base | STATIC_ENV | TELEMETRY_ENV


def read_secret(project: str, secret_id: str) -> Optional[str]:
    """Return the latest value stored in ``secret_id``, or None if missing.

    None means either the secret does not exist or it has no accessible
    version yet — both are treated by the caller as "no engine to update".
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project}/secrets/{secret_id}/versions/latest"
    try:
        resp = client.access_secret_version(request={"name": name})
    except (gax.NotFound, gax.FailedPrecondition):
        # NotFound: secret or version absent. FailedPrecondition: the latest
        # version is DISABLED/DESTROYED — e.g. an operator disabled it to force
        # a clean redeploy (see the rollback runbook). Both mean "no engine to
        # update" → the caller recreates.
        return None
    return resp.payload.data.decode()


def write_secret(project: str, secret_id: str, value: str) -> None:
    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{project}"
    name = f"{parent}/secrets/{secret_id}"
    try:
        client.get_secret(request={"name": name})
    except gax.NotFound:
        client.create_secret(
            request={
                "parent": parent,
                "secret_id": secret_id,
                "secret": {"replication": {"automatic": {}}},
            }
        )
    else:
        # Secret already exists — avoid version sprawl by skipping the write
        # when the latest version already holds this exact value.
        try:
            latest = client.access_secret_version(
                request={"name": f"{name}/versions/latest"}
            )
            if latest.payload.data.decode() == value:
                return
        except (gax.NotFound, gax.FailedPrecondition):
            pass  # no accessible version yet (absent, or latest disabled/destroyed)
    client.add_secret_version(
        request={"parent": name, "payload": {"data": value.encode()}}
    )


def deploy_one(key: str, cfg: dict, project: str, sa: str) -> None:
    mod = import_module(cfg["app_module"])
    kwargs = dict(
        agent_engine=mod.app,
        requirements=REQUIREMENTS,
        # "core" must ship alongside the per-agent shim: without it every
        # engine import fails AT RUNTIME on the deployed engine, while local
        # tests still pass because core/ is on the local path. Task 11's
        # deployed smoke test is the only thing that catches this.
        extra_packages=[cfg["module_path"], "core"],
        display_name=cfg["display_name"],
        env_vars=env_vars_for(key),
        service_account=sa,
        min_instances=0,
        max_instances=3,
    )
    # Idempotency is keyed off the stored resource name (not the mutable
    # display_name): read it from Secret Manager and update that engine.
    resource_name = read_secret(project, cfg["secret_id"])
    engine = None
    if resource_name:
        try:
            engine = agent_engines.get(resource_name)
        except gax.NotFound:
            # Secret pointed at an engine that no longer exists — recreate.
            engine = None
    if engine is not None:
        # update() is an instance method on AgentEngine, not a module-level
        # function — call .update(**kwargs) on the fetched engine.
        engine = engine.update(**kwargs)
    else:
        engine = agent_engines.create(**kwargs)
    write_secret(project, cfg["secret_id"], engine.resource_name)
    print(f"{key}: {engine.resource_name}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--env", choices=["npe", "prd"], required=True)
    args = p.parse_args()
    # Fail fast with a clear message if the runtime config env vars (loaded from
    # Secret Manager by deploy-agents.yml) are missing — otherwise the first
    # engine could deploy and the second abort with an opaque KeyError, leaving
    # the webhook half-migrated.
    missing = [k for k in RUNTIME_ENV_KEYS if not os.environ.get(k)]
    if missing:
        raise SystemExit(
            f"Missing required runtime env vars: {', '.join(missing)}. "
            "Did the 'Load runtime env vars from Secret Manager' step run?"
        )
    project = f"agro-extension-digital-{args.env}"
    # The agent modules bake their datastore/RAG resource names from
    # GOOGLE_CLOUD_PROJECT at import time (agent_*_app/agent.py:_datastore),
    # while the deploy target is derived independently from --env. If the two
    # disagree we'd ship an engine into `project` whose RAG paths point at a
    # different project (cross-project leak / PermissionDenied at query time).
    # Fail fast on a mismatch; otherwise pin the var to the target so a manual
    # run with it unset can't KeyError on import either.
    env_project = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if env_project and env_project != project:
        raise SystemExit(
            f"GOOGLE_CLOUD_PROJECT ({env_project!r}) does not match the --env "
            f"target project ({project!r}). Refusing to deploy an engine whose "
            "datastore/RAG paths would point at a different project."
        )
    os.environ["GOOGLE_CLOUD_PROJECT"] = project
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    bucket = f"gs://{project}-agent-engine-staging"
    vertexai.init(project=project, location=location, staging_bucket=bucket)
    sa_for = {
        "agent_aa": f"agent-aa-runtime@{project}.iam.gserviceaccount.com",
        "agent_pp": f"agent-pp-runtime@{project}.iam.gserviceaccount.com",
    }
    for key, cfg in AGENTS.items():
        deploy_one(key, cfg, project, sa_for[key])


if __name__ == "__main__":
    main()
