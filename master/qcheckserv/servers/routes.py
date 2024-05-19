from flask import render_template, Blueprint, request, url_for, redirect, flash, session, make_response
from flask_login import login_required
from wtforms import BooleanField, StringField
from qcheckserv import db
from qcheckserv.servers.models import Server, ServerData, ServerGroup
from qcheckserv.servers.forms import ServerGroupCreationForm
from qcheckserv.servers.utils import ServerDataResponse
from qcheckserv.main.utils import add_notification_refresh_header, admin_required
from qcheckserv.users.models import User
from datetime import datetime, timedelta

servers = Blueprint('servers', __name__)
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


@servers.route("/server-list")
@login_required
@add_notification_refresh_header
def server_list():
    server_groups = ServerGroup.query.all()
    servers = Server.query.all()
    server_groups.append({'name': 'All', 'servers': servers})
    return render_template("partials/server/list.html", server_groups=server_groups)


@servers.route("/server/group/list")
@login_required
@add_notification_refresh_header
def server_group_list():
    server_groups = ServerGroup.query.all()
    return render_template("partials/server/group/list.html", server_groups=server_groups)


@servers.route("/server/group/<id>/delete")
@login_required
@admin_required
def server_group_list_delete(id: int):
    group = ServerGroup.query.get_or_404(id)
    group_name = group.name
    db.session.delete(group)
    db.session.commit()
    flash(f"Group '{group_name}' has been deleted", 'success')
    session['flash_message_available'] = True
    return redirect(url_for('servers.server_group_list'))


@servers.route("/server/group/<id>/edit", methods=['POST', 'GET'])
@login_required
@admin_required
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
        form.submit.label.text = 'Update'
    
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
@login_required
@admin_required
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


def get_labels_and_datetimes_in_timeframe(timestamp_since, timestamp_to):
    labels = []
    datetimes = []
    x = timestamp_to
    x = x.replace(second=0)
    while x.minute % 5 != 0:
        x -= timedelta(minutes=1)
    while x >= timestamp_since:
        labels.append(datetime.strftime(x, DATETIME_FORMAT))
        datetimes.append(x)
        x -= timedelta(minutes=5)
    return labels, datetimes


def get_timestamps(request, earliest_timestamp):
    default_values = True
    timestamp_since = request.args.get('since', default=None)
    if timestamp_since is None:
        timestamp_since = (datetime.now() - timedelta(hours = 3))
    else:
        timestamp_since = datetime.strptime(timestamp_since, DATETIME_FORMAT)
        default_values = False
    timestamp_since  = timestamp_since.replace(second=0, microsecond=0)

    timestamp_to = request.args.get('to', default=None)
    if timestamp_to is None:
        timestamp_to = datetime.now()
    else:
        timestamp_to = datetime.strptime(timestamp_to, DATETIME_FORMAT)
        default_values = False
    timestamp_to  = timestamp_to.replace(second=0, microsecond=0)

    if timestamp_since < earliest_timestamp:
        timestamp_since = earliest_timestamp

    if (timestamp_to < timestamp_since):
        return (datetime.now() - timedelta(hours = 3)), datetime.now()

    return timestamp_since, timestamp_to, default_values


@servers.route("/server/<id>")
@login_required
def server_details(id: int):
    server = Server.query.get(id)
    earliest_timestamp = ServerData.query.filter_by(server_id=id).order_by(ServerData.timestamp).first().timestamp
    timestamp_since, timestamp_to, should_refresh_on_new_data = get_timestamps(request, earliest_timestamp)
    # @TODO: Add generalization of data for higher timeframes
    values = (ServerData
        .query
        .filter_by(server_id=id)
        .filter(ServerData.timestamp >= timestamp_since)
        .filter(ServerData.timestamp <= timestamp_to)
        .order_by(ServerData.timestamp.desc())
        .limit(1000)
        .all()
    )
    values.reverse()
    # Labels should be generated for every 5 minutes and values not in timeframe should have empty elements
    labels, datetimes = get_labels_and_datetimes_in_timeframe(timestamp_since, timestamp_to)
    server_data_response = ServerDataResponse()
    for dt in datetimes:
        value_for_datetime = 'ERROR'
        for val in values:
            if abs((dt - val.timestamp).total_seconds()) < 50:
                value_for_datetime = val
                break
        server_data_response.append_value(value_for_datetime)
    server_data_response.try_to_fix_partitions_data()
    return render_template(
        "partials/server/details.html", 
        server=server, 
        labels=labels, 
        server_data_response=server_data_response,
        since=timestamp_since,
        to=timestamp_to,
        should_refresh_on_new_data=should_refresh_on_new_data,
        last_data_timestamp=datetimes[0],
    )


@servers.route("/server/<id>/check")
@login_required
def server_details_changed(id: int):
    server = Server.query.get(id)
    last_data_timestamp = request.args.get('last_data_timestamp', default=None)
    if last_data_timestamp is None:
        return '', 400
    else:
        last_data_timestamp = datetime.strptime(last_data_timestamp, DATETIME_FORMAT)
    
    latest_server_data = (ServerData
        .query
        .filter_by(server_id=id)
        .filter(ServerData.timestamp > last_data_timestamp)
        .order_by(ServerData.timestamp.desc())
        .limit(1)
        .first()
    )

    resp = make_response("", 200)
    if latest_server_data and latest_server_data.timestamp > last_data_timestamp:
        resp.headers["HX-Trigger"] = "newServerData"
    return resp