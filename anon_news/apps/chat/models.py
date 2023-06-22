from django.db import models

from apps.accounts.models import User


class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name='chats')
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}'


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True)
    text_message = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)