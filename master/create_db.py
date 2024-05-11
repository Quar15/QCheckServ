from qcheckserv.api.models import Server, ServerData, ServerGroup, ServerServerGroupHelper
from qcheckserv.users.models import User
from qcheckserv import create_app, db

app = create_app()
with app.app_context():
    db.create_all()