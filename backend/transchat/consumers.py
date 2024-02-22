# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import User

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        blockcmd = False
        unblockcmd = False
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json['user']
        msg = str(message).split(" ")
        user = User.objects.get(username=username)
        self.scope['state'] ={
            "username": username
		}
        for i in msg:
            if i and blockcmd == True:
                if i == username:
                    self.send(text_data=json.dumps({"message": "You can't block yourself."}))
                    return
                try:
                    blockuser = User.objects.filter(username=i).get(username=i)
                except User.DoesNotExist:
                    self.send(text_data=json.dumps({"message": "Unable to find user " + i + "."}))
                    return
                user.blocked_user.add(blockuser)
                self.send(text_data=json.dumps({"message": "User " + blockuser.username + " blocked succesfully."}))
                return
            if i and unblockcmd == True:
                if i == username:
                    return
                try:
                    unblockuser = User.objects.filter(username=i).get(username=i)
                except User.DoesNotExist:
                    self.send(text_data=json.dumps({"message": "This user isn't blocked."}))
                    return
                user.blocked_user.remove(unblockuser)
                self.send(text_data=json.dumps({"message": "User " + unblockuser.username + " unblocked succesfully."}))
                return
            if i:
                if i == '/block' or i == '/BLOCK':
                    blockcmd = True
                if i == '/unblock' or i == '/UNBLOCK':
                    unblockcmd = True
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "message": user.username + "\n" + message, "user": user.username}
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]
        msg_user = event['user']
        user = User.objects.get(username=self.scope['state']['username'])
        try:
            print("blockeduser = " + str(user.blocked_user.get(username=msg_user)))
        except User.DoesNotExist:
            self.send(text_data=json.dumps({"message": message, "user": msg_user}))