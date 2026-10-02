from django.urls import path
from . import views

urlpatterns = [
    # Finance/HR dashboard
    path('', views.expense_requests, name='expense_requests'),
    path('reports/', views.expense_reports, name='expense_reports'),
    path('<int:pk>/', views.expense_detail, name='expense_detail'),
    path('<int:pk>/finance/approve/', views.finance_approve, name='finance_approve_expense'),
    path('<int:pk>/finance/reject/', views.finance_reject, name='finance_reject_expense'),
    path('<int:pk>/reimburse/', views.mark_reimbursed, name='mark_expense_reimbursed'),
]