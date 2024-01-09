# consumers.py

import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # process the received message (e.g., update game state)

        await self.send(text_data=json.dumps({
            'message': message,
        }))

