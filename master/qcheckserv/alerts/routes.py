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


@alerts.route("/alert/notification/create")
@login_required
@admin_required
def alert_notification_create():
    return render_template('alerts/create_notification.html')


@alerts.route("/alert/notification/edit")
@login_required
@admin_required
def alert_notification_edit():
    return render_template('alerts/create_notification.html')


@alerts.route("/alert/notification/delete")
@login_required
@admin_required
def alert_notification_delete():
    return redirect(url_for('alerts.alerts_list'))


@alerts.route("/alert/trigger/create")
@login_required
@admin_required
def alert_trigger_create():
    return render_template('alerts/create_trigger.html')


@alerts.route("/alert/trigger/edit")
@login_required
@admin_required
def alert_trigger_edit():
    return render_template('alerts/create_trigger.html')


@alerts.route("/alert/trigger/delete")
@login_required
@admin_required
def alert_trigger_delete():
    return redirect(url_for('alerts.alerts_list'))