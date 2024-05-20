from flask import url_for, request, Blueprint
import json
from datetime import datetime
from qcheckserv import db
from qcheckserv.servers.models import Server, ServerData
from qcheckserv.alerts.models import AlertDefinition


api = Blueprint('api', __name__)

DATETIME_FORMAT = "%Y-%m-%d %H:%M"

SERVER_CHECKER_PAYLOAD_VERSION = 2

VERSION = 'version'
TIMESTAMP = 'timestamp'
HOSTNAME = 'hostname'
CPU_PERC = 'cpu_perc'
LOADAVG = 'loadavg'
MEM_PERC = 'mem_perc'
PARTITIONS = 'partitions'
BYTES_RECEIVED = 'bytes_received'
BYTES_SENT = 'bytes_sent'


def handle_initial_request(request, req_elements):
    if not request.data:
        return False, '401', 401
    try:
        data = json.loads(request.data)
    except json.decoder.JSONDecodeError:
        return False, '400', 400
    if VERSION in data and data[VERSION] != SERVER_CHECKER_PAYLOAD_VERSION:
            return False, f"Old version of checker", 400
    for e in req_elements:
        if e not in data:
            return False, f"Missing '{e}'", 401
    return True, data, 200


@api.route("/api/gather/server", methods=['POST'])
def gather_server_data():
    req_elements = [VERSION, TIMESTAMP, HOSTNAME, CPU_PERC, LOADAVG, MEM_PERC, PARTITIONS, BYTES_RECEIVED, BYTES_SENT]
    success, data, status_code = handle_initial_request(request, req_elements)
    if not success:
        return data, status_code
    
    server = Server.query.filter_by(hostname=data[HOSTNAME]).first()
    if server is None:
        server = Server(hostname=data[HOSTNAME])
        db.session.add(server)
        db.session.commit()
    
    server_data = ServerData(
        timestamp = datetime.strptime(data[TIMESTAMP], DATETIME_FORMAT),
        cpu_perc = data[CPU_PERC],
        loadavg = data[LOADAVG],
        mem_perc = data[MEM_PERC],
        partitions = data[PARTITIONS],
        bytes_received = data[BYTES_RECEIVED],
        bytes_sent = data[BYTES_SENT],
        server_id = server.id
    )
    db.session.add(server_data)
    db.session.commit()

    return json.dumps(data), 200


@api.route('/api/alert/triggered')
def get_alerts():
    alert_definitions = AlertDefinition.query.all()
    triggered_alerts = []
    for alert_definition in alert_definitions:
        if (alert_definition.is_triggered()):
            triggered_alerts.append(f"{alert_definition}")
    return json.dumps(triggered_alerts)
