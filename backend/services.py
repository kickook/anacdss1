"""Domain services for monitoring and alerting."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from sqlalchemy.orm import Session

from .config import CONFIG
from .dify_client import DifyPayload, get_client
from .models import AlertEvent, AlertRule, MonitoringParameter, MonitoringSession, OperatingRoom, Patient


@dataclass
class ParameterReading:
    """Represents a reading from a monitoring device."""

    parameter_id: int
    name: str
    value: float
    unit: Optional[str]


def evaluate_readings(session: MonitoringSession, readings: Iterable[ParameterReading], db_session: Session) -> List[AlertEvent]:
    """Evaluate incoming readings, persist alerts, and trigger Dify."""

    triggered_events: List[AlertEvent] = []
    dify_client = get_client()

    for reading in readings:
        parameter: MonitoringParameter = MonitoringParameter.query.get(reading.parameter_id)
        if not parameter:
            continue

        for rule in parameter.alert_rules:
            if _is_alert_triggered(rule, reading.value):
                alert_message = _compose_alert_message(rule, reading)
                payload = _build_payload(session, rule, reading, alert_message)
                dify_response = None
                try:
                    dify_response = dify_client.send_alert(payload).get("result")
                except Exception as exc:  # pragma: no cover - network failure path
                    dify_response = f"Failed to reach Dify: {exc}"

                event = AlertEvent(
                    session_id=session.id,
                    rule_id=rule.id,
                    value=reading.value,
                    dify_response=dify_response,
                )
                db_session.add(event)
                triggered_events.append(event)

    if triggered_events:
        db_session.commit()

    return triggered_events


def _is_alert_triggered(rule: AlertRule, value: float) -> bool:
    if rule.lower_bound is not None and value < rule.lower_bound:
        return True
    if rule.upper_bound is not None and value > rule.upper_bound:
        return True
    return False


def _compose_alert_message(rule: AlertRule, reading: ParameterReading) -> str:
    template = rule.message_template or "Parameter {name} out of range with value {value}{unit}."
    unit = f" {reading.unit}" if reading.unit else ""
    return template.format(name=reading.name, value=reading.value, unit=unit)


def _build_payload(session: MonitoringSession, rule: AlertRule, reading: ParameterReading, alert_message: str) -> DifyPayload:
    patient: Patient = session.patient
    operating_room: OperatingRoom = session.operating_room

    patient_info: Dict[str, Optional[str]] = {
        "name": patient.name,
        "age": str(patient.age) if patient.age is not None else None,
        "sex": patient.sex,
        "allergies": patient.allergies,
        "medication_plan": patient.medication_plan,
        "medical_record_number": patient.medical_record_number,
    }

    vitals: Dict[str, float] = {reading.name: reading.value}

    return DifyPayload(
        alert_message=alert_message,
        patient_info={k: v for k, v in patient_info.items() if v},
        vital_signs=vitals,
        operating_room=operating_room.name,
    )
