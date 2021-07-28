from flask import Flask
from flask_session import Session
from sqlalchemy.engine.url import make_url
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.exc import OperationalError, ProgrammingError

from app.view_jobs import jobs
from app.view_users import users
from app.models import db, Roles


def create_app(config='app.config.Config'):
    app = Flask(__name__)
    with app.app_context():
        app.config.from_object(config)
        init_db(app)
        app.db = db

    app.register_blueprint(jobs)
    app.register_blueprint(users)
    Session(app)
    return app


def init_db(app):
    url = make_url(app.config["DATABASE_URL"])
    db.init_app(app)
    db.app = app
    try:
        if not database_exists(url):
            create_database(url)
        db.create_all()
    except OperationalError:
        db.create_all()
    except ProgrammingError:
        pass
    else:
        db.create_all()
    Roles.init_roles()