import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Chat, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Get the chat object (using sync_to_async)
        chat = await sync_to_async(Chat.objects.get)(name=self.room_name)

        # Save the message to the database (using sync_to_async)
        await sync_to_async(Message.objects.create)(
            chat=chat,
            sender=self.user,
            text_message=message
        )

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {
                "type": "chat_message",
                "message": message,
                "user": self.user.username,
            }
        )

    async def chat_message(self, event):
        message = event["message"]
        username = event['user']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message, 'user': username}))
