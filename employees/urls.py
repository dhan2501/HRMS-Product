from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard_home'),

    # Employees
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.add_employee, name='add_employee'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.edit_employee, name='edit_employee'),

    # Departments
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.add_department, name='add_department'),
    path('departments/<int:pk>/edit/', views.edit_department, name='edit_department'),
    path('departments/<int:pk>/delete/', views.delete_department, name='delete_department'),

    # Designations
    path('designations/', views.designation_list, name='designation_list'),
    path('designations/add/', views.add_designation, name='add_designation'),
    path('designations/<int:pk>/edit/', views.edit_designation, name='edit_designation'),
    path('designations/<int:pk>/delete/', views.delete_designation, name='delete_designation'),
]