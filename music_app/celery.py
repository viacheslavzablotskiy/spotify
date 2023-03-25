from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'music_app.settings')
app = Celery('music_app')
app.config_from_object('django.conf:settings', namespace="CELERY")
app.autodiscover_tasks()
