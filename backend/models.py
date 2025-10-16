"""Database models for the monitoring backend."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import db


class Role(db.Model):
    """Role for RBAC."""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    users: Mapped[List["User"]] = relationship(back_populates="role")


class User(db.Model):
    """User with assigned role."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)

    role: Mapped[Role] = relationship(back_populates="users")


class OperatingRoom(db.Model):
    """Operating room definition."""

    __tablename__ = "operating_rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    devices: Mapped[List["DeviceIntegration"]] = relationship(back_populates="operating_room")
    sessions: Mapped[List["MonitoringSession"]] = relationship(back_populates="operating_room")


class Patient(db.Model):
    """Patient scheduled for anesthesia."""

    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    medical_record_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    age: Mapped[int] = mapped_column(Integer)
    sex: Mapped[Optional[str]] = mapped_column(String(16))
    allergies: Mapped[Optional[str]] = mapped_column(Text)
    medication_plan: Mapped[Optional[str]] = mapped_column(Text)

    sessions: Mapped[List["MonitoringSession"]] = relationship(back_populates="patient")


class DeviceIntegration(db.Model):
    """External device connected to an OR."""

    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    device_type: Mapped[str] = mapped_column(String(50), nullable=False)
    connection_info: Mapped[str] = mapped_column(Text, nullable=False)
    operating_room_id: Mapped[int] = mapped_column(ForeignKey("operating_rooms.id"), nullable=False)

    operating_room: Mapped[OperatingRoom] = relationship(back_populates="devices")
    parameters: Mapped[List["MonitoringParameter"]] = relationship(back_populates="device")


class MonitoringParameter(db.Model):
    """Parameter stream retrieved from a device."""

    __tablename__ = "monitoring_parameters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(20))
    dify_field: Mapped[Optional[str]] = mapped_column(String(80))

    device: Mapped[DeviceIntegration] = relationship(back_populates="parameters")
    alert_rules: Mapped[List["AlertRule"]] = relationship(back_populates="parameter")


class AlertRule(db.Model):
    """Threshold definitions for alerts."""

    __tablename__ = "alert_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parameter_id: Mapped[int] = mapped_column(ForeignKey("monitoring_parameters.id"), nullable=False)
    lower_bound: Mapped[Optional[float]] = mapped_column()
    upper_bound: Mapped[Optional[float]] = mapped_column()
    severity: Mapped[str] = mapped_column(String(20), default="warning")
    message_template: Mapped[Optional[str]] = mapped_column(Text)

    parameter: Mapped[MonitoringParameter] = relationship(back_populates="alert_rules")


class MonitoringSession(db.Model):
    """Represents a monitoring session for a patient in an OR."""

    __tablename__ = "monitoring_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    operating_room_id: Mapped[int] = mapped_column(ForeignKey("operating_rooms.id"), nullable=False)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")

    operating_room: Mapped[OperatingRoom] = relationship(back_populates="sessions")
    patient: Mapped[Patient] = relationship(back_populates="sessions")
    events: Mapped[List["AlertEvent"]] = relationship(back_populates="session")


class AlertEvent(db.Model):
    """Alert triggered during a monitoring session."""

    __tablename__ = "alert_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("monitoring_sessions.id"), nullable=False)
    rule_id: Mapped[int] = mapped_column(ForeignKey("alert_rules.id"), nullable=False)
    value: Mapped[Optional[float]] = mapped_column()
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    dify_response: Mapped[Optional[str]] = mapped_column(Text)

    session: Mapped[MonitoringSession] = relationship(back_populates="events")
    rule: Mapped[AlertRule] = relationship()
