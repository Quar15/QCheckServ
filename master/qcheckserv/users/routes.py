from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from qcheckserv import db, bcrypt
from qcheckserv.users.models import User
from qcheckserv.users.forms import LoginForm, RegistrationForm


users = Blueprint('users', __name__)


@users.route("/users/list", methods=['GET', 'POST'])
def user_list():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.id).paginate(page=page, per_page=50)
    print(users.items)
    return render_template('partials/user/list.html', users=users)


@users.route("/users/<id>/edit", methods=['GET', 'POST'])
def user_edit(id: int):
    return ''


@users.route("/users/<id>/delete", methods=['GET', 'POST'])
def user_delete(id: int):
    return ''


@users.route("/users/create", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, pretty_name=form.pretty_name.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Account '{user.username}' created", 'success')
    return render_template('users/create.html', title='Register', form=form)


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
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('users.login'))