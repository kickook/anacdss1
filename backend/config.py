"""Application configuration and settings."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE_PATH = (PROJECT_ROOT / "anacdss.db").resolve()


def _get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    """Helper to pull environment variables with defaults."""
    return os.environ.get(name, default)


@dataclass
class DatabaseConfig:
    uri: str = _get_env("DATABASE_URI", f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}")
    echo: bool = _get_env("SQLALCHEMY_ECHO", "false").lower() == "true"


@dataclass
class DifyConfig:
    base_url: str = _get_env("DIFY_BASE_URL", "https://api.dify.ai/v1")
    app_id: str = _get_env("DIFY_APP_ID", "")
    api_key: str = _get_env("DIFY_API_KEY", "")
    timeout: int = int(_get_env("DIFY_TIMEOUT", "15"))


@dataclass
class MonitoringConfig:
    polling_interval: int = int(_get_env("MONITORING_POLLING_INTERVAL", "10"))
    alert_batch_window: int = int(_get_env("ALERT_BATCH_WINDOW", "60"))


@dataclass
class AppConfig:
    secret_key: str = _get_env("SECRET_KEY", "change-me")
    database: DatabaseConfig = DatabaseConfig()
    dify: DifyConfig = DifyConfig()
    monitoring: MonitoringConfig = MonitoringConfig()


CONFIG = AppConfig()
