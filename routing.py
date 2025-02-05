from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path


from x_tfoms_project.asgi import application

application = ProtocolTypeRouter(
    {
        'websocket': URLRouter(
            [
                path('ws/', DataConsumers),
            ]
        )
    }
)