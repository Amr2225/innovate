from django.contrib import admin
from .models import Message, ChatRoom
from django.utils.html import format_html
from django.urls import reverse

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'message_count', 'created_at', 'view_messages_link')
    search_fields = ('name',)
    ordering = ('-created_at',)

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'

    def view_messages_link(self, obj):
        url = reverse('admin:chat_message_changelist') + f'?room__id__exact={obj.id}'
        return format_html('<a href="{}">View Messages</a>', url)
    view_messages_link.short_description = 'Room Messages'

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('formatted_content', 'sender_name', 'receiver_name', 'room', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp', 'room', 'sender', 'receiver')
    search_fields = ('content', 'sender__first_name', 'sender__last_name', 'receiver__first_name', 'receiver__last_name', 'room__name')
    readonly_fields = ('id', 'timestamp')
    ordering = ('-timestamp',)
    
    def formatted_content(self, obj):
        """Display formatted content with sender info"""
        style = 'color: green;' if obj.is_read else 'color: orange; font-weight: bold;'
        return format_html(
            '<span style="{}">{}: {}</span>',
            style,
            obj.sender.full_name,
            obj.content[:50] + ('...' if len(obj.content) > 50 else '')
        )
    formatted_content.short_description = 'Message'

    def sender_name(self, obj):
        return obj.sender.full_name
    sender_name.short_description = 'Sender'
    sender_name.admin_order_field = 'sender__first_name'

    def receiver_name(self, obj):
        return obj.receiver.full_name if obj.receiver else 'Group Message'
    receiver_name.short_description = 'Receiver'
    receiver_name.admin_order_field = 'receiver__first_name'

    def save_model(self, request, obj, form, change):
        if not change:  # If this is a new message
            obj.sender = request.user  # Set current admin user as sender
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # If this is a new message
            form.base_fields['sender'].initial = request.user
        return form

