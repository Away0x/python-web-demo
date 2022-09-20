from .common import *

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

DEBUG = False

ALLOWED_HOSTS = ['hellodjango-blog.tongwu.com']

CACHES = {
    "default": {
        "BACKEND": "redis_cache.RedisCache",
        "LOCATION": "redis://:UJaoRZlNrH40BDaWU6fi@redis:6379/0",
        "OPTIONS": {
            "CONNECTION_POOL_CLASS": "redis.BlockingConnectionPool",
            "CONNECTION_POOL_CLASS_KWARGS": {"max_connections": 50, "timeout": 20},
            "MAX_CONNECTIONS": 1000,
            "PICKLE_VERSION": -1,
        },
    },
}