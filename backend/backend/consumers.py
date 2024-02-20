import json
from channels.generic.websocket import AsyncWebsocketConsumer
from game.models import RoomsModel

# class RoomsConsumer(AsyncWebsocketConsumer):
#     connected_users = set()

#     async def connect(self):
#         self.group_name = "rooms"
#         await self.channel_layer.group_add(
#             self.group_name,
#             self.channel_name
#         )

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         await self.channel_layer.group_send(
#             self.group_name,
#             {
#                 'type': 'update_rooms',
#                 'action': json.loads(text_data),
#             }
#         )

#     async def update_rooms(self, event):
#         action = event['action']
#         if (action['action'] == "new"):
#             RoomsModel(
#                 game="pong",
#                 name=action['name'],
#                 nplayers=1,
#                 owner=action['owner']
#             ).save()
#         if (action['action'] == "delete"):
#             RoomsModel.objects.get(id=action['id']).delete()
#         await self.send(text_data=json.dumps([
#             {
#                 "id": i.id,
#                 "name": i.name
#             } for i in RoomsModel.objects.all()]))
