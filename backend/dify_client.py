"""Client helper to interact with Dify LLM service."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

from .config import CONFIG


@dataclass
class DifyPayload:
    """Payload that will be sent to Dify LLM."""

    alert_message: str
    patient_info: Dict[str, Any]
    vital_signs: Dict[str, Any]
    operating_room: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "inputs": {
                "alert_message": self.alert_message,
                "patient_info": self.patient_info,
                "vital_signs": self.vital_signs,
                "operating_room": self.operating_room,
            }
        }


class DifyClient:
    """Simple wrapper around the Dify HTTP API."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, app_id: Optional[str] = None) -> None:
        self.api_key = api_key or CONFIG.dify.api_key
        self.base_url = base_url or CONFIG.dify.base_url.rstrip("/")
        self.app_id = app_id or CONFIG.dify.app_id

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def send_alert(self, payload: DifyPayload) -> Dict[str, Any]:
        """Send alert context to Dify and return response."""

        if not self.api_key or not self.app_id:
            raise RuntimeError("Dify API key or App ID missing.")

        url = f"{self.base_url}/apps/{self.app_id}/workflows/run"
        response = requests.post(url, json=payload.to_dict(), headers=self._headers(), timeout=CONFIG.dify.timeout)
        response.raise_for_status()
        return response.json()


def get_client() -> DifyClient:
    """Factory returning a configured client."""

    return DifyClient()
