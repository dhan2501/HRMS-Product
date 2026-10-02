from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'expense-claims', api_views.ExpenseClaimViewSet)
router.register(r'expense-comments', api_views.ExpenseCommentViewSet)
urlpatterns = router.urls