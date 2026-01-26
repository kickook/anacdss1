import json

import requests

import config


def send_alert(context):
    if not config.DIFY_API_URL or not config.DIFY_API_KEY:
        return None

    headers = {
        "Authorization": f"Bearer {config.DIFY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": context,
        "response_mode": "blocking",
    }

    response = requests.post(
        config.DIFY_API_URL,
        headers=headers,
        data=json.dumps(payload),
        timeout=config.DIFY_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()
