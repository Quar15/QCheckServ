from flask import render_template, Blueprint, request, url_for
from flask_login import login_required
from qcheckserv.servers.models import Server, ServerData, ServerGroup
from qcheckserv.users.models import User

main = Blueprint('main', __name__)


@main.route("/heartbeat")
def heartbeat():
    return ""


@main.route("/")
@login_required
def index():
    n_hosts = Server.query.count()
    n_groups = ServerGroup.query.count()
    n_users = User.query.count()
    list_to_show = request.args.get('list')
    match list_to_show:
        case 'groups':
            hx_get_list_url = url_for('servers.server_group_list')
        case 'users':
            hx_get_list_url = url_for('users.user_list')
        case _:
            hx_get_list_url = url_for('servers.server_list')
    
    return render_template(
        "index.html",
        n_hosts=n_hosts,
        n_groups=n_groups,
        n_users=n_users,
        hx_get_list_url=hx_get_list_url,
    )