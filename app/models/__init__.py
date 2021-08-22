# create the database object and provide all the table classes
from flask_sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch
import redis

from app.config import Config

db = SQLAlchemy()
es = Elasticsearch("localhost:9200")
# test: only used for general history recording
redis_pool = redis.ConnectionPool(host=Config.REDIS_HOST, port=Config.REDIS_PORT)

from .users import Permissions, Users, Roles
from .jobs import JobPost
from .jobs_es import create_es
from .errors import MyError