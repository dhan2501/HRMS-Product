from django.urls import path
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'employees', api_views.EmployeeViewSet)
router.register(r'departments', api_views.DepartmentViewSet)
router.register(r'designations', api_views.DesignationViewSet)

urlpatterns = router.urls
