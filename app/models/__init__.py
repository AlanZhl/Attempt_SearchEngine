# create the database object and provide all the table classes
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .users import Permissions, Users, Roles
from .jobs import JobPost