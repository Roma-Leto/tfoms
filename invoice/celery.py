from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'x_tfoms_project.settings')
# app = Celery('x_tfoms_project')
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.autodiscover_tasks()


# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'x_tfoms_project.settings')

app = Celery('myproject')

# Используем настройки Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически загружаем задачи из всех зарегистрированных приложений Django
app.autodiscover_tasks()