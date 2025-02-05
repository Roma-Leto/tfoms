"""
ASGI config for x_tfoms_project project.
It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os

from channels.routing import get_default_application
from django.core.asgi import get_asgi_application

from x_tfoms_project.wsgi import application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'x_tfoms_project.settings')

# application = get_asgi_application()
application = get_default_application()
