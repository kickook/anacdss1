"""Convenience entry point so the Flask backend runs cleanly in IDEs like PyCharm."""
from __future__ import annotations

from backend.app import create_app, init_db


app = create_app()
init_db(app)


if __name__ == "__main__":  # pragma: no cover - manual launch helper
    app.run(host="0.0.0.0", port=8000)
