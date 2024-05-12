from flask import render_template, Blueprint
from flask_login import login_required
from qcheckserv.api.models import Server, ServerData, ServerGroup
from datetime import datetime

main = Blueprint('main', __name__)
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

@main.route("/")
def index():
    n_hosts = Server.query.count()
    n_groups = ServerGroup.query.count()
    return render_template("index.html", n_hosts=n_hosts, n_groups=n_groups)


@main.route("/server-list")
def server_list():
    server_groups = ServerGroup.query.all()
    servers = Server.query.all()
    server_groups.append(ServerGroup(name='All', servers=servers))
    return render_template("partials/server_list.html", server_groups=server_groups)


@main.route("/server/<id>")
def server_details(id: int):
    server = Server.query.get(id)
    values = ServerData.query.filter_by(server_id=id).order_by(ServerData.timestamp.desc()).limit(13).all()
    values.reverse()
    labels = [datetime.strftime(val.timestamp, DATETIME_FORMAT) for val in values]
    values_cpu = [val.cpu_perc for val in values]
    values_loadavg = [val.loadavg for val in values] 
    values_mem = [val.mem_perc for val in values]
    values_partitions = [val.partitions for val in values]
    values_bytes_received = [val.bytes_received / 1024 / 1024 for val in values]
    values_bytes_sent = [val.bytes_sent / 1024 / 1024  for val in values]
    return render_template(
        "partials/server_details.html", 
        server=server, 
        labels=labels, 
        values_cpu=values_cpu,
        values_loadavg=values_loadavg,
        values_mem=values_mem,
        values_partitions=values_partitions,
        values_bytes_received=values_bytes_received,
        values_bytes_sent=values_bytes_sent,
    )


@main.route("/heartbeat")
def heartbeat():
    return ""