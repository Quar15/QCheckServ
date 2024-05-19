from qcheckserv.servers.models import ServerServerGroupHelper, Server, ServerData, ServerGroup
from qcheckserv.alerts.models import AlertDefinition, AlertNotification, AlertTrigger
from qcheckserv.users.models import User
from qcheckserv import create_app, db

app = create_app()
with app.app_context():
    db.create_all()