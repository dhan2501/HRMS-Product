from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'conversations', api_views.ConversationViewSet, basename='conversation')
router.register(r'chat-messages', api_views.MessageViewSet, basename='chat-message')
router.register(r'message-reads', api_views.MessageReadViewSet, basename='message-read')
urlpatterns = router.urls