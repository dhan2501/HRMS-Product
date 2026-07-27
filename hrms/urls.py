# # from django.contrib import admin
# # from django.urls import path, include
# # from django.conf import settings
# # from django.conf.urls.static import static

# # urlpatterns = [
# #     path('admin/', admin.site.urls),
# #     path('', include('employees.urls')),
# #     path('auth/', include('django.contrib.auth.urls')),
# #     path('attendance/', include('attendance.urls')),
# #     path('leaves/', include('leaves.urls')),
# #     path('payroll/', include('payroll.urls')),
# #     path('recruitment/', include('recruitment.urls')),
# #     # REST API endpoints
# #     path('api/v1/', include('employees.api_urls')),
# #     path('api/v1/', include('attendance.api_urls')),
# #     path('api/v1/', include('leaves.api_urls')),
# #     path('api/v1/', include('payroll.api_urls')),
# #     path('api/v1/', include('recruitment.api_urls')),

# #     # Employee Self Service Portal
# #     path('portal/', include('employees.portal_urls')),
# # ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# from employees import auth_views
# from employees.chatbot_view import chatbot_api

# urlpatterns = [
#     path('admin/', admin.site.urls),

#     # HR Admin Login (alag)
#     path('admin-login/', auth_views.admin_login, name='admin_login'),
#     path('admin-logout/', auth_views.admin_logout, name='admin_logout'),

#     # Employee Login (alag)
#     path('employee-login/', auth_views.employee_login, name='employee_login'),
#     path('employee-logout/', auth_views.employee_logout, name='employee_logout'),

#     # Django default auth (password reset etc.)
#     path('auth/', include('django.contrib.auth.urls')),

#     # Pages
#     path('', include('employees.urls')),
#     path('attendance/', include('attendance.urls')),
#     path('leaves/', include('leaves.urls')),
#     path('payroll/', include('payroll.urls')),
#     path('recruitment/', include('recruitment.urls')),
#     path('portal/', include('employees.portal_urls')),

#     # REST API
#     path('api/v1/', include('employees.api_urls')),
#     path('api/v1/', include('attendance.api_urls')),
#     path('api/v1/', include('leaves.api_urls')),
#     path('api/v1/', include('payroll.api_urls')),
#     path('api/v1/', include('recruitment.api_urls')),

#     path('chatbot/api/', chatbot_api, name='chatbot_api'),

#     path('messages/', include('messaging.urls')),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from employees import auth_views

# ✅ Custom 404 handler
handler404 = 'hrms.views.custom_404'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', auth_views.root_redirect, name='root_redirect'),

    # Root URL — Smart redirect
    path('', auth_views.root_redirect, name='root_redirect'),

    # Alag login pages
    path('admin-login/', auth_views.admin_login, name='admin_login'),
    path('admin-logout/', auth_views.admin_logout, name='admin_logout'),
    path('employee-login/', auth_views.employee_login, name='employee_login'),
    path('employee-logout/', auth_views.employee_logout, name='employee_logout'),
    #only use password reset
    path('auth/password-reset/', include('django.contrib.auth.urls')),


    # HR Admin pages (staff only)
    path('dashboard/', include('employees.urls')),
    path('attendance/', include('attendance.urls')),
    path('leaves/', include('leaves.urls')),
    path('payroll/', include('payroll.urls')),
    path('recruitment/', include('recruitment.urls')),

    # Employee Portal
    path('portal/', include('employees.portal_urls')),

    # Messaging
    path('messages/', include('messaging.urls')),

    # REST API
    path('api/v1/', include('employees.api_urls')),
    path('api/v1/', include('attendance.api_urls')),
    path('api/v1/', include('leaves.api_urls')),
    path('api/v1/', include('payroll.api_urls')),
    path('api/v1/', include('recruitment.api_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)