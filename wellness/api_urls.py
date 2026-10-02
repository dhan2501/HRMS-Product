from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'wellness-resources', api_views.WellnessResourceViewSet)
urlpatterns = router.urls