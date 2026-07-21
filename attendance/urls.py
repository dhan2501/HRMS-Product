from django.urls import path
from . import views

urlpatterns = [
    path('', views.daily_attendance, name='daily_attendance'),
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('bulk/', views.bulk_attendance, name='bulk_attendance'),
    path('monthly/', views.monthly_attendance, name='monthly_attendance'),
    path('reports/', views.attendance_reports, name='attendance_reports'),

    # WFH - Admin side
    path('wfh/', views.wfh_requests, name='wfh_requests'),
    path('wfh/<int:pk>/approve/', views.approve_wfh, name='approve_wfh'),
    path('wfh/<int:pk>/reject/', views.reject_wfh, name='reject_wfh'),
]