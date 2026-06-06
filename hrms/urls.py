from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('employees.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('attendance/', include('attendance.urls')),
    path('leaves/', include('leaves.urls')),
    path('payroll/', include('payroll.urls')),
    path('recruitment/', include('recruitment.urls')),
    # REST API endpoints
    path('api/v1/', include('employees.api_urls')),
    path('api/v1/', include('attendance.api_urls')),
    path('api/v1/', include('leaves.api_urls')),
    path('api/v1/', include('payroll.api_urls')),
    path('api/v1/', include('recruitment.api_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
