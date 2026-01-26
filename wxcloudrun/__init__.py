from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import config


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    with app.app_context():
        from wxcloudrun import model  # noqa: F401
        db.create_all()

    from wxcloudrun.views import api_bp, ui_bp
    app.register_blueprint(api_bp)
    app.register_blueprint(ui_bp)

    return app


app = create_app()
