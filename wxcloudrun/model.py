from datetime import datetime

from wxcloudrun import db


class Room(db.Model):
    __tablename__ = "rooms"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    devices = db.relationship("Device", backref="room", lazy=True)
    sessions = db.relationship("Session", backref="room", lazy=True)


class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    device_type = db.Column(db.String(80), nullable=False)
    vendor = db.Column(db.String(120))
    model = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    parameters = db.relationship("Parameter", backref="device", lazy=True)


class Parameter(db.Model):
    __tablename__ = "parameters"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey("devices.id"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    code = db.Column(db.String(40), nullable=False)
    unit = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    threshold = db.relationship("Threshold", backref="parameter", uselist=False)


class Threshold(db.Model):
    __tablename__ = "thresholds"

    id = db.Column(db.Integer, primary_key=True)
    parameter_id = db.Column(db.Integer, db.ForeignKey("parameters.id"), nullable=False)
    min_value = db.Column(db.Float)
    max_value = db.Column(db.Float)
    severity = db.Column(db.String(20), default="medium")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    mrn = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sessions = db.relationship("Session", backref="patient", lazy=True)


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    status = db.Column(db.String(20), default="active")
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)

    vitals = db.relationship("VitalRecord", backref="session", lazy=True)
    alerts = db.relationship("Alert", backref="session", lazy=True)


class VitalRecord(db.Model):
    __tablename__ = "vital_records"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)
    parameter_id = db.Column(db.Integer, db.ForeignKey("parameters.id"), nullable=False)
    value = db.Column(db.Float, nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    parameter = db.relationship("Parameter")


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)
    parameter_id = db.Column(db.Integer, db.ForeignKey("parameters.id"), nullable=False)
    value = db.Column(db.Float, nullable=False)
    threshold_min = db.Column(db.Float)
    threshold_max = db.Column(db.Float)
    message = db.Column(db.String(200), nullable=False)
    resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    parameter = db.relationship("Parameter")
