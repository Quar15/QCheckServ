from flask import render_template, Blueprint, request, url_for, redirect, flash
from flask_login import login_required
from wtforms import BooleanField, StringField
from qcheckserv import db
from qcheckserv.servers.models import Server, ServerData, ServerGroup
from qcheckserv.servers.forms import ServerGroupCreationForm
from qcheckserv.users.models import User
from datetime import datetime

servers = Blueprint('servers', __name__)
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


@servers.route("/server-list")
def server_list():
    server_groups = ServerGroup.query.all()
    servers = Server.query.all()
    server_groups.append({'name': 'All', 'servers': servers})
    return render_template("partials/server/list.html", server_groups=server_groups)


@servers.route("/server/group/list")
def server_group_list():
    server_groups = ServerGroup.query.all()
    return render_template("partials/server/group/list.html", server_groups=server_groups)


@servers.route("/server/group/<id>/delete")
def server_group_list_delete(id: int):
    group = ServerGroup.query.get_or_404(id)
    group_name = group.name
    db.session.delete(group)
    db.session.commit()
    flash(f"Group '{group_name}' has been deleted", 'success')
    return redirect(url_for('servers.server_group_list'))


@servers.route("/server/group/<id>/edit", methods=['POST', 'GET'])
def server_group_list_edit(id: int):
    server_group = ServerGroup.query.get_or_404(id)
    servers = Server.query.all()
    for s in servers:
        if s in server_group.servers:
            setattr(ServerGroupCreationForm, s.hostname, BooleanField(s.hostname, default='checked'))
        else:
            setattr(ServerGroupCreationForm, s.hostname, BooleanField(s.hostname))
    form = ServerGroupCreationForm()
    if form.validate_on_submit():
        server_group.name = form.name.data
        server_group.servers = []
        for s in servers:
            if form[s.hostname].data:
                server_group.servers.append(s)
        db.session.commit()
        flash(f"Server Group '{server_group.name}' updated", 'success')
        return redirect(url_for('main.index', list='groups'))
    elif request.method == 'GET':
        form.server_group_id.data = server_group.id
        form.name.data = server_group.name
        servers = Server.query.all()
    
    n_hosts = Server.query.count()
    n_groups = ServerGroup.query.count()
    n_users = User.query.count()
    return render_template(
        'servers/create_group.html', 
        title='Update Group', 
        form=form,
        action_url=url_for('servers.server_group_list_edit', id=server_group.id),
        servers=servers,
        n_hosts=n_hosts,
        n_groups=n_groups,
        n_users=n_users,
    )


@servers.route("/server/group/create", methods=['POST', 'GET'])
def server_group_list_create():
    servers = Server.query.all()
    for s in servers:
        setattr(ServerGroupCreationForm, s.hostname, BooleanField(s.hostname))
    form = ServerGroupCreationForm()
    if form.validate_on_submit():
        servers_in_group = []
        for s in servers:
            if form[s.hostname].data:
                servers_in_group.append(s)
        server_group = ServerGroup(name=form.name.data, servers=servers_in_group)
        db.session.add(server_group)
        db.session.commit()
        flash(f"Server Group '{server_group.name}' created", 'success')
        return redirect(url_for('main.index', list='groups'))
    n_hosts = Server.query.count()
    n_groups = ServerGroup.query.count()
    n_users = User.query.count()
    return render_template(
        'servers/create_group.html', 
        title='Create Group', 
        form=form,
        action_url=url_for('servers.server_group_list_create'),
        servers=servers,
        n_hosts=n_hosts,
        n_groups=n_groups,
        n_users=n_users,
    )


@servers.route("/server/<id>")
def server_details(id: int):
    server = Server.query.get(id)
    values = ServerData.query.filter_by(server_id=id).order_by(ServerData.timestamp.desc()).limit(13).all()
    values.reverse()
    # @TODO: labels should be generated for every 5 minutes and values not in timeframe should have empty elements
    labels = [datetime.strftime(val.timestamp, DATETIME_FORMAT) for val in values]
    values_cpu = [val.cpu_perc for val in values]
    values_loadavg = [val.loadavg for val in values] 
    values_mem = [val.mem_perc for val in values]
    values_partitions = [val.partitions for val in values]
    values_bytes_received = [val.bytes_received / 1024 / 1024 for val in values]
    values_bytes_sent = [val.bytes_sent / 1024 / 1024  for val in values]
    return render_template(
        "partials/server/details.html", 
        server=server, 
        labels=labels, 
        values_cpu=values_cpu,
        values_loadavg=values_loadavg,
        values_mem=values_mem,
        values_partitions=values_partitions,
        values_bytes_received=values_bytes_received,
        values_bytes_sent=values_bytes_sent,
    )