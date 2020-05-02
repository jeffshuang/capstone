import json
from channels.generic.websocket import AsyncWebsocketConsumer

class FeedConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        print(text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if "showers" in message or "rain" in message:
            message+=" 🌧"  

        if "cloudy" in message:
            message+=" ☁️"

        if "sun" in message:
            message+=" ☀️"

        if "alarm" in message.lower():
            message+=" ⏰" 

        query = text_data_json['query']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'query': query
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        query = event['query']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'query': query
        }))