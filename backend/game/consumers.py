import json
from channels.generic.websocket import AsyncWebsocketConsumer
#from channels.generic.websocket import WebsocketConsumer
#from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from .models import RoomsModel, PlayersModel

@sync_to_async
def room_list(rooms):
    return json.dumps([
        {
            "id": i.id,
            "name": i.name
            } for i in rooms])

#@sync_to_async
#def check_event(event):
#    if 'action' not in event.keys():
#        print("Error: No action in event.")
#        return None
#    action = event['action']
#    if 'action' not in action.keys():
#        print("Error: No action.")
#        return None
#    if 'game' not in action.keys():
#        print("Error: No game.")
#        return None
#    if 'login' not in action.keys():
#        print("Error: No login.")
#        return None
#    if not PlayersModel.objects.filter(login=action['login']).exists():
#        print("Error: Login " + action['login'] + " does not exist.")
#        return None
#    return action

class RoomsConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.group_name = "rooms"
        self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        rooms = RoomsModel.objects.all()
        rooms_data = await room_list(rooms)
        await self.send(text_data=rooms_data)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        rooms = RoomsModel.objects.all()
        rooms_data = await room_list(rooms)
        await self.send(text_data=rooms_data)        
        #data = json.loads(text_data)
        #print("receive")
        #print(data)
        #await self.channel_layer.group_send(
        #    self.group_name,
        #    {
        #        'type': 'group_update_rooms',
        #        'action': data,
        #    }
        #)
        #self.send(text_data=json.dumps(update_rooms(json.loads(text_data))))

    #async def group_update_rooms(self, event):
    #    print("update_rooms")
    #    print(event)
    #    action = await check_event(event)
    #    owner = PlayersModel.objects.get(login=action['login'])
    #    if (action['action'] == "new"):
    #        RoomsModel(
    #                game=action['game'],
    #                name=action['name'],
    #                nplayers=1,
    #                owner=owner
    #                ).save()
    #    if (action['action'] == "delete"):
    #        RoomsModel.objects.get(id=action['id']).delete()
    #    rooms = RoomsModel.objects.all()
    #    rooms_data = await room_list(rooms)
    #    await self.send(text_data=rooms_data)        

