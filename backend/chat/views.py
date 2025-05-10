from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from users.permissions import isInstitution, isStudent, isTeacher
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.exceptions import NotFound

User = get_user_model()

# Test view for WebSocket chat functionality
@login_required
def test_chat(request):
    return render(request, 'chat/test_websocket.html')

# ----------------------
# Chat Room Views
# ----------------------

# API view for listing all chat rooms and creating new ones
# Handles GET (list) and POST (create) requests
class ChatRoomListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['name']

    # Filter chat rooms based on user role and access permissions
    def get_queryset(self):
        user = self.request.user
        if user.role == "Institution":
            return ChatRoom.objects.filter(messages__sender=user).prefetch_related('messages', 'messages__sender', 'messages__receiver')
        elif user.role in ["Student", "Teacher"]:
            return ChatRoom.objects.filter(
                Q(messages__sender=user) | Q(messages__receiver=user)
            ).distinct().prefetch_related('messages', 'messages__sender', 'messages__receiver')
        return ChatRoom.objects.none()

    # Return paginated list of chat rooms with standardized response format
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "count": len(serializer.data),
            "results": serializer.data
        })

    # Create a new chat room with standardized response format
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        # Re-fetch the instance to get all related data
        instance = ChatRoom.objects.filter(id=instance.id).prefetch_related('messages', 'messages__sender', 'messages__receiver').first()
        return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)

    # Set the chat room sender to the current user
    def perform_create(self, serializer):
        return serializer.save()


# API view for retrieving, updating, and deleting specific chat rooms
# Handles GET (retrieve), PUT/PATCH (update), and DELETE requests
class ChatRoomDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'p_id'
    
    def get_queryset(self):
        user = self.request.user
        if user.role == "Institution":
            return ChatRoom.objects.filter(messages__sender=user).prefetch_related(
                'messages', 
                'messages__sender', 
                'messages__receiver'
            ).distinct()
        elif user.role in ["Student", "Teacher"]:
            return ChatRoom.objects.filter(
                Q(messages__sender=user) | Q(messages__receiver=user)
            ).prefetch_related(
                'messages', 
                'messages__sender', 
                'messages__receiver'
            ).distinct()
        return ChatRoom.objects.none()

    def get_permissions(self):
        self.permission_classes = [permissions.IsAuthenticated]
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [isInstitution]
        return super().get_permissions()

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except ChatRoom.DoesNotExist:
            raise NotFound(detail="Chat room not found")

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            # Re-fetch the instance to get all related data
            instance = self.get_queryset().get(id=instance.id)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except ChatRoom.DoesNotExist:
            raise NotFound(detail="Chat room not found")

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ChatRoom.DoesNotExist:
            raise NotFound(detail="Chat room not found")


# API view for listing messages in a specific chat room
# Handles GET (list) requests only
class ChatRoomMessagesAPIView(generics.ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['sender', 'receiver', 'timestamp', 'is_read']

    # Filter messages based on chat room and user access permissions
    def get_queryset(self):
        room_id = self.kwargs.get('p_id')
        user = self.request.user
        messages = Message.objects.filter(room_id=room_id).select_related('sender', 'receiver', 'room')
        
        if user.role == "Institution":
            messages = messages.filter(sender=user)
        elif user.role in ["Student", "Teacher"]:
            messages = messages.filter(Q(sender=user) | Q(receiver=user))
        
        unread_messages = messages.filter(receiver=user, is_read=False)
        unread_messages.update(is_read=True)
        
        return messages.order_by('-timestamp')

    # Return paginated list of messages with standardized response format
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "count": len(serializer.data),
            "results": serializer.data
        })

# ----------------------
# Message Views
# ----------------------

# API view for listing all messages and creating new ones
# Handles GET (list) and POST (create) requests
class MessageListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['room', 'sender', 'receiver', 'timestamp', 'is_read']

    # Filter messages based on user role and access permissions
    def get_queryset(self):
        user = self.request.user
        if user.role == "Institution":
            return Message.objects.filter(sender=user).select_related('sender', 'receiver', 'room').order_by('-timestamp')
        elif user.role in ["Student", "Teacher"]:
            messages = Message.objects.filter(
                Q(sender=user) | Q(receiver=user)
            ).select_related('sender', 'receiver', 'room')
            unread_messages = messages.filter(receiver=user, is_read=False)
            unread_messages.update(is_read=True)
            return messages.order_by('-timestamp')
        return Message.objects.none()

    # Return all messages for the current query context
    def get_messages_data(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return serializer.data

    # Return paginated list of messages with standardized response format
    def list(self, request, *args, **kwargs):
        messages_data = self.get_messages_data(request)
        return Response({
            "count": len(messages_data),
            "results": messages_data
        })

    # Create a new message with permission checks and standardized response format
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        # Re-fetch the instance to get all related data
        instance = Message.objects.filter(id=instance.id).select_related('sender', 'receiver', 'room').first()
        return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)

    # Set the message sender to the current user
    def perform_create(self, serializer):
        receiver = serializer.validated_data.get('receiver')
        if receiver and not ChatRoom.can_users_chat(self.request.user, receiver):
            raise ValidationError({"error": "You are not allowed to send messages to this user"})
        return serializer.save(sender=self.request.user)


# API view for retrieving, updating, and deleting specific messages
# Handles GET (retrieve), PUT/PATCH (update), and DELETE requests
class MessageDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'p_id'

    # Filter messages based on user role and access permissions
    def get_queryset(self):
        user = self.request.user
        if user.role == "Institution":
            return Message.objects.filter(sender=user).select_related('sender', 'receiver', 'room')
        elif user.role in ["Student", "Teacher"]:
            return Message.objects.filter(
                Q(sender=user) | Q(receiver=user)
            ).select_related('sender', 'receiver', 'room')
        return Message.objects.none()

    # Get all messages for the current context
    def get_messages_data(self, request):
        # Use the same queryset logic as MessageListCreateAPIView
        if request.user.role == "Institution":
            queryset = Message.objects.filter(sender=request.user).order_by('-timestamp')
        elif request.user.role in ["Student", "Teacher"]:
            queryset = Message.objects.filter(
                Q(sender=request.user) | Q(receiver=request.user)
            ).order_by('-timestamp')
        else:
            queryset = Message.objects.none()
            
        serializer = self.get_serializer(queryset, many=True)
        return serializer.data

    # Retrieve a specific message with standardized response format
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        messages_data = self.get_messages_data(request)
        return Response({
            "status": "success",
            "message": "Message retrieved successfully",
            "data": {
                "message": serializer.data,
                "all_messages": messages_data
            },
            "total_count": len(messages_data)
        })

    # Update a specific message with permission checks and standardized response format
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.sender != self.request.user:
            raise ValidationError({"error": "You can only modify your own messages"})
            
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Return all messages after updating
        messages_data = self.get_messages_data(request)
        return Response({
            "status": "success",
            "message": "Message updated successfully",
            "data": {
                "updated_message": serializer.data,
                "all_messages": messages_data
            },
            "total_count": len(messages_data)
        })

    # Delete a specific message with permission checks and standardized response format
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.sender != self.request.user:
            raise ValidationError({"error": "You can only delete your own messages"})
            
        self.perform_destroy(instance)
        
        # Return all remaining messages after deletion
        messages_data = self.get_messages_data(request)
        return Response({
            "status": "success",
            "message": "Message deleted successfully",
            "data": {
                "all_messages": messages_data
            },
            "total_count": len(messages_data)
        }, status=status.HTTP_200_OK)  # Changed from 204 to 200 to include data

    def perform_destroy(self, instance):
        if instance.sender != self.request.user:
            raise ValidationError({"error": "You can only delete your own messages"})
        instance.delete()
