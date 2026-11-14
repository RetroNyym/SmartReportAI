import os
from typing import Any

import yaml

from .settings import ROOT_DIR

CONFIG_DIR = ROOT_DIR / "config"


def _expand_env(value: Any) -> Any:
    """Replace ${VAR} placeholders in YAML values with environment variables."""
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    if isinstance(value, str):
        return os.path.expandvars(value)
    return value


def _load_yaml(file_name: str) -> dict:
    with open(CONFIG_DIR / file_name, encoding="utf-8") as f:
        return _expand_env(yaml.safe_load(f))


def load_connections() -> dict[str, dict]:
    return _load_yaml("connections.yaml")["connections"]


def load_reports() -> list[dict]:
    """Return report definitions from config/reports.yaml with absolute query paths."""
    reports = _load_yaml("reports.yaml")["reports"]
    for report in reports:
        report["query"] = str(ROOT_DIR / report["query"])
    return reports
