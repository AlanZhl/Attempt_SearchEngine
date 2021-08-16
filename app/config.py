import os


class Config():
    SQLALCHEMY_DATABASE_URI = DATABASE_URL = "mysql+pymysql://dev:12345678@localhost/search_engine"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # session相关
    SESSION_KEY = os.urandom(24) # 这里方便起见就随便输入个字符串，可以随机生成保存
    SESSION_TYPE = "filesystem"
    FILE_PATH = os.getcwd() + r"\flask_session"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = False
    SESSION_KEY_PREFIX = 'session'

    QUERY = {
        "_source": ['post_id'],
        "size": 200,
        "query": {
            "multi_match": {
                "query": "software",
                "type": "best_fields",
                "fields": ["title", "description"],
                "tie_breaker": 0.3
            }
        }
    }    # return 200 results a time in real practice