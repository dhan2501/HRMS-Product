from django.db import models
from django.contrib.auth.models import User
from employees.models import Employee


class Conversation(models.Model):
    """One-to-one or group conversation."""
    CONV_TYPE = [
        ('direct', 'Direct Message'),
        ('group', 'Group Chat'),
    ]
    conv_type    = models.CharField(max_length=10, choices=CONV_TYPE, default='direct')
    name         = models.CharField(max_length=100, blank=True)  # For group chats
    participants = models.ManyToManyField(User, related_name='conversations')
    created_by   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_conversations')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def get_other_participant(self, user):
        """For DM: get the other person."""
        return self.participants.exclude(id=user.id).first()

    def last_message(self):
        return self.messages.order_by('-created_at').first()

    def unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()

    def __str__(self):
        return f"{self.conv_type} - {self.id}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content      = models.TextField()
    file         = models.FileField(upload_to='chat_files/', null=True, blank=True)
    file_name    = models.CharField(max_length=255, blank=True)
    is_read      = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"


class MessageRead(models.Model):
    """Track who read which message (for group chats)."""
    message  = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reads')
    user     = models.ForeignKey(User, on_delete=models.CASCADE)
    read_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['message', 'user']