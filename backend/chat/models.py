import uuid
from django.db import models
from django.conf import settings


class ChatRoom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @staticmethod
    def can_users_chat(user1, user2):
        # Institution can chat with students and teachers in their institution
        if user1.role == "Institution":
            return user2.role in ["Student", "Teacher"] and user2.institution.filter(id=user1.id).exists()
        elif user2.role == "Institution":
            return user1.role in ["Student", "Teacher"] and user1.institution.filter(id=user2.id).exists()
        
        # Students can chat with their teachers and other students in same institution
        if user1.role == "Student" and user2.role in ["Student", "Teacher"]:
            return bool(set(user1.institution.all()) & set(user2.institution.all()))
        elif user2.role == "Student" and user1.role in ["Student", "Teacher"]:
            return bool(set(user1.institution.all()) & set(user2.institution.all()))
        
        # Teachers can chat with their students and other teachers in same institution
        if user1.role == "Teacher" and user2.role in ["Student", "Teacher"]:
            return bool(set(user1.institution.all()) & set(user2.institution.all()))
        
        return False


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.first_name}: {self.content[:20]}"

    class Meta:
        ordering = ['-timestamp']
# models.py

