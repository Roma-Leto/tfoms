"""
Django settings for x_tfoms_project project.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-7058n%5*kp-^w&_=q0ss^a6=)*euok^&v7s2i2hs8ta_#3o_xn'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'localhost', '*'
]

# Application definition

INSTALLED_APPS = [
    'daphne',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'invoice',
    'django_bootstrap5',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'x_tfoms_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'x_tfoms_project.wsgi.application'
ASGI_APPLICATION = 'x_tfoms_project.asgi.application'



TEST_DB = False

# Database
if TEST_DB:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'mssql',
            'NAME': 'mtrnt',  # Имя базы данных
            'USER': 'leto',       # Имя пользователя
            'PASSWORD': '1MSLeto',   # Пароль
            'HOST': '192.168.0.12', # Адрес сервера
            'PORT': '1433',                # Порт (по умолчанию 1433 для MSSQL)
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server',  # Укажите версию драйвера
            },
        }
    }


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization

LANGUAGE_CODE = 'ru-Ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True
USE_L10N = False
USE_TZ = True

AUTH_USER_MODEL = 'users.User'

# superuser
# login - admin
# pass - admin

LOGIN_REDIRECT_URL = 'profile/'
LOGOUT_REDIRECT_URL = '/'

# Static files (CSS, JavaScript, Images)

STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR/'static',
]

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DATE_INPUT_FORMATS = ['%d.%m.%Y']  # Формат даты, например, 25-12-2023
DATE_FORMAT = ['%d.%m.%Y']

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'



# region Настройка логирования проекта

# Проверка на наличие папки для логов и создание в случае отсутствия
folder_name = 'logs'
LOG_DIR = os.path.join(BASE_DIR, folder_name)
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Конфигурация
LOGGING = {
    'version': 1,  # Версия конфигурации логирования
    'disable_existing_loggers': False,
    # Если False существующие логгеры не будут отключены
    'formatters': {  # Определяет формат вывода логов
        'verbose': {  # Подробный формат
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {  # Простой формат
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {  # Определяет куда отправлять логи
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'django.log'),
            # 'maxBytes': 1024 * 1024 * 5,  # 5 MB
            # 'backupCount': 5,  # Хранить 5 файлов
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {  # Определяет какие логгеры использовать
        'django': {  # Логгер для Django (уровень `INFO`)
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'invoice': {  # Логгер для приложения
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
# endregion

# region Celery + Redis
# Команда для Docker для выявления ip контейнера:
# docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' redis
REDIS_HOST = '172.17.0.2'
# REDIS_HOST = 'localhost'
# REDIS_HOST = 'redis'
REDIS_PORT = '6379'
CELERY_BROKER_URL = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 7200}
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# CELERY_BROKER_URL = 'redis://redis:6379/0'
# CELERY_RESULT_BACKEND = 'redis://redis:6379/0'

# endregion Celery + Redis
