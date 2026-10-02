from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'tenants', api_views.TenantViewSet)
router.register(r'tenant-recharges', api_views.RechargeLogViewSet)
urlpatterns = router.urls