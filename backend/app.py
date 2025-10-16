"""Flask application entry point."""
from __future__ import annotations

from flask import Flask, jsonify, request
from flask_cors import CORS

from .config import CONFIG
from .database import db
from .models import AlertRule, DeviceIntegration, MonitoringParameter, OperatingRoom, Patient, Role, User


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = CONFIG.database.uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = CONFIG.secret_key

    db.init_app(app)
    CORS(app)

    @app.route("/health")
    def health_check() -> tuple[str, int]:
        return "ok", 200

    @app.route("/operating-rooms", methods=["GET"])
    def list_operating_rooms():
        rooms = OperatingRoom.query.all()
        return jsonify([
            {"id": r.id, "name": r.name, "description": r.description}
            for r in rooms
        ])

    @app.route("/operating-rooms", methods=["POST"])
    def create_operating_room():
        data = request.json or {}
        room = OperatingRoom(name=data.get("name"), description=data.get("description"))
        db.session.add(room)
        db.session.commit()
        return jsonify({"id": room.id, "name": room.name}), 201

    @app.route("/devices", methods=["POST"])
    def create_device():
        data = request.json or {}
        device = DeviceIntegration(
            name=data.get("name"),
            device_type=data.get("device_type"),
            connection_info=data.get("connection_info"),
            operating_room_id=data.get("operating_room_id"),
        )
        db.session.add(device)
        db.session.commit()
        return jsonify({"id": device.id}), 201

    @app.route("/parameters", methods=["POST"])
    def create_parameter():
        data = request.json or {}
        parameter = MonitoringParameter(
            device_id=data.get("device_id"),
            name=data.get("name"),
            unit=data.get("unit"),
            dify_field=data.get("dify_field"),
        )
        db.session.add(parameter)
        db.session.commit()
        return jsonify({"id": parameter.id}), 201

    @app.route("/alert-rules", methods=["POST"])
    def create_alert_rule():
        data = request.json or {}
        rule = AlertRule(
            parameter_id=data.get("parameter_id"),
            lower_bound=data.get("lower_bound"),
            upper_bound=data.get("upper_bound"),
            severity=data.get("severity", "warning"),
            message_template=data.get("message_template"),
        )
        db.session.add(rule)
        db.session.commit()
        return jsonify({"id": rule.id}), 201

    return app


def init_db(app: Flask) -> None:
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    application = create_app()
    init_db(application)
    application.run(host="0.0.0.0", port=8000)
