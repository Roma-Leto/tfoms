#!/usr/bin/env python
""" Настройка приложения Celery """
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'x_tfoms_project.settings')

app = Celery(
    'tfoms_celery',
    namespace='CELERY',
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True
)

app.config_from_object('django.conf:settings')

app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')