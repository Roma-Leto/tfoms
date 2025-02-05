from channels.generic.websocket import AsyncWebsocketConsumer


class Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            await self.send(text_data=f"Принято сообщение {text_data}")

    async def disconnect(self, code):
        pass
