"""Deploy or update agent_aa and agent_pp on Vertex AI Agent Runtime.

Usage:
    uv run python agents/deploy.py --env npe        # or prd
"""
import argparse
import os
from importlib import import_module
from typing import Optional

import vertexai
from google.cloud import secretmanager
from vertexai import agent_engines

REQUIREMENTS = [
    "google-cloud-aiplatform[adk,agent_engines]>=1.135.0",
    "google-adk>=1.35.0,<2.0.0",
    "langchain-community",
    "langchain-google-vertexai",
    "langgraph",
    "sqlalchemy-bigquery",
    "google-cloud-bigquery-storage",
    "google-cloud-discoveryengine",
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
        "display_name": "Planificación de Producción",
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


def env_vars_for(agent_key: str) -> dict[str, str]:
    base = {k: os.environ[k] for k in RUNTIME_ENV_KEYS}
    return base | TELEMETRY_ENV


def find_existing(display_name: str) -> Optional[str]:
    for eng in agent_engines.list():
        if eng.display_name == display_name:
            return eng.resource_name
    return None


def write_secret(project: str, secret_id: str, value: str) -> None:
    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{project}"
    name = f"{parent}/secrets/{secret_id}"
    try:
        client.get_secret(request={"name": name})
    except Exception:
        client.create_secret(
            request={
                "parent": parent,
                "secret_id": secret_id,
                "secret": {"replication": {"automatic": {}}},
            }
        )
    client.add_secret_version(
        request={"parent": name, "payload": {"data": value.encode()}}
    )


def deploy_one(key: str, cfg: dict, project: str, sa: str) -> None:
    mod = import_module(cfg["app_module"])
    existing = find_existing(cfg["display_name"])
    kwargs = dict(
        agent_engine=mod.app,
        requirements=REQUIREMENTS,
        extra_packages=[cfg["module_path"]],
        display_name=cfg["display_name"],
        env_vars=env_vars_for(key),
        service_account=sa,
        min_instances=0,
        max_instances=3,
    )
    if existing:
        # update() is an instance method on AgentEngine, not a module-level
        # function — fetch the engine first, then call .update(**kwargs).
        engine = agent_engines.get(existing)
        engine = engine.update(**kwargs)
    else:
        engine = agent_engines.create(**kwargs)
    write_secret(project, cfg["secret_id"], engine.resource_name)
    print(f"{key}: {engine.resource_name}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--env", choices=["npe", "prd"], required=True)
    args = p.parse_args()
    project = f"agro-extension-digital-{args.env}"
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
