from qcheckserv import db, login_manager
from qcheckserv.users.enum_user_role import EnumUserRole
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    pretty_name = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    role = db.Column(db.Enum(EnumUserRole), nullable=False, default=EnumUserRole.USER)

    def __repr__(self):
        return f"User({self.id}, '{self.username}')"