from qcheckserv import create_app
import os

app = create_app(os.getenv("QCHECKSERV_APP_CONFIG", "qcheckserv.config.DevelopmentConfig"))

if __name__ == "__main__":
    app.run(host="0.0.0.0")