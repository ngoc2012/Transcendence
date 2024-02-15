import json
from channels.generic.websocket import AsyncWebsocketConsumer
from game.models import RoomsModel

class RoomsConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.group_name = "rooms"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'update_rooms',
                'action': json.loads(text_data),
            }
        )

    async def update_rooms(self, event):
        action = event['action']
        if (action['action'] == "new"):
            RoomsModel(
                game="pong",
                name=action['name'],
                nplayers=1,
                owner=action['owner']
            ).save()
        if (action['action'] == "delete"):
            RoomsModel.objects.get(id=action['id']).delete()
        await self.send(text_data=json.dumps([
            {
                "id": i.id,
                "name": i.name
            } for i in RoomsModel.objects.all()]))
        

# class TournamentInviteConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.tournament_id = self.scope['url_route']['kwargs']['tournament_id']
#         self.tournament_group_name = f'tournament_{self.tournament_id}'
        
#         await self.channel_layer.group_add(
#             self.tournament_group_name,
#             self.channel_name
#         )

#         await self.accept()

#     async def disconnect(self, close_code):
#         pass
    
#     async def receive(self, text_data):
#         text_data_json = json.load(text_data)
#         message = text_data_json['message']

#         # send message to websocket
#         await self.send(text_data=json.dumps({
#             'message' : message
#         }))

class TournamentInviteConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.tournament_id = self.scope['url_route']['kwargs']['tournament_id']
        self.tournament_group_name = f'tournament_{self.tournament_id}'
        
        # Add this socket to the group
        await self.channel_layer.group_add(
            self.tournament_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Remove this socket from the group on disconnect
        await self.channel_layer.group_discard(
            self.tournament_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data=None, bytes_data=None):
        # Parse the incoming text data
        text_data_json = json.loads(text_data)  # Corrected to json.loads
        message = text_data_json['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))