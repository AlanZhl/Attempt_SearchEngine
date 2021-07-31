# create the database object and provide all the table classes
from flask_sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch

db = SQLAlchemy()
es = Elasticsearch()

from .users import Permissions, Users, Roles
from .jobs import JobPost
from .jobs_es import create_es