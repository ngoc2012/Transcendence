import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from game.models import RoomsModel, PlayersModel, PlayerRoomModel

@sync_to_async
def get_room_data(players, room_id):
    room = RoomsModel.objects.get(id=room_id)
    return json.dumps({
        'ball': {'x': room.x, 'y':room.y},
        'players': [{'x': i.x, 'y': i.y} for i in players]
    })

class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        # Join room group
        await self.channel_layer.group_add(
            self.room_id,
            self.channel_name
        )
        await self.accept()
        await self.channel_layer.group_send(
            self.room_id,
            {
                'type': 'group_data'
            }
        )
        # Start a loop to continuously update the game state
        #await self.game_loop()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_id,
            self.channel_name
        )

    async def receive(self, text_data):
        await self.channel_layer.group_send(
            self.room_id,
            {
                'type': 'group_data'
            }
        )
    
    async def group_data(self, event):
        players = PlayerRoomModel.objects.filter(room=self.room_id)
        room_data = await get_room_data(players, self.room_id)
        await self.send(text_data=room_data)
    
    #async def game_loop(self):
    #    # Simulate a game loop that updates the state every 1 second
    #    while True:
    #        await asyncio.sleep(1)  # Sleep for 1 second
#
    #        # Update the game state (this is just an example, actual logic depends on your game)
    #        self.state['ball_position']['x'] += 1
    #        self.state['ball_position']['y'] += 1
#
    #        # Notify all clients about the updated state
    #        await self.channel_layer.group_send(
    #        self.room_group_name,
    #        {
    #            'type': 'game_update_state',
    #            'state': self.state,
    #        }
    #    )

    #async def game_update_state(self, event):
    #    # Handle the event when the game state is updated
    #    state = event['state']
    #    await self.send(text_data=json.dumps({
    #        'state': state,
    #    }))