# consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if isinstance(self.scope["user"], AnonymousUser):
            await self.close()
            return

        self.user = self.scope["user"]
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        try:
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

            # Create room if it doesn't exist
            room, created = await self.get_or_create_room(self.room_name)
            
            # Notify others that user is online
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'username': self.user.username,
                    'status': 'online'
                }
            )
        except Exception as e:
            await self.close()
            return

    async def disconnect(self, close_code):
        if hasattr(self, 'user') and hasattr(self, 'room_group_name'):
            # Notify others that user is offline
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'username': self.user.username,
                    'status': 'offline'
                }
            )

            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            
            if message_type == 'message':
                message = data.get('message')
                receiver_username = data.get('receiver')
                
                if not message:
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'Message content is required'
                    }))
                    return

                # Validate receiver if provided
                if receiver_username:
                    receiver = await self.get_user_by_username(receiver_username)
                    if not receiver:
                        await self.send(text_data=json.dumps({
                            'type': 'error',
                            'message': 'Receiver not found'
                        }))
                        return
                    
                    # Check if users can chat
                    can_chat = await self.can_users_chat(self.user, receiver)
                    if not can_chat:
                        await self.send(text_data=json.dumps({
                            'type': 'error',
                            'message': 'You are not allowed to send messages to this user'
                        }))
                        return
                
                # Save message to database
                message_obj = await self.save_message(
                    self.user.username,
                    self.room_name,
                    message,
                    receiver_username
                )

                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': message,
                        'username': self.user.username,
                        'receiver': receiver_username,
                        'timestamp': message_obj['timestamp'].isoformat()
                    }
                )
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid message format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'username': event['username'],
            'receiver': event.get('receiver'),
            'timestamp': event['timestamp']
        }))

    async def user_status(self, event):
        # Send user status to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'status',
            'username': event['username'],
            'status': event['status']
        }))

    @database_sync_to_async
    def get_or_create_room(self, room_name):
        return ChatRoom.objects.get_or_create(name=room_name)

    @database_sync_to_async
    def get_user_by_username(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def can_users_chat(self, user1, user2):
        return ChatRoom.can_users_chat(user1, user2)

    @database_sync_to_async
    def save_message(self, username, room_name, message, receiver_username=None):
        user = User.objects.get(username=username)
        room = ChatRoom.objects.get(name=room_name)
        receiver = None
        if receiver_username:
            receiver = User.objects.get(username=receiver_username)
        
        message_obj = Message.objects.create(
            sender=user,
            receiver=receiver,
            room=room,
            content=message
        )
        
        return {
            'id': str(message_obj.id),
            'timestamp': message_obj.timestamp
        }
