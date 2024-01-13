import json
#from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
from .models import RoomsModel

def update_rooms(event):
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
    return ([
        {
            "id": i.id,
            "name": i.name
        } for i in RoomsModel.objects.all()
        ])
        
class RoomsConsumer(WebsocketConsumer):

    def connect(self):
        self.accept()
        #self.group_name = "rooms"
        #await self.channel_layer.group_add(
        #    self.group_name,
        #    self.channel_name
        #)

    def disconnect(self, close_code):
        pass
        #await self.channel_layer.group_discard(
        #    self.group_name,
        #    self.channel_name
        #)

    def receive(self, text_data):
        self.send(text_data=json.dumps(update_rooms(json.loads(text_data))))
        #await self.channel_layer.group_send(
        #    self.group_name,
        #    {
        #        'type': 'update_rooms',
        #        'action': json.loads(text_data),
        #    }
        #)


