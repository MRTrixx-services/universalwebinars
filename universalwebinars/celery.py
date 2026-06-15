import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "universalwebinars.settings")

app = Celery("universalwebinars")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()