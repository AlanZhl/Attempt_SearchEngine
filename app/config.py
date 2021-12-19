import os
import re


class Config():
    # database related
    SQLALCHEMY_DATABASE_URI = DATABASE_URL = "mysql+pymysql://dev:12345678@localhost/search_engine"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # session related
    SESSION_KEY = os.urandom(24)
    SESSION_TYPE = "redis"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = False
    SESSION_KEY_PREFIX = 'session_'
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    
    # all legal characters for a cookie (except for "&" and "+", which are used as delimiters)
    PATTERN = re.compile(r"[\w :!#$%'()\[\]{}\*+-./<=>?@^_`|~]")

    QUERY = {
        "_source": ['post_id'],
        "size": 300,
        "query": {
            "multi_match": {
                "query": "software",
                "type": "best_fields",
                "fields": ["title", "company", "description"],
                "tie_breaker": 0.3
            }
        }
    }