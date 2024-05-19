from flask import render_template, Blueprint, request, url_for, make_response, flash
from flask_login import login_required
from qcheckserv.main.utils import admin_required, add_notification_refresh_header
from qcheckserv.alerts.models import Alert, AlertDefinition, AlertNotification, AlertTrigger

alerts = Blueprint('alerts', __name__)


@alerts.route("/alerts-list")
@login_required
@add_notification_refresh_header
def alerts_list():
    alert_definitions = AlertDefinition.query.all()
    alerts = Alert.query.all()
    return render_template(
        "partials/alert/list.html", 
        alert_definitions=alert_definitions,
        alerts=alerts,
    )


@alerts.route("/alert/definition/create")
@login_required
@admin_required
def alert_definition_create():
    return render_template('alerts/create_definition.html')


@alerts.route("/alert/definition/edit")
@login_required
@admin_required
def alert_definition_edit():
    return render_template('alerts/create_definition.html')


@alerts.route("/alert/definition/delete")
@login_required
@admin_required
def alert_definition_delete():
    return redirect(url_for('alerts.alerts_list'))