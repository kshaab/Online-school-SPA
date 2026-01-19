from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "online_school.settings")

app = Celery("online_school")

app.config_from_object("online_school.settings", namespace="CELERY")

app.autodiscover_tasks()
