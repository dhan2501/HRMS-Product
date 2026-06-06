from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'leave-types', api_views.LeaveTypeViewSet)
router.register(r'leave-balances', api_views.LeaveBalanceViewSet)
router.register(r'leave-requests', api_views.LeaveRequestViewSet)
urlpatterns = router.urls
