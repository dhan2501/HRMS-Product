# # from django.urls import path
# # from . import views

# # urlpatterns = [
# #     # Dashboard
# #     path('', views.dashboard, name='dashboard'),
# #     path('dashboard/', views.dashboard, name='dashboard_home'),

# #     # Employees
# #     path('employees/', views.employee_list, name='employee_list'),
# #     path('employees/add/', views.add_employee, name='add_employee'),
# #     path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
# #     path('employees/<int:pk>/edit/', views.edit_employee, name='edit_employee'),

# #     # Departments
# #     path('departments/', views.department_list, name='department_list'),
# #     path('departments/add/', views.add_department, name='add_department'),
# #     path('departments/<int:pk>/edit/', views.edit_department, name='edit_department'),
# #     path('departments/<int:pk>/delete/', views.delete_department, name='delete_department'),

# #     # Designations
# #     path('designations/', views.designation_list, name='designation_list'),
# #     path('designations/add/', views.add_designation, name='add_designation'),
# #     path('designations/<int:pk>/edit/', views.edit_designation, name='edit_designation'),
# #     path('designations/<int:pk>/delete/', views.delete_designation, name='delete_designation'),
# # ]

# # from django.urls import path
# # from . import views

# # urlpatterns = [
# #     path('', views.dashboard, name='dashboard'),
# #     path('home/', views.dashboard, name='dashboard_home'),
# #     path('employees/', views.employee_list, name='employee_list'),
# #     path('employees/add/', views.add_employee, name='add_employee'),
# #     path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
# #     path('employees/<int:pk>/edit/', views.edit_employee, name='edit_employee'),
# #     path('departments/', views.department_list, name='department_list'),
# #     path('departments/add/', views.add_department, name='add_department'),
# #     path('departments/<int:pk>/edit/', views.edit_department, name='edit_department'),
# #     path('departments/<int:pk>/delete/', views.delete_department, name='delete_department'),
# #     path('designations/', views.designation_list, name='designation_list'),
# #     path('designations/add/', views.add_designation, name='add_designation'),
# #     path('designations/<int:pk>/edit/', views.edit_designation, name='edit_designation'),
# #     path('designations/<int:pk>/delete/', views.delete_designation, name='delete_designation'),
# # ]


# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.dashboard, name='dashboard'),
#     path('home/', views.dashboard, name='dashboard_home'),

#     # Employees
#     path('employees/', views.employee_list, name='employee_list'),
#     path('employees/add/', views.add_employee, name='add_employee'),
#     path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
#     path('employees/<int:pk>/edit/', views.edit_employee, name='edit_employee'),
#     path('employees/<int:pk>/status/', views.update_employee_status, name='update_employee_status'),

#     # ✅ Login Credentials Management
#     path('employees/credentials/', views.employee_credentials, name='employee_credentials'),
#     path('employees/<int:pk>/create-login/', views.create_employee_login, name='create_employee_login'),
#     path('employees/<int:pk>/reset-password/', views.reset_employee_password, name='reset_employee_password'),
#     path('employees/create-all-logins/', views.create_all_logins, name='create_all_logins'),

#     # Departments
#     path('departments/', views.department_list, name='department_list'),
#     path('departments/add/', views.add_department, name='add_department'),
#     path('departments/<int:pk>/edit/', views.edit_department, name='edit_department'),
#     path('departments/<int:pk>/delete/', views.delete_department, name='delete_department'),

#     # Designations
#     path('designations/', views.designation_list, name='designation_list'),
#     path('designations/add/', views.add_designation, name='add_designation'),
#     path('designations/<int:pk>/edit/', views.edit_designation, name='edit_designation'),
#     path('designations/<int:pk>/delete/', views.delete_designation, name='delete_designation'),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('home/', views.dashboard, name='dashboard_home'),

    # Employees
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.add_employee, name='add_employee'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.edit_employee, name='edit_employee'),
    path('employees/<int:pk>/status/', views.update_employee_status, name='update_employee_status'),

    # ✅ Performance Section
    path('employees/<int:pk>/performance/add/', views.add_performance_review, name='add_performance_review'),
    path('employees/<int:pk>/performance/<int:review_pk>/edit/', views.edit_performance_review, name='edit_performance_review'),
    path('employees/<int:pk>/performance/<int:review_pk>/delete/', views.delete_performance_review, name='delete_performance_review'),

    # ✅ Reporting Manager connectivity
    path('my-team/', views.my_team, name='my_team'),

    # ✅ Login Credentials Management
    path('employees/credentials/', views.employee_credentials, name='employee_credentials'),
    path('employees/<int:pk>/create-login/', views.create_employee_login, name='create_employee_login'),
    path('employees/<int:pk>/reset-password/', views.reset_employee_password, name='reset_employee_password'),
    path('employees/create-all-logins/', views.create_all_logins, name='create_all_logins'),

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