from .common import *

SECRET_KEY = 'development-secret-key'

DEBUG = True

ALLOWED_HOSTS = ['*']

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}