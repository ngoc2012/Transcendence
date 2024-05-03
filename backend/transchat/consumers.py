# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import User, Room
from accounts.models import PlayersModel

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        self.scope['state'] ={
            'username': '',
            'room': ''
		}
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        user = PlayersModel.objects.get(login=self.scope['state']['username'])
        room = Room.objects.get(room_name=self.scope['state']['room'])
        room.users.remove(user)
        room.save()
        async_to_sync(self.channel_layer.group_send)(self.room_group_name, {"type": "update"})
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def block_user(self, huh, data, str):
        if str == data['username']:
            self.send(text_data=json.dumps({"message": "You can't block yourself.", 'user': data['user']}))
            return
        try:
            block_user = PlayersModel.objects.get(login=str)
        except PlayersModel.DoesNotExist:
            self.send(text_data=json.dumps({"message": "Unable to find user " + str + "."}))
            return
        data['user'].blocked_users.add(block_user)
        data['user'].save()
        self.send(text_data=json.dumps({"message": "User " + block_user.login + " blocked succesfully.", 'user': data['username']}))
        return
    
    def unblock_user(self, huh, data, str):
        if str == data['username']:
            self.send(text_data=json.dumps({"message": "You can't unblock yourself.", 'user': data['username']}))
            return
        try:
            block_user = PlayersModel.objects.get(login=str)
        except PlayersModel.DoesNotExist:
            self.send(text_data=json.dumps({"message": "Unable to find user " + str + " or you didn't block this user.", 'user': data['username']}))
            return
        data['user'].blocked_users.remove(block_user)
        data['user'].save()
        self.send(text_data=json.dumps({"message": "User " + block_user.username + " unblocked succesfully.", 'user': data['username']}))
        return

    def send_whisper(self, huh, data, value):
        msg = ' '.join(data['msg_split'][2::])
        if value == data['username']:
            self.send(text_data=json.dumps({"message": "You can't whisper yourself.", 'user': data['username']}))
            return
        try:
            PlayersModel.objects.get(login=value)
        except PlayersModel.DoesNotExist:
            self.send(text_data=json.dumps({'message': "Unable to find user " + value + ".", 'user': data['username']}))
            return
        try:
            receiver = Room.objects.get(room_name='general_chat').users.get(login=value)
        except PlayersModel.DoesNotExist:
            self.send(text_data=json.dumps({"message": "Unable to whisper " + value + ". " + value + " is not in your room.", 'user': data['username']}))
            return
        if msg == receiver.login:
            self.send(text_data=json.dumps({"message": "You can't send empty whispers.", "user": data['username']}))
            return
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "whisper", "message": msg, "receiver": receiver.username, 'sender': data['username']}
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        print(text_data)
        if json.loads(text_data)["type"] == 'connection':
            if self.scope['state']['username'] == '':
                if json.loads(text_data)['type'] == 'connection':
                    self.scope['state']['username'] = json.loads(text_data)['user']
                    self.scope['state']['room'] = 'general_chat'
                    room = Room.objects.get(room_name='general_chat')
                    try:
                        room.users.get(login=self.scope['state']['username'])
                    except PlayersModel.DoesNotExist:
                        room.users.add(PlayersModel.objects.get(login=self.scope['state']['username']))
                        room.save()
                    async_to_sync(self.channel_layer.group_send)(self.room_group_name, {"type": "update"})
                    return
        elif json.loads(text_data)["type"] == 'update':
                async_to_sync(self.channel_layer.group_send)(self.room_group_name, {"type": "update"})
                return
        data = {
            'text_data': json.loads(text_data),
            'message': json.loads(text_data)['message'],
            'username': json.loads(text_data)['user'],
            'user': PlayersModel.objects.get(login=json.loads(text_data)['user']),
            'msg_split': str(json.loads(text_data)['message']).split(" "),
            'blockcmd': False,
            'unblockcmd': False,
            'whisper': False,
            'type': json.loads(text_data)['type']
        }
        for i in data['msg_split']:
            if i and data['blockcmd'] == True:
                self.block_user(self, data, i)
                return
            if i and data['unblockcmd'] == True:
                self.unblock_user(self, data, i)
                return
            if i and data['whisper'] == True:
                self.send_whisper(self, data, i)
                return
            if i:
                if i == '/block' or i == '/BLOCK' or i == '/b' or i == '/B':
                    data['blockcmd'] = True
                if i == '/unblock' or i == '/UNBLOCK' or i == '/ub' or i == '/UB':
                    data['unblockcmd'] = True
                if i == '/whisper' or i == '/WHISPER' or i == '/w' or i == '/W':
                    data['whisper'] = True
        # Send message to room group
        if data['message'] != '':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {"type": "chat_message", "message": data['user'].login + ":\n" + data['message'], "user": data['user'].login}
            )


    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]
        msg_user = event['user']
        user = PlayersModel.objects.get(login=self.scope['state']['username'])
        try:
            user.blocked_users.get(login=msg_user)
        except PlayersModel.DoesNotExist:
            self.send(text_data=json.dumps({"message": message, "user": msg_user}))

    def update(self, event):
        type = event['type']
        room = Room.objects.get(room_name='general_chat')
        if self.scope['state']['username'] != '':
            try:
                room.users.get(login=self.scope['state']['username'])
            except PlayersModel.DoesNotExist:
                room.users.add(PlayersModel.objects.get(login=self.scope['state']['username']))
                room.save();
        queryset = Room.objects.get(room_name=self.room_name).users.all()
        queryseturl = Room.objects.get(room_name=self.room_name).users.all().values("avatar")
        self.send(json.dumps({'type': 'update', 'users': list(queryset.values("login")), 'pictures': list(queryseturl)}))

    def whisper(self, event):
        message = event['message']
        receiver = event['receiver']
        user = event['sender']
        if self.scope['state']['username'] == receiver:
            self.send(json.dumps({"type": "whisper", "message": user + " whispered :\n" + message, 'user': receiver}))