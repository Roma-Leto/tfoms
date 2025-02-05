import json
from random import randint
from time import sleep

from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from pyexpat.errors import messages


class WSConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

        for i in range(1000):
            self.send(json.dumps({'message': randint(1, 100)}))
            sleep(1)

    def receive(self, text_data=None, bytes_data=None):
        if text_data:
            self.send(text_data=f"Принято сообщение {text_data}")

    def disconnect(self, code):
        pass
