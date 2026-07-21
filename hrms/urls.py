# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', include('employees.urls')),
#     path('auth/', include('django.contrib.auth.urls')),
#     path('attendance/', include('attendance.urls')),
#     path('leaves/', include('leaves.urls')),
#     path('payroll/', include('payroll.urls')),
#     path('recruitment/', include('recruitment.urls')),
#     # REST API endpoints
#     path('api/v1/', include('employees.api_urls')),
#     path('api/v1/', include('attendance.api_urls')),
#     path('api/v1/', include('leaves.api_urls')),
#     path('api/v1/', include('payroll.api_urls')),
#     path('api/v1/', include('recruitment.api_urls')),

#     # Employee Self Service Portal
#     path('portal/', include('employees.portal_urls')),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from employees import auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # HR Admin Login (alag)
    path('admin-login/', auth_views.admin_login, name='admin_login'),
    path('admin-logout/', auth_views.admin_logout, name='admin_logout'),

    # Employee Login (alag)
    path('employee-login/', auth_views.employee_login, name='employee_login'),
    path('employee-logout/', auth_views.employee_logout, name='employee_logout'),

    # Django default auth (password reset etc.)
    path('auth/', include('django.contrib.auth.urls')),

    # Pages
    path('', include('employees.urls')),
    path('attendance/', include('attendance.urls')),
    path('leaves/', include('leaves.urls')),
    path('payroll/', include('payroll.urls')),
    path('recruitment/', include('recruitment.urls')),
    path('portal/', include('employees.portal_urls')),

    # REST API
    path('api/v1/', include('employees.api_urls')),
    path('api/v1/', include('attendance.api_urls')),
    path('api/v1/', include('leaves.api_urls')),
    path('api/v1/', include('payroll.api_urls')),
    path('api/v1/', include('recruitment.api_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)