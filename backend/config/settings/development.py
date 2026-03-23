"""Development settings — extends base."""
from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Use SQLite as H2-equivalent for local development
# Full ORM abstraction means zero code changes when migrating to PostgreSQL/MySQL
DATABASES["default"]["ENGINE"] = "django.db.backends.sqlite3"
DATABASES["default"]["NAME"] = BASE_DIR / "dev.sqlite3"

# Relax CORS for local dev
CORS_ALLOW_ALL_ORIGINS = True

# Django debug toolbar (optional)
try:
    import debug_toolbar  # noqa
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = ["127.0.0.1"]
except ImportError:
    pass

# Celery — run tasks eagerly in development if no broker available
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
