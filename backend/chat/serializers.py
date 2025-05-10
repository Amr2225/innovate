from rest_framework import serializers
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model

User = get_user_model()

# Minimal user serializer for chat functionality
# Only includes essential user information to reduce payload size
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name']

# Message serializer for handling chat messages
# Includes nested user serializers for both sender and receiver
class MessageSerializer(serializers.ModelSerializer):
    # Nested serializers for user details - read_only to prevent modification during message creation
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'room']
        # Auto-generated fields that shouldn't be modified by clients
        read_only_fields = ['id', 'timestamp']

# ChatRoom serializer for managing chat rooms
# Includes a method field to get the last message in the room
class ChatRoomSerializer(serializers.ModelSerializer):
    # Custom method field to include the most recent message in room data
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'last_message']

    # Helper method to fetch and serialize the most recent message
    # Returns None if no messages exist in the room
    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-timestamp').first()
        if last_message:
            return MessageSerializer(last_message).data
        return None
