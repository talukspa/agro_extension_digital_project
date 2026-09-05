"""AdkApp shim for Producción Primaria — all logic lives in core."""
from core.agent import build_app

app = build_app(
    name="pp_agent",
    display_name="Producción Primaria",
    main_datastore_env="DATASTORE_PP_ID",
)
