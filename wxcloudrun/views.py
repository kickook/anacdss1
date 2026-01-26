from datetime import datetime

from flask import Blueprint, render_template, request

from wxcloudrun import db
from wxcloudrun.dify_client import send_alert
from wxcloudrun.model import Alert, Device, Parameter, Patient, Room, Session, Threshold, VitalRecord
from wxcloudrun.response import error, success

api_bp = Blueprint("api", __name__, url_prefix="/api")
ui_bp = Blueprint("ui", __name__)


@ui_bp.route("/")
def index():
    rooms = Room.query.order_by(Room.id.desc()).all()
    alerts = Alert.query.order_by(Alert.created_at.desc()).limit(20).all()
    return render_template("index.html", rooms=rooms, alerts=alerts)


@api_bp.post("/rooms")
def create_room():
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    if not name:
        return error("name is required")
    room = Room(name=name, location=payload.get("location"))
    db.session.add(room)
    db.session.commit()
    return success({"id": room.id, "name": room.name})


@api_bp.get("/rooms")
def list_rooms():
    rooms = Room.query.order_by(Room.id.desc()).all()
    return success([{"id": room.id, "name": room.name, "location": room.location} for room in rooms])


@api_bp.post("/rooms/<int:room_id>/devices")
def create_device(room_id):
    room = Room.query.get(room_id)
    if not room:
        return error("room not found", status=404)
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    device_type = payload.get("device_type")
    if not name or not device_type:
        return error("name and device_type are required")
    device = Device(
        room_id=room.id,
        name=name,
        device_type=device_type,
        vendor=payload.get("vendor"),
        model=payload.get("model"),
    )
    db.session.add(device)
    db.session.commit()
    return success({"id": device.id, "name": device.name})


@api_bp.post("/devices/<int:device_id>/parameters")
def create_parameter(device_id):
    device = Device.query.get(device_id)
    if not device:
        return error("device not found", status=404)
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    code = payload.get("code")
    if not name or not code:
        return error("name and code are required")
    parameter = Parameter(
        device_id=device.id,
        name=name,
        code=code,
        unit=payload.get("unit"),
    )
    db.session.add(parameter)
    db.session.commit()
    return success({"id": parameter.id, "name": parameter.name, "code": parameter.code})


@api_bp.post("/parameters/<int:parameter_id>/threshold")
def create_threshold(parameter_id):
    parameter = Parameter.query.get(parameter_id)
    if not parameter:
        return error("parameter not found", status=404)
    payload = request.get_json(silent=True) or {}
    threshold = Threshold(
        parameter_id=parameter.id,
        min_value=payload.get("min_value"),
        max_value=payload.get("max_value"),
        severity=payload.get("severity", "medium"),
    )
    db.session.add(threshold)
    db.session.commit()
    return success({"id": threshold.id})


@api_bp.post("/patients")
def create_patient():
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    if not name:
        return error("name is required")
    patient = Patient(
        name=name,
        gender=payload.get("gender"),
        age=payload.get("age"),
        mrn=payload.get("mrn"),
    )
    db.session.add(patient)
    db.session.commit()
    return success({"id": patient.id, "name": patient.name})


@api_bp.post("/sessions")
def create_session():
    payload = request.get_json(silent=True) or {}
    room_id = payload.get("room_id")
    patient_id = payload.get("patient_id")
    if not room_id or not patient_id:
        return error("room_id and patient_id are required")
    room = Room.query.get(room_id)
    patient = Patient.query.get(patient_id)
    if not room or not patient:
        return error("room or patient not found", status=404)
    session = Session(room_id=room.id, patient_id=patient.id)
    db.session.add(session)
    db.session.commit()
    return success({"id": session.id, "status": session.status})


@api_bp.post("/sessions/<int:session_id>/ingest")
def ingest_vitals(session_id):
    session = Session.query.get(session_id)
    if not session:
        return error("session not found", status=404)
    payload = request.get_json(silent=True) or {}
    readings = payload.get("readings")
    if not readings:
        return error("readings is required")

    alerts = []
    for reading in readings:
        parameter_id = reading.get("parameter_id")
        value = reading.get("value")
        if parameter_id is None or value is None:
            return error("each reading must include parameter_id and value")
        parameter = Parameter.query.get(parameter_id)
        if not parameter:
            return error(f"parameter {parameter_id} not found", status=404)
        recorded_at = reading.get("recorded_at")
        if recorded_at:
            recorded_at = datetime.fromisoformat(recorded_at)
        record = VitalRecord(
            session_id=session.id,
            parameter_id=parameter.id,
            value=float(value),
            recorded_at=recorded_at or datetime.utcnow(),
        )
        db.session.add(record)
        threshold = parameter.threshold
        if threshold and (
            (threshold.min_value is not None and value < threshold.min_value)
            or (threshold.max_value is not None and value > threshold.max_value)
        ):
            message = f"{parameter.name} 超出阈值"
            alert = Alert(
                session_id=session.id,
                parameter_id=parameter.id,
                value=value,
                threshold_min=threshold.min_value,
                threshold_max=threshold.max_value,
                message=message,
            )
            db.session.add(alert)
            alerts.append(alert)
    db.session.commit()

    dify_response = None
    if alerts:
        context = {
            "session_id": session.id,
            "room_id": session.room_id,
            "patient_id": session.patient_id,
            "alerts": [
                {
                    "parameter": alert.parameter.name,
                    "value": alert.value,
                    "min": alert.threshold_min,
                    "max": alert.threshold_max,
                    "message": alert.message,
                }
                for alert in alerts
            ],
        }
        try:
            dify_response = send_alert(context)
        except Exception:
            dify_response = None

    return success(
        {
            "records": len(readings),
            "alerts": [alert.id for alert in alerts],
            "dify": dify_response,
        }
    )


@api_bp.get("/alerts")
def list_alerts():
    alerts = Alert.query.order_by(Alert.created_at.desc()).limit(50).all()
    return success(
        [
            {
                "id": alert.id,
                "session_id": alert.session_id,
                "parameter": alert.parameter.name,
                "value": alert.value,
                "message": alert.message,
                "created_at": alert.created_at.isoformat(),
            }
            for alert in alerts
        ]
    )
