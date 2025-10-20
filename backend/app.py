"""Flask application entry point."""
from __future__ import annotations

from flask import Flask, jsonify, redirect, render_template, request, url_for, flash
from flask_cors import CORS

from backend.config import CONFIG
from backend.database import db
from backend.models import (
    AlertRule,
    DeviceIntegration,
    MonitoringParameter,
    OperatingRoom,
    Patient,
    Role,
    User,
)


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

    @app.route("/devices", methods=["GET"])
    def list_devices():
        devices = DeviceIntegration.query.all()
        return jsonify([
            {
                "id": d.id,
                "name": d.name,
                "device_type": d.device_type,
                "connection_info": d.connection_info,
                "operating_room_id": d.operating_room_id,
                "operating_room": d.operating_room.name if d.operating_room else None,
            }
            for d in devices
        ])

    @app.route("/devices", methods=["POST"])
    def create_device():
        data = request.json or {}
        operating_room_id = data.get("operating_room_id")
        if operating_room_id is not None:
            operating_room_id = int(operating_room_id)
        device = DeviceIntegration(
            name=data.get("name"),
            device_type=data.get("device_type"),
            connection_info=data.get("connection_info"),
            operating_room_id=operating_room_id,
        )
        db.session.add(device)
        db.session.commit()
        return jsonify({"id": device.id}), 201

    @app.route("/parameters", methods=["GET"])
    def list_parameters():
        parameters = MonitoringParameter.query.all()
        return jsonify([
            {
                "id": p.id,
                "name": p.name,
                "unit": p.unit,
                "dify_field": p.dify_field,
                "device_id": p.device_id,
                "device": p.device.name if p.device else None,
            }
            for p in parameters
        ])

    @app.route("/parameters", methods=["POST"])
    def create_parameter():
        data = request.json or {}
        device_id = data.get("device_id")
        if device_id is not None:
            device_id = int(device_id)
        parameter = MonitoringParameter(
            device_id=device_id,
            name=data.get("name"),
            unit=data.get("unit"),
            dify_field=data.get("dify_field"),
        )
        db.session.add(parameter)
        db.session.commit()
        return jsonify({"id": parameter.id}), 201

    @app.route("/alert-rules", methods=["GET"])
    def list_alert_rules():
        rules = AlertRule.query.all()
        return jsonify([
            {
                "id": r.id,
                "parameter_id": r.parameter_id,
                "parameter": r.parameter.name if r.parameter else None,
                "lower_bound": r.lower_bound,
                "upper_bound": r.upper_bound,
                "severity": r.severity,
                "message_template": r.message_template,
            }
            for r in rules
        ])

    @app.route("/alert-rules", methods=["POST"])
    def create_alert_rule():
        data = request.json or {}
        parameter_id = data.get("parameter_id")
        if parameter_id is not None:
            parameter_id = int(parameter_id)
        lower_bound = data.get("lower_bound")
        if lower_bound not in (None, ""):
            lower_bound = float(lower_bound)
        else:
            lower_bound = None
        upper_bound = data.get("upper_bound")
        if upper_bound not in (None, ""):
            upper_bound = float(upper_bound)
        else:
            upper_bound = None
        rule = AlertRule(
            parameter_id=parameter_id,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            severity=data.get("severity", "warning"),
            message_template=data.get("message_template"),
        )
        db.session.add(rule)
        db.session.commit()
        return jsonify({"id": rule.id}), 201

    @app.route("/admin", methods=["GET", "POST"])
    def admin_dashboard():
        if request.method == "POST":
            entity = request.form.get("entity")
            try:
                if entity == "operating_room":
                    room = OperatingRoom(
                        name=request.form.get("name"),
                        description=request.form.get("description"),
                    )
                    db.session.add(room)
                    db.session.commit()
                    flash("已新增手术间。", "success")
                elif entity == "device":
                    device = DeviceIntegration(
                        name=request.form.get("name"),
                        device_type=request.form.get("device_type"),
                        connection_info=request.form.get("connection_info"),
                        operating_room_id=int(request.form.get("operating_room_id")),
                    )
                    db.session.add(device)
                    db.session.commit()
                    flash("已新增设备集成。", "success")
                elif entity == "parameter":
                    parameter = MonitoringParameter(
                        device_id=int(request.form.get("device_id")),
                        name=request.form.get("name"),
                        unit=request.form.get("unit"),
                        dify_field=request.form.get("dify_field"),
                    )
                    db.session.add(parameter)
                    db.session.commit()
                    flash("已新增监测参数。", "success")
                elif entity == "alert_rule":
                    lower_bound = request.form.get("lower_bound")
                    upper_bound = request.form.get("upper_bound")
                    rule = AlertRule(
                        parameter_id=int(request.form.get("parameter_id")),
                        lower_bound=float(lower_bound) if lower_bound else None,
                        upper_bound=float(upper_bound) if upper_bound else None,
                        severity=request.form.get("severity", "warning"),
                        message_template=request.form.get("message_template"),
                    )
                    db.session.add(rule)
                    db.session.commit()
                    flash("已新增预警规则。", "success")
                else:
                    flash("未知的管理操作。", "error")
            except Exception as exc:  # pragma: no cover - defensive path
                db.session.rollback()
                flash(f"保存失败：{exc}", "error")
            return redirect(url_for("admin_dashboard"))

        rooms = OperatingRoom.query.all()
        devices = DeviceIntegration.query.all()
        parameters = MonitoringParameter.query.all()
        alert_rules = AlertRule.query.all()

        return render_template(
            "admin/dashboard.html",
            rooms=rooms,
            devices=devices,
            parameters=parameters,
            alert_rules=alert_rules,
        )

    return app


def init_db(app: Flask) -> None:
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    application = create_app()
    init_db(application)
    application.run(host="0.0.0.0", port=8000)
