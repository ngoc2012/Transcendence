import json

from channels.generic.websocket import AsyncWebsocketConsumer

class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        user_id = self.scope.get('user')

        # Join room group
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        # Update game state (new paddle)
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'update_state',
                'state': {},
            }
        )
        await self.accept()

        # Start a loop to continuously update the game state
        await self.game_loop()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle user input (if needed)
        pass

    async def update_state(self):
        # Send the updated game state back to all clients in the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_update_state',
                'state': self.state,
            }
        )

    #async def game_loop(self):
    #    # Simulate a game loop that updates the state every 1 second
    #    while True:
    #        await asyncio.sleep(1)  # Sleep for 1 second

    #        # Update the game state (this is just an example, actual logic depends on your game)
    #        self.state['ball_position']['x'] += 1
    #        self.state['ball_position']['y'] += 1

    #        # Notify all clients about the updated state
    #        await self.update_state()

    #async def game_update_state(self, event):
    #    # Handle the event when the game state is updated
    #    state = event['state']
    #    await self.send(text_data=json.dumps({
    #        'state': state,
    #    }))

    #async def player_join(self, event):
    #    # Notify all clients when a new player joins the room
    #    player_count = event['player_count']
    #    await self.send(text_data=json.dumps({
    #        'player_count': player_count,
    #    }))

