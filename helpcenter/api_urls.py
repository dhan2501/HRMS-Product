from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'policy-categories', api_views.PolicyCategoryViewSet)
router.register(r'policy-documents', api_views.PolicyDocumentViewSet)
urlpatterns = router.urls