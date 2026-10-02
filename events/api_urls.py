from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'events', api_views.EventViewSet)
urlpatterns = router.urls