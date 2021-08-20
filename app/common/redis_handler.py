import redis

from app.config import Config


class Redis_Handler():
    def __init__(self):
        self._host = Config.REDIS_HOST
        self._port = Config.REDIS_PORT

    def get_redis_instance(self):
        if not self._host or not self._port:
            return None
        redis_pool = redis.ConnectionPool(host=self._host, port=self._port)
        return redis.Redis(connection_pool=redis_pool)
