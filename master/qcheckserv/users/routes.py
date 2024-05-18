from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from qcheckserv import db, bcrypt
from qcheckserv.users.models import User
from qcheckserv.servers.models import Server, ServerGroup
from qcheckserv.users.forms import LoginForm, RegistrationForm, UserEditForm


users = Blueprint('users', __name__)


@users.route("/users/partial/list", methods=['GET', 'POST'])
@login_required
def user_list():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.id).paginate(page=page, per_page=50)
    return render_template('partials/user/list.html', users=users)


@users.route("/users/<id>/edit", methods=['GET', 'POST'])
@login_required
def user_edit(id: int):
    user = User.query.get_or_404(id)
    form = UserEditForm()
    if form.validate_on_submit():
        if form.password.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hashed_password
        user.username = form.username.data
        user.pretty_name = form.pretty_name.data
        user.role=form.user_role.data
        db.session.commit()
        flash(f"Account '{user.username}' has been updated", 'success')
        return redirect(url_for('users.user_list', list="users"))
    elif request.method == 'GET':
        form.user_id.data = user.id
        form.username.data = user.username
        form.pretty_name.data = user.pretty_name
        form.user_role.data = user.role.name
    n_hosts = Server.query.count()
    n_groups = ServerGroup.query.count()
    n_users = User.query.count()
    return render_template(
        'users/create.html', 
        title='Update User',
        form=form,
        action_url=url_for('users.user_edit', id=user.id),
        n_hosts=n_hosts,
        n_groups=n_groups,
        n_users=n_users,
    )


@users.route("/users/<id>/delete", methods=['GET', 'POST'])
@login_required
def user_delete(id: int):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash(f"Cannot remove current account", 'error')
        return redirect(url_for('users.user_list'))
    user_name = user.pretty_name
    db.session.delete(user)
    db.session.commit()
    flash(f"User '{user_name}' has been deleted", 'success')
    return redirect(url_for('users.user_list'))


@users.route("/users/create", methods=['GET', 'POST'])
@login_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, pretty_name=form.pretty_name.data, password=hashed_password, role=form.user_role.data)
        db.session.add(user)
        db.session.commit()
        flash(f"Account '{user.username}' created", 'success')
        return redirect(url_for('users.user_list'))
    n_hosts = Server.query.count()
    n_groups = ServerGroup.query.count()
    n_users = User.query.count()
    return render_template(
        'users/create.html', 
        title='Create User', 
        action_url=url_for('users.register'),
        form=form,
        n_hosts=n_hosts,
        n_groups=n_groups,
        n_users=n_users,
    )


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Logged in as {user.pretty_name}', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('users.login'))