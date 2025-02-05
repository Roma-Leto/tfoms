from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from invoice.consumers import WSConsumer


# from x_tfoms_project.asgi import application

ws_urlpatterns = [
    path('ws/count/', WSConsumer.as_asgi())
]
