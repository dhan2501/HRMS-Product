from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'attendance', api_views.AttendanceViewSet)
router.register(r'holidays', api_views.HolidayViewSet)
urlpatterns = router.urls
