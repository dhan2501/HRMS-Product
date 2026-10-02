from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Conversation, Message, MessageRead
from .serializers import ConversationSerializer, MessageSerializer, MessageReadSerializer


class ConversationViewSet(viewsets.ModelViewSet):
    """Only conversations the logged-in user is part of."""
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def perform_create(self, serializer):
        conversation = serializer.save(created_by=self.request.user)
        conversation.participants.add(self.request.user)


class MessageViewSet(viewsets.ModelViewSet):
    """Only messages belonging to a conversation the user participates in."""
    serializer_class = MessageSerializer

    def get_queryset(self):
        qs = Message.objects.filter(conversation__participants=self.request.user)
        conversation = self.request.query_params.get('conversation')
        if conversation:
            qs = qs.filter(conversation_id=conversation)
        return qs

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        message = self.get_object()
        message.is_read = True
        message.save(update_fields=['is_read'])
        MessageRead.objects.get_or_create(message=message, user=request.user)
        return Response(self.get_serializer(message).data)


class MessageReadViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MessageReadSerializer

    def get_queryset(self):
        return MessageRead.objects.filter(message__conversation__participants=self.request.user)