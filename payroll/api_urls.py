from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'salary-structures', api_views.SalaryStructureViewSet)
router.register(r'payslips', api_views.PayslipViewSet)
urlpatterns = router.urls
