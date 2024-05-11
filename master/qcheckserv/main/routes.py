from flask import render_template, Blueprint
from flask_login import login_required
from qcheckserv.api.models import Server, ServerData, ServerGroup

main = Blueprint('main', __name__)


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
    return render_template("partials/server_details.html", server=server)


@main.route("/heartbeat")
def heartbeat():
    return ""