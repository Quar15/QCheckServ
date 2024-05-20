import operator
from datetime import datetime
from qcheckserv import db
from qcheckserv.servers.models import Server
from qcheckserv.alerts.utils import (
    EnumAlertNotificationType, 
    EnumAlertStatus, 
    EnumAlertTriggerTypeComparator, 
    EnumTriggerTypeEnum,
    EnumServerResourceType,
    EnumStorageResourceType,
    EnumNetworkResourceType,
)


class AlertTrigger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    trigger_type = db.Column(db.Enum(EnumTriggerTypeEnum), nullable=False)
    details = db.Column(db.JSON, nullable=False)

    definition = db.relationship('AlertDefinition', backref='trigger', lazy=True)

    def __repr__(self) -> str:
        return f"AlertTrigger({self.id}, {self.trigger_type}, {self.details})"


    def is_triggered(self):
        return False


class AlertNotification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notification_type = db.Column(db.Enum(EnumAlertNotificationType), nullable=False)
    details = db.Column(db.JSON, nullable=False)

    definition = db.relationship('AlertDefinition', backref='notification', lazy=True)


class AlertDefinitionServerHelper(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    alert_definition = db.Column("alert_definition_id", db.Integer, db.ForeignKey("alert_definition.id"))
    server_id = db.Column("server_id", db.Integer, db.ForeignKey("server.id"))


class AlertDefinition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    alert_trigger_id = db.Column(db.Integer, db.ForeignKey('alert_trigger.id'), nullable=False)
    alert_notification_id = db.Column(db.Integer, db.ForeignKey('alert_notification.id'), nullable=False)

    alerts = db.relationship('Alert', backref='definition', lazy=False)
    servers = db.relationship(
        'Server',
        secondary='alert_definition_server_helper',
        backref='alert_definitions',
        lazy=True
    )

    def __repr__(self) -> str:
        return f"AlertDefinition({self.id}, {self.alert_trigger_id}, {self.alert_notification_id}, {self.servers})"

    def is_triggered(self) -> bool:
        print(self.trigger)
        trigger = AlertTriggerFactory().get_alert(self.trigger)
        return trigger.is_triggered()


class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    alert_definition_id = db.Column(db.Integer, db.ForeignKey('alert_definition.id'), nullable=False)
    server_id = db.Column(db.Integer, db.ForeignKey('server.id'), nullable=False)


class AlertTriggerObject():
    def __init__(self, alert_trigger: 'AlertTrigger'):
        self.id = alert_trigger.id
        self.created_at = alert_trigger.created_at
        self.updated_at = alert_trigger.updated_at
        self.trigger_type = alert_trigger.trigger_type
        self.details = alert_trigger.details
        self.definition = alert_trigger.definition[0]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id}, {self.trigger_type}, {self.details})"

    def is_triggered(self) -> bool:
        return False

    def get_comparator(self):
        match(self.details["comparator"]):
            case EnumAlertTriggerTypeComparator.BIGGER:
                return operator.gt
            case EnumAlertTriggerTypeComparator.BIGGER_EQUAL:
                return operator.ge
            case EnumAlertTriggerTypeComparator.LESS:
                return operator.lt
            case EnumAlertTriggerTypeComparator.LESS_EQUAL:
                return operator.le
            case EnumAlertTriggerTypeComparator.EQUAL:
                return operator.eq
            case _:
                raise ValueError(f"{self.details['comparator']} is not valid EnumAlertTriggerTypeComparator")

    def get_event_duration(self, begin_datetime):
        return abs(begin_datetime - datetime.now()).total_seconds()

    def event_duration_is_longer_than_trigger_duration(self, begin_datetime) -> bool:
        return self.get_event_duration(begin_datetime) > self.details['duration']

    def save(self) -> None:
        alert = AlertTrigger.query.get(self.id)
        alert.id = self.id
        alert.created_at = self.created_at
        alert.updated_at = self.updated_at
        alert.trigger_type = self.trigger_type
        alert.details = self.details
        alert.definition = self.definition
        db.session.add(alert)
        db.session.commit()


