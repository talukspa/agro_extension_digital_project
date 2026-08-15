"""Unit tests for agents/deploy.py pure helpers.

Network-touching paths (vertexai.init, agent_engines.create/list, Secret
Manager) are NOT tested here — they are covered by Phase 3's live smoke
test against the dev project.
"""
from unittest.mock import MagicMock

import pytest


def test_env_vars_for_collects_required_runtime_keys(monkeypatch):
    """env_vars_for must read exactly the runtime + telemetry env keys."""
    import importlib
    import deploy
    for k, v in {
        "DATASTORE_AA_ID": "ds-aa",
        "DATASTORE_PP_ID": "ds-pp",
        "DATASTORE_GUIDES_ID": "ds-g",
        "DATASTORE_FAQ_ID": "ds-faq",
        "DATASTORE_CHILEPRUNES_CL_ID": "ds-cl",
        "BIGQUERY_DATASET": "ds-bq",
    }.items():
        monkeypatch.setenv(k, v)
    monkeypatch.delenv("OTEL_CAPTURE_MESSAGE_CONTENT", raising=False)
    importlib.reload(deploy)  # TELEMETRY_ENV is materialized at import
    env = deploy.env_vars_for("agent_aa")
    assert env["DATASTORE_AA_ID"] == "ds-aa"
    assert env["BIGQUERY_DATASET"] == "ds-bq"
    # Telemetry must be on by default.
    assert env["GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY"] == "true"
    # Message-content capture is OFF by default to keep PII out of traces.
    assert env["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] == "false"


def test_env_vars_for_message_content_capture_opt_in(monkeypatch):
    """Operators can flip OTEL_CAPTURE_MESSAGE_CONTENT to opt back in."""
    import importlib
    import deploy
    for k, v in {
        "DATASTORE_AA_ID": "ds-aa",
        "DATASTORE_PP_ID": "ds-pp",
        "DATASTORE_GUIDES_ID": "ds-g",
        "DATASTORE_FAQ_ID": "ds-faq",
        "DATASTORE_CHILEPRUNES_CL_ID": "ds-cl",
        "BIGQUERY_DATASET": "ds-bq",
    }.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setenv("OTEL_CAPTURE_MESSAGE_CONTENT", "true")
    importlib.reload(deploy)
    env = deploy.env_vars_for("agent_aa")
    assert env["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] == "true"


def test_env_vars_for_raises_when_required_key_missing(monkeypatch):
    monkeypatch.delenv("DATASTORE_AA_ID", raising=False)
    import deploy
    with pytest.raises(KeyError):
        deploy.env_vars_for("agent_aa")


def test_env_vars_for_omits_reserved_project_var(monkeypatch):
    """GOOGLE_CLOUD_PROJECT / _LOCATION are reserved by Agent Engine and must
    NOT be shipped in deployment_spec.env — create() rejects them. The runtime
    injects them automatically."""
    import deploy
    for k, v in {
        "DATASTORE_AA_ID": "ds-aa",
        "DATASTORE_PP_ID": "ds-pp",
        "DATASTORE_GUIDES_ID": "ds-g",
        "DATASTORE_FAQ_ID": "ds-faq",
        "DATASTORE_CHILEPRUNES_CL_ID": "ds-cl",
        "BIGQUERY_DATASET": "ds-bq",
    }.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "agro-extension-digital-npe")
    env = deploy.env_vars_for("agent_aa")
    assert "GOOGLE_CLOUD_PROJECT" not in env
    assert "GOOGLE_CLOUD_LOCATION" not in env


# Idempotency is now keyed off the resource name stored in Secret Manager
# (find_existing / display_name matching was removed), so we test read_secret.
def test_read_secret_returns_stored_resource_name(monkeypatch):
    import deploy
    fake_client = MagicMock()
    fake_client.access_secret_version.return_value = MagicMock(
        payload=MagicMock(
            data=b"projects/p/locations/us-central1/reasoningEngines/123"
        )
    )
    monkeypatch.setattr(
        deploy.secretmanager, "SecretManagerServiceClient", lambda: fake_client
    )
    assert (
        deploy.read_secret("proj", "engine-aa-resource-name")
        == "projects/p/locations/us-central1/reasoningEngines/123"
    )


def test_read_secret_returns_none_when_secret_missing(monkeypatch):
    import deploy
    fake_client = MagicMock()
    fake_client.access_secret_version.side_effect = deploy.gax.NotFound("nope")
    monkeypatch.setattr(
        deploy.secretmanager, "SecretManagerServiceClient", lambda: fake_client
    )
    assert deploy.read_secret("proj", "missing") is None


def test_read_secret_returns_none_when_latest_version_disabled(monkeypatch):
    # An operator may disable the latest engine-name secret version to force a
    # clean redeploy (see the rollback runbook). access_secret_version then
    # raises FailedPrecondition, not NotFound — read_secret must still return
    # None so deploy_one recreates instead of crashing.
    import deploy
    fake_client = MagicMock()
    fake_client.access_secret_version.side_effect = deploy.gax.FailedPrecondition(
        "version is in DISABLED state"
    )
    monkeypatch.setattr(
        deploy.secretmanager, "SecretManagerServiceClient", lambda: fake_client
    )
    assert deploy.read_secret("proj", "engine-aa-resource-name") is None


# ---------------------------------------------------------------------------
# write_secret: create-if-missing + skip-if-unchanged version management
# ---------------------------------------------------------------------------
def _patch_sm_client(monkeypatch, deploy, client):
    monkeypatch.setattr(
        deploy.secretmanager, "SecretManagerServiceClient", lambda: client
    )


def test_write_secret_creates_missing_secret_then_adds_version(monkeypatch):
    import deploy
    client = MagicMock()
    client.get_secret.side_effect = deploy.gax.NotFound("no such secret")
    _patch_sm_client(monkeypatch, deploy, client)

    deploy.write_secret("proj", "engine-aa-resource-name", "res/123")

    client.create_secret.assert_called_once()
    create_req = client.create_secret.call_args.kwargs["request"]
    assert create_req["secret_id"] == "engine-aa-resource-name"
    assert create_req["parent"] == "projects/proj"
    # A version is written for the brand-new secret.
    client.add_secret_version.assert_called_once()
    add_req = client.add_secret_version.call_args.kwargs["request"]
    assert add_req["payload"]["data"] == b"res/123"


def test_write_secret_skips_when_latest_value_unchanged(monkeypatch):
    import deploy
    client = MagicMock()
    client.get_secret.return_value = MagicMock()  # secret exists
    client.access_secret_version.return_value = MagicMock(
        payload=MagicMock(data=b"res/same")
    )
    _patch_sm_client(monkeypatch, deploy, client)

    deploy.write_secret("proj", "engine-aa-resource-name", "res/same")

    # Latest already equals value -> no version sprawl.
    client.create_secret.assert_not_called()
    client.add_secret_version.assert_not_called()


def test_write_secret_adds_version_when_value_changed(monkeypatch):
    import deploy
    client = MagicMock()
    client.get_secret.return_value = MagicMock()
    client.access_secret_version.return_value = MagicMock(
        payload=MagicMock(data=b"res/old")
    )
    _patch_sm_client(monkeypatch, deploy, client)

    deploy.write_secret("proj", "engine-aa-resource-name", "res/new")

    client.create_secret.assert_not_called()
    client.add_secret_version.assert_called_once()
    assert (
        client.add_secret_version.call_args.kwargs["request"]["payload"]["data"]
        == b"res/new"
    )


def test_write_secret_adds_version_when_secret_exists_but_no_version(monkeypatch):
    import deploy
    client = MagicMock()
    client.get_secret.return_value = MagicMock()  # secret exists...
    # ...but has no accessible version yet
    client.access_secret_version.side_effect = deploy.gax.NotFound("no version")
    _patch_sm_client(monkeypatch, deploy, client)

    deploy.write_secret("proj", "engine-aa-resource-name", "res/first")

    client.create_secret.assert_not_called()
    client.add_secret_version.assert_called_once()


# ---------------------------------------------------------------------------
# deploy_one: create-vs-update idempotency keyed off the stored resource name
# ---------------------------------------------------------------------------
CFG = {
    "module_path": "agent_aa_app",
    "app_module": "agent_aa_app.agent_engine_app",
    "display_name": "AA",
    "secret_id": "engine-aa-resource-name",
}


def _stub_deploy_deps(monkeypatch, deploy):
    """Neutralize import + secret IO so we isolate the create/update branch."""
    mod = MagicMock()
    mod.app = MagicMock(name="AdkApp")
    monkeypatch.setattr(deploy, "import_module", lambda name: mod)
    monkeypatch.setattr(deploy, "write_secret", MagicMock(name="write_secret"))
    # env_vars_for reads RUNTIME_ENV_KEYS from os.environ (seeded by conftest).
    return mod


def test_deploy_one_updates_existing_engine(monkeypatch):
    import deploy
    _stub_deploy_deps(monkeypatch, deploy)
    monkeypatch.setattr(deploy, "read_secret", lambda p, s: "res/existing")

    existing = MagicMock(name="engine")
    updated = MagicMock(resource_name="res/existing")
    existing.update.return_value = updated
    engines = MagicMock()
    engines.get.return_value = existing
    monkeypatch.setattr(deploy, "agent_engines", engines)

    deploy.deploy_one("agent_aa", CFG, "proj", "sa@x")

    engines.get.assert_called_once_with("res/existing")
    existing.update.assert_called_once()
    engines.create.assert_not_called()
    # The stored resource name is written back (idempotent no-op if unchanged).
    deploy.write_secret.assert_called_once_with(
        "proj", "engine-aa-resource-name", "res/existing"
    )


def test_deploy_one_creates_when_secret_missing(monkeypatch):
    import deploy
    _stub_deploy_deps(monkeypatch, deploy)
    monkeypatch.setattr(deploy, "read_secret", lambda p, s: None)

    created = MagicMock(resource_name="res/new-123")
    engines = MagicMock()
    engines.create.return_value = created
    monkeypatch.setattr(deploy, "agent_engines", engines)

    deploy.deploy_one("agent_aa", CFG, "proj", "sa@x")

    engines.get.assert_not_called()
    engines.create.assert_called_once()
    # New resource name is persisted so the next run updates in place.
    deploy.write_secret.assert_called_once_with(
        "proj", "engine-aa-resource-name", "res/new-123"
    )


def test_deploy_one_recreates_when_stored_engine_is_gone(monkeypatch):
    import deploy
    _stub_deploy_deps(monkeypatch, deploy)
    monkeypatch.setattr(deploy, "read_secret", lambda p, s: "res/stale")

    created = MagicMock(resource_name="res/fresh")
    engines = MagicMock()
    engines.get.side_effect = deploy.gax.NotFound("engine deleted")
    engines.create.return_value = created
    monkeypatch.setattr(deploy, "agent_engines", engines)

    deploy.deploy_one("agent_aa", CFG, "proj", "sa@x")

    # NotFound on the stored resource -> fall back to create, not crash.
    engines.get.assert_called_once_with("res/stale")
    engines.create.assert_called_once()
    deploy.write_secret.assert_called_once_with(
        "proj", "engine-aa-resource-name", "res/fresh"
    )


def test_deploy_one_propagates_non_notfound_get_errors(monkeypatch):
    import deploy
    _stub_deploy_deps(monkeypatch, deploy)
    monkeypatch.setattr(deploy, "read_secret", lambda p, s: "res/x")

    engines = MagicMock()
    engines.get.side_effect = deploy.gax.PermissionDenied("nope")
    monkeypatch.setattr(deploy, "agent_engines", engines)

    with pytest.raises(deploy.gax.PermissionDenied):
        deploy.deploy_one("agent_aa", CFG, "proj", "sa@x")
    # Only NotFound triggers create; other errors must not silently recreate.
    engines.create.assert_not_called()
    deploy.write_secret.assert_not_called()


# ---------------------------------------------------------------------------
# main: up-front env validation before any engine mutation
# ---------------------------------------------------------------------------
def test_main_aborts_before_mutation_when_required_env_missing(monkeypatch):
    import deploy
    monkeypatch.setattr("sys.argv", ["deploy.py", "--env", "npe"])
    monkeypatch.delenv("DATASTORE_AA_ID", raising=False)
    init = MagicMock()
    monkeypatch.setattr(deploy.vertexai, "init", init)
    deploy_one = MagicMock()
    monkeypatch.setattr(deploy, "deploy_one", deploy_one)

    with pytest.raises(SystemExit) as exc:
        deploy.main()

    assert "DATASTORE_AA_ID" in str(exc.value)
    # Fail fast: no vertexai.init, no engine deploy -> no half-migrated state.
    init.assert_not_called()
    deploy_one.assert_not_called()


def test_main_happy_path_deploys_both_agents(monkeypatch):
    import deploy
    for k, v in {
        "DATASTORE_AA_ID": "a", "DATASTORE_PP_ID": "b", "DATASTORE_GUIDES_ID": "c",
        "DATASTORE_FAQ_ID": "d", "DATASTORE_CHILEPRUNES_CL_ID": "e",
        "BIGQUERY_DATASET": "bq",
    }.items():
        monkeypatch.setenv(k, v)
    # The workflow exports GOOGLE_CLOUD_PROJECT matching --env; mirror that.
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "agro-extension-digital-prd")
    monkeypatch.setattr("sys.argv", ["deploy.py", "--env", "prd"])
    init = MagicMock()
    monkeypatch.setattr(deploy.vertexai, "init", init)
    calls = []
    monkeypatch.setattr(
        deploy, "deploy_one", lambda key, cfg, project, sa: calls.append((key, project, sa))
    )

    deploy.main()

    init.assert_called_once()
    assert init.call_args.kwargs["project"] == "agro-extension-digital-prd"
    # Both agents deployed with their per-agent runtime service accounts.
    keys = {c[0] for c in calls}
    assert keys == {"agent_aa", "agent_pp"}
    sas = {c[2] for c in calls}
    assert (
        "agent-aa-runtime@agro-extension-digital-prd.iam.gserviceaccount.com" in sas
    )


def test_main_aborts_when_project_env_mismatches_target(monkeypatch):
    """A manual run whose GOOGLE_CLOUD_PROJECT disagrees with --env must abort
    before any deploy — the agent modules bake datastore/RAG paths from that
    env var, so a mismatch would ship a cross-project engine."""
    import deploy
    for k, v in {
        "DATASTORE_AA_ID": "a", "DATASTORE_PP_ID": "b", "DATASTORE_GUIDES_ID": "c",
        "DATASTORE_FAQ_ID": "d", "DATASTORE_CHILEPRUNES_CL_ID": "e",
        "BIGQUERY_DATASET": "bq",
    }.items():
        monkeypatch.setenv(k, v)
    # Target prd, but the environment still points at npe.
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "agro-extension-digital-npe")
    monkeypatch.setattr("sys.argv", ["deploy.py", "--env", "prd"])
    init = MagicMock()
    monkeypatch.setattr(deploy.vertexai, "init", init)
    deploy_one = MagicMock()
    monkeypatch.setattr(deploy, "deploy_one", deploy_one)

    with pytest.raises(SystemExit) as exc:
        deploy.main()

    assert "does not match" in str(exc.value)
    init.assert_not_called()
    deploy_one.assert_not_called()
