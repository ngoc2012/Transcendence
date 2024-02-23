# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import User, Room

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
        user = User.objects.get(username=self.scope['state']['username'])
        room = Room.objects.get(room_name=self.scope['state']['room'])
        room.users.remove(user)
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def block_user(self, huh, data, str):
        if str == data['username']:
            self.send(text_data=json.dumps({"message": "You can't block yourself.", 'user': data['user'], 'room': data['room']}))
            return
        try:
            block_user = User.objects.filter(username=str).get(username=str)
        except User.DoesNotExist:
            self.send(text_data=json.dumps({"message": "Unable to find user " + str + "."}))
            return
        data['user'].blocked_user.add(block_user)
        self.send(text_data=json.dumps({"message": "User " + block_user.username + " blocked succesfully.", 'user': data['username'], 'room': data['room']}))
        return
    
    def unblock_user(self, huh, data, str):
        if str == data['username']:
            self.send(text_data=json.dumps({"message": "You can't unblock yourself.", 'user': data['username'], 'room': data['room']}))
            return
        try:
            block_user = User.objects.filter(username=str).get(username=str)
        except User.DoesNotExist:
            self.send(text_data=json.dumps({"message": "Unable to find user " + str + ".", 'user': data['username'], 'room': data['room']}))
            return
        data['user'].blocked_user.remove(block_user)
        self.send(text_data=json.dumps({"message": "User " + block_user.username + " unblocked succesfully.", 'user': data['username'], 'room': data['room']}))
        return

    def send_whisper(self, huh, data, value):
        msg = ' '.join(data['msg_split'][2::])
        if value == data['username']:
            self.send(text_data=json.dumps({"message": "You can't whisper yourself.", 'user': data['username'], 'room': data['room']}))
            return
        try:
            User.objects.filter(username=value).get(username=value)
        except User.DoesNotExist:
            self.send(text_data=json.dumps({'message': "Unable to find user " + value + ".", 'user': data['username'], 'room': data['room']}))
            return
        try:
            receiver = Room.objects.get(room_name=data['room']).users.get(username=value)
        except User.DoesNotExist:
            self.send(text_data=json.dumps({"message": "Unable to whisper " + value + ". " + value + " is not in your room.", 'user': data['username'], 'room': data['room']}))
            return
        if msg == receiver.username:
            self.send(text_data=json.dumps({"message": "You can't send empty whispers.", "user": data['username'], 'room': data['room']}))
            return
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "whisper", "message": msg, "receiver": receiver.username, 'room': data['room'], 'sender': data['username']}
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data = {
            'text_data': json.loads(text_data),
            'message': json.loads(text_data)['message'],
            'username': json.loads(text_data)['user'],
            'user': User.objects.get(username=json.loads(text_data)['user']),
            'msg_split': str(json.loads(text_data)['message']).split(" "),
            'room': json.loads(text_data)['room'],
            'blockcmd': False,
            'unblockcmd': False,
            'whisper': False,
            'type': json.loads(text_data)['type']
        }
        if self.scope['state']['username'] == '':
            if data['text_data']['type'] == 'connection':
                self.scope['state']['username'] = data['username']
                self.scope['state']['room'] = data['room']
                return
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
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "message": data['user'].username + ":\n" + data['message'], "user": data['user'].username, 'room': data['room']}
        )


    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]
        msg_user = event['user']
        user = User.objects.get(username=self.scope['state']['username'])
        try:
            user.blocked_user.get(username=msg_user)
        except User.DoesNotExist:
            self.send(text_data=json.dumps({"message": message, "user": msg_user}))

    def whisper(self, event):
        message = event['message']
        receiver = event['receiver']
        user = event['sender']
        if self.scope['state']['username'] == receiver:
            self.send(json.dumps({"type": "whisper", "message": user + " whispered :\n" + message, 'user': receiver, 'room': event['room']}))