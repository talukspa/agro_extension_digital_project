"""AdkApp shim wrapping agent_pp_app's root_agent for Agent Runtime deploy.

Mirror of agent_aa_app/agent_engine_app.py — see that file for the why.
"""
from vertexai.agent_engines import AdkApp

from agent_pp_app.agent import root_agent

app = AdkApp(agent=root_agent)
