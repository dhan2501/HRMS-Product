from django.urls import path

from tenants import views

app_name = 'tenants'

urlpatterns = [
    path('login/', views.console_login, name='login'),
    path('logout/', views.console_logout, name='logout'),

    path('', views.tenant_list, name='list'),
    path('new/', views.tenant_create, name='create'),
    path('<int:pk>/edit/', views.tenant_edit, name='edit'),
    path('<int:pk>/recharge/', views.tenant_recharge, name='recharge'),
    path('<int:pk>/suspend/', views.tenant_suspend, name='suspend'),
]