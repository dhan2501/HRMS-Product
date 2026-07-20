from django.urls import path
from . import views

urlpatterns = [
    # Salary Structure
    path('', views.salary_structure, name='salary_structure'),
    path('add/', views.add_salary, name='add_salary'),
    path('<int:pk>/edit/', views.edit_salary, name='edit_salary'),
    path('<int:pk>/delete/', views.delete_salary, name='delete_salary'),

    # Payslips
    path('payslips/', views.payslips, name='payslips'),
    path('payslips/generate/', views.generate_payslips, name='generate_payslips'),
    path('payslips/<int:pk>/paid/', views.mark_paid, name='mark_paid'),
    path('payslips/<int:pk>/', views.payslip_detail, name='payslip_detail'),
]