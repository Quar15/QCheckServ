from datetime import datetime
from qcheckserv import db
from qcheckserv.alerts.utils import (
    EnumAlertNotificationType, 
    EnumAlertStatus, 
    EnumAlertTriggerTypeComparator, 
    EnumTriggerTypeEnum
)


class AlertTrigger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    trigger_type = db.Column(db.Enum(EnumTriggerTypeEnum), nullable=False)
    details = db.Column(db.JSON, nullable=False)

    definition = db.relationship('AlertDefinition', backref='trigger', lazy=True)


class AlertNotification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notification_type = db.Column(db.Enum(EnumTriggerTypeEnum), nullable=False)
    details = db.Column(db.JSON, nullable=False)

    definition = db.relationship('AlertDefinition', backref='notification', lazy=True)


class AlertDefinition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'), nullable=False)
    alert_trigger_id = db.Column(db.Integer, db.ForeignKey('alert_trigger.id'), nullable=False)
    alert_notification_id = db.Column(db.Integer, db.ForeignKey('alert_notification.id'), nullable=False)

    alerts = db.relationship('Alert', backref='definition', lazy=False)


class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    alert_definition_id = db.Column(db.Integer, db.ForeignKey('alert_definition.id'), nullable=False)