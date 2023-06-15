from django.db import models

from apps.accounts.models import User


class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name='chats')


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    text_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)