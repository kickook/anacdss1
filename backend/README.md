# Backend Overview

This Flask backend provides configuration APIs and alert orchestration for the anesthesia vital sign early-warning system.

## Features

- Operating room management and device registration.
- Parameter and alert rule configuration with flexible thresholds.
- Built-in `/admin` control panel to manage rooms, device interfaces, monitoring parameters, and alert rules without manual database edits.
- Dify LLM integration through `backend.dify_client` to enrich alerts with recommendations.

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
python ../run.py
```

Environment variables (see `backend/config.py`) allow customization of database URI, Dify credentials, and monitoring tuning. Visit `http://localhost:8000/admin` while the server is running to manage configuration through the browser.

> 💡 **PyCharm 提示**：将 `run.py` 作为运行配置（Script path 指向仓库根目录下的 `run.py`，Working directory 设置为仓库根目录），即可一键启动服务。PyCharm 会自动读取 `requirements.txt` 并提示创建虚拟环境。
