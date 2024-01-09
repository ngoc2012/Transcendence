import json
from channels.generic.websocket import AsyncWebsocketConsumer
from views import rooms
from game.models import RoomsModel

user_channel = {}

class RoomsConsumer(AsyncWebsocketConsumer):
    global rooms
    global user_channel

    async def connect(self):
        user_id = self.scope.get('user')
        self.group_name = "rooms"

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Start a periodic task to update the room list every N seconds
        #await self.send_room_list_periodically()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        #data = json.loads(text_data)
        #message = text_data_json['message']
        rooms.add(text_data)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'update_rooms',
                'state': self.state,
            }
        )

    async def update_rooms(self, event):
        state = event['state']
        await self.send(text_data=json.dumps(rooms))

    #async def update_rooms(self, event):
    #    room_list = event['room_list']

    #    # Send the updated room list to the connected clients
    #    await self.send(text_data=json.dumps({
    #        'type': 'update_rooms',
    #        'room_list': room_list,
    #    }))

    #async def send_room_list_periodically(self):
    #    while True:
    #        # Get the updated room list (customize as needed)
    #        room_list = self.get_rooms_list()

    #        # Send the room list to the consumer group
    #        await self.channel_layer.group_send(
    #            "room_list",
    #            {
    #                'type': 'update_rooms',
    #                'room_list': room_list,
    #            }
    #        )

    #        # Wait for a specific interval before sending the next update
    #        await asyncio.sleep(10)  # Adjust the interval as needed
