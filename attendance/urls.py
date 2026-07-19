from django.urls import path
from . import views

urlpatterns = [
    path('', views.daily_attendance, name='daily_attendance'),
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('bulk/', views.bulk_attendance, name='bulk_attendance'),
    path('monthly/', views.monthly_attendance, name='monthly_attendance'),
    path('reports/', views.attendance_reports, name='attendance_reports'),
]