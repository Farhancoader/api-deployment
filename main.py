import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import dotenv_values
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="Effective Config API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

DEFAULTS: dict[str, Any] = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "on"}


def coerce(key: str, value: Any) -> Any:
    if key in {"port", "workers"}:
        return int(value)
    if key == "debug":
        return as_bool(value)
    return str(value)


def load_yaml_layer() -> dict[str, Any]:
    # This assignment specifies config.development.yaml.
    path = Path("config.development.yaml")
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}


@app.get("/effective-config")
async def effective_config(request: Request, set: list[str] = Query(default=[])):
    config: dict[str, Any] = dict(DEFAULTS)

    # Layer 2: config.<env>.yaml
    config.update(load_yaml_layer())

    # Layer 3: .env; NUM_WORKERS is an alias for workers.
    env_file = dotenv_values(".env")
    for raw_key, value in env_file.items():
        if value is None:
            continue
        key = "workers" if raw_key == "NUM_WORKERS" else raw_key
        if key.startswith("APP_"):
            key = key[4:].lower()
        config[key.lower()] = value

    # Layer 4: OS environment variables with APP_ prefix.
    for raw_key, value in os.environ.items():
        if raw_key.startswith("APP_"):
            config[raw_key[4:].lower()] = value

    # Highest precedence: repeated ?set=key=value query parameters.
    for item in set:
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        key = key.strip().lower()
        if key.startswith("app_"):
            key = key[4:]
        if key == "num_workers":
            key = "workers"
        if key:
            config[key] = value

    result = {key: coerce(key, value) for key, value in config.items()}
    # Never expose the real secret, even if an override is supplied.
    if "api_key" in result:
        result["api_key"] = "****"
    return JSONResponse(content=result)
