import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "HOST": "127.0.0.1",
        "PORT": 5432,
        "NAME": "onlinejudge",
        "USER": "onlinejudge",
        "PASSWORD": "onlinejudge",
        "OPTIONS": {"sslmode": "allow"}
    }
}

REDIS_URL = "redis://127.0.0.1:6380"

DEBUG = True

ALLOWED_HOSTS = ["*"]

DATA_DIR = f"{BASE_DIR}/data"
