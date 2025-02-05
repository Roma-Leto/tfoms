"""
ASGI config for x_tfoms_project project.
It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from invoice.routing import ws_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'x_tfoms_project.settings')

django_asgi_app = get_asgi_application()



# from routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            ws_urlpatterns
        )
    )
})