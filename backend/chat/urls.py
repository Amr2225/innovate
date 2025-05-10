# chat/urls.py
from django.urls import path, include, re_path
from . import consumers, views

urlpatterns = [
    # Test URL
    path('test/', views.test_chat, name='test-chat'),
    
    # Chat Room URLs
    path('rooms/', views.ChatRoomListCreateAPIView.as_view(), name='chatroom-list-create'),
    path('rooms/<int:p_id>/', views.ChatRoomDetailAPIView.as_view(), name='chatroom-detail'),
    path('rooms/<int:p_id>/messages/', views.ChatRoomMessagesAPIView.as_view(), name='chatroom-messages'),
    
    # Message URLs
    path('messages/', views.MessageListCreateAPIView.as_view(), name='message-list-create'),
    path('messages/<uuid:p_id>/', views.MessageDetailAPIView.as_view(), name='message-detail'),
]

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
