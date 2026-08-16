"""AdkApp shim for Adecuación Agroindustrial — all logic lives in core."""
from core.agent import build_app

app = build_app(
    name="aa_agent",
    display_name="Adecuación Agroindustrial",
    main_datastore_env="DATASTORE_AA_ID",
)
