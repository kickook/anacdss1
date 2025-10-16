# Backend Overview

This Flask backend provides configuration APIs and alert orchestration for the anesthesia vital sign early-warning system.

## Features

- Operating room management and device registration.
- Parameter and alert rule configuration with flexible thresholds.
- Dify LLM integration through `backend.dify_client` to enrich alerts with recommendations.

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.py
python app.py
```

Environment variables (see `backend/config.py`) allow customization of database URI, Dify credentials, and monitoring tuning.
