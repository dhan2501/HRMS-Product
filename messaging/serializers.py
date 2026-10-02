from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Conversation, Message, MessageRead


class UserMiniSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name']


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'sender_name', 'content',
            'file', 'file_name', 'is_read', 'created_at',
        ]
        read_only_fields = ['sender', 'is_read']


class ConversationSerializer(serializers.ModelSerializer):
    participants_detail = UserMiniSerializer(source='participants', many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'conv_type', 'name', 'participants', 'participants_detail',
            'created_by', 'created_at', 'updated_at', 'last_message', 'unread_count',
        ]
        read_only_fields = ['created_by']

    def get_last_message(self, obj):
        msg = obj.last_message()
        if not msg:
            return None
        return MessageSerializer(msg).data

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        return obj.unread_count(request.user)


class MessageReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageRead
        fields = ['id', 'message', 'user', 'read_at']
        read_only_fields = ['user']