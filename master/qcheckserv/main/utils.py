from flask import session, make_response, redirect, url_for, flash
from flask_login import current_user
from functools import wraps
from qcheckserv.users.enum_user_role import EnumUserRole


def admin_required(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        if current_user.role != EnumUserRole.ADMIN:
            flash('Unauthorized', 'error')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return wrap


def add_notification_refresh_header(viewmethod):
    @wraps(viewmethod)
    def new_viewmethod(*args, **kwargs):
        resp = make_response(viewmethod(*args, **kwargs))
        if 'flash_message_available' in session and session['flash_message_available']:
            resp.headers["HX-Trigger"] = "newNotification"
            session['flash_message_available'] = False
        return resp
    return new_viewmethod