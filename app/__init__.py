from flask import Flask
from flask_session import Session

from app.jobs import jobs
from app.users import users


def create_app(config='app.config.Config'):
    app = Flask(__name__)
    with app.app_context():
        app.config.from_object(config)
        # init_db(app)
        # app.db = db

    app.register_blueprint(jobs)
    app.register_blueprint(users)
    Session(app)
    return app