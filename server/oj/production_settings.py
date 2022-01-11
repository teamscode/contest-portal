from utils.shortcuts import get_env

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': get_env("POSTGRES_HOST", "oj-postgres"),
        'PORT': get_env("POSTGRES_PORT", "5432"),
        'NAME': get_env("POSTGRES_DB"),
        'USER': get_env("POSTGRES_USER"),
        'PASSWORD': get_env("POSTGRES_PASSWORD"),
        'OPTIONS': {'sslmode': 'get_env("DB_SSL_MODE", "allow")'}
    }
}

REDIS_URL = get_env("REDIS_URL", "redis://oj-redis:6379")

DEBUG = False

ALLOWED_HOSTS = ['*']

DATA_DIR = "/data"