class AlertTriggerStatus(AlertTriggerObject):
    def is_triggered(self):
        connected_servers = self.definition.servers
        for server in connected_servers:
            server_data = server.get_last_data()
            if self.event_duration_is_longer_than_trigger_duration(server_data.timestamp):
                return True
        return False


class AlertTriggerPercentageUsage(AlertTriggerObject):
    def is_triggered(self):
        comp = self.get_comparator()
        connected_servers = self.definition.servers
        for server in connected_servers:
            server_data = server.get_last_data()
            server_data_value = None
            match(self.details["resource_type"]):
                case EnumServerResourceType.CPU_PERC.value:
                    server_data_value = server_data.cpu_perc
                case EnumServerResourceType.MEM_PERC.value:
                    server_data_value = server_data.mem_perc
                case _:
                    raise ValueError(self.details["resource_type"])
            if comp(server_data_value, self.details["value"]):
                    return True
        return False


class AlertTriggerStorage(AlertTriggerObject):
    def is_triggered(self):
        comp = self.get_comparator()
        connected_servers = self.definition.servers
        for server in connected_servers:
            server_data = server.get_last_data()
            mountpoints_of_interest = [p["mountpoint"] for p in self.details['partitions']]
            for partition in server_data.partitions:
                if partition["mountpoint"] in mountpoints_of_interest:
                    match(self.details["storage_resource_type"]):
                        case EnumStorageResourceType.INODES_PERC.value:
                            server_data_value = (partition["inodes_free"] / partition["inodes_files"])
                        case EnumStorageResourceType.USAGE_PERC.value:
                            server_data_value = partition["usage_perc"]
                        case EnumStorageResourceType.USED.value:
                            server_data_value = partition["used"]
                        case _:
                            raise ValueError(f"{self.details['storage_resource_type']} is not valid")
                    if comp(server_data_value, self.details["value"]):
                        return True 
        return False


class AlertTriggerLoadAvg(AlertTriggerObject):
    def is_triggered(self):
        comp = self.get_comparator()
        connected_servers = self.definition.servers
        for server in connected_servers:
            server_data = server.get_last_data()
            server_data_value = server_data.loadavg[1]
            if comp(server_data_value, self.details["value"]):
                return True
        return False


class AlertTriggerNetwork(AlertTriggerObject):
    def is_triggered(self):
        comp = self.get_comparator()
        connected_servers = self.definition.servers
        for server in connected_servers:
            server_data = server.get_last_data()
            match(self.details['network_resource_type']):
                case EnumNetworkResourceType.DOWNLOAD.value:
                    server_data_value = server_data.bytes_received
                case EnumNetworkResourceType.UPLOAD.value:
                    server_data_value = server_data.bytes_sent
                case _:
                    raise ValueError(f"{self.details['network_resource_type']} is not valid EnumNetworkResourceType")
            print(server_data_value, self.details["value"])
            if comp(server_data_value, self.details["value"]):
                return True
        return False


class AlertTriggerFactory():
    def get_alert(self, alert_trigger_record: 'AlertTrigger') -> 'AlertTrigger':
        match(alert_trigger_record.trigger_type):
            case EnumTriggerTypeEnum.STATUS:
                return AlertTriggerStatus(alert_trigger_record)
            case EnumTriggerTypeEnum.PERCENTAGE_USAGE:
                return AlertTriggerPercentageUsage(alert_trigger_record)
            case EnumTriggerTypeEnum.STORAGE:
                return AlertTriggerStorage(alert_trigger_record)
            case EnumTriggerTypeEnum.LOAD_AVG:
                return AlertTriggerLoadAvg(alert_trigger_record)
            case EnumTriggerTypeEnum.NETWORK:
                return AlertTriggerNetwork(alert_trigger_record)
            case _:
                return ValueError(alert_trigger_record) 