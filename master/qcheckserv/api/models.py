from qcheckserv import db
from datetime import datetime


class Server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(255), unique=True, nullable=False)

    data = db.relationship('ServerData', backref='server', lazy=False)
    server_group = db.relationship(
        'ServerGroup',
        secondary='server_server_group_helper',
        back_populates='servers',
        lazy=True
    )
    
    def get_last_data(self) -> 'ServerData':
        return ServerData.query.filter_by(server_id=self.id).order_by(ServerData.timestamp).first()

    def __repr__(self):
        return f"Server({self.id}, '{self.hostname}')"


class ServerData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cpu_perc = db.Column(db.Float, nullable=False)
    loadavg = db.Column(db.JSON, nullable=False)
    mem_perc = db.Column(db.Float, nullable=False)
    partitions = db.Column(db.JSON, nullable=False)
    bytes_received = db.Column(db.Integer, nullable=True)
    bytes_sent = db.Column(db.Integer, nullable=True)

    server_id = db.Column(db.Integer, db.ForeignKey('server.id'), nullable=False)

    def __repr__(self):
        return f"ServerData({self.id}, {self.timestamp}, {self.server_id})"


class ServerServerGroupHelper(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    server_id = db.Column("server_id", db.Integer, db.ForeignKey("server.id"))
    server_group_id = db.Column("server_group_id", db.Integer, db.ForeignKey("server_group.id"))


class ServerGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    servers = db.relationship(
        'Server',
        secondary='server_server_group_helper',
        back_populates='server_group',
        lazy=True
    )

    def __repr__(self):
        return f"ServerGroup({self.id}, {self.name})"