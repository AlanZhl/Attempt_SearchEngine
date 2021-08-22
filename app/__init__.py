from flask import Flask
from flask_session import Session
from sqlalchemy.engine.url import make_url
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.exc import OperationalError, ProgrammingError

# from app.jobscrawler import init_jobposts
from app.view_jobs import jobs
from app.view_users import users
from app.models import db, es, Roles, create_es
from app.common import Redis_Handler
from app.config import Config


def create_app(config='app.config.Config'):
    app = Flask(__name__)
    with app.app_context():
        app.config.from_object(config)
        init_redis(app)
        init_db(app)
        app.db = db
        create_es(es)

    app.register_blueprint(jobs)
    app.register_blueprint(users)
    Session(app)
    return app


def init_redis(app):
    redis_handler = Redis_Handler()
    r = redis_handler.get_redis_instance()
    session_lst = r.keys(Config.SESSION_KEY_PREFIX + "*")
    if session_lst:
        r.delete(*session_lst)
    app.config["SESSION_REDIS"] = r


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