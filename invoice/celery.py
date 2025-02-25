#!/usr/bin/env python
""" Настройка приложения Celery """
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'x_tfoms_project.settings')

app = Celery('inv_celery', namespace='CELERY_')

app.config_from_object('x_tfoms_project.settings')

app.autodiscover_tasks()

