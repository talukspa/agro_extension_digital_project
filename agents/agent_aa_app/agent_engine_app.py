"""AdkApp shim wrapping agent_aa_app's root_agent for Agent Runtime deploy.

When deployed via vertexai.agent_engines.create(), the AdkApp template
auto-wires the default session_service (Agent Runtime managed Sessions)
and memory_service (Memory Bank on this engine's resource id), so no
builders are passed here. Tracing is driven by env vars at deploy time
(see agents/deploy.py:TELEMETRY_ENV) — the soft-deprecated
`enable_tracing=True` kwarg is intentionally not passed.
"""
from vertexai.agent_engines import AdkApp

from agent_aa_app.agent import root_agent

app = AdkApp(agent=root_agent)
