from django.urls import path
from . import views

urlpatterns = [
    # Leave Requests
    path('', views.leave_requests, name='leave_requests'),
    path('apply/', views.apply_leave, name='apply_leave'),
    path('<int:pk>/approve/', views.approve_leave, name='approve_leave'),
    path('<int:pk>/reject/', views.reject_leave, name='reject_leave'),
    path('<int:pk>/cancel/', views.cancel_leave, name='cancel_leave'),

    # Leave Types
    path('types/', views.leave_types, name='leave_types'),
    path('types/add/', views.add_leave_type, name='add_leave_type'),
    path('types/<int:pk>/edit/', views.edit_leave_type, name='edit_leave_type'),
    path('types/<int:pk>/delete/', views.delete_leave_type, name='delete_leave_type'),

    # Reports
    path('reports/', views.leave_reports, name='leave_reports'),
]