from django.urls import path
from . import views

urlpatterns = [
    # Job Openings
    path('', views.job_list, name='job_list'),
    path('jobs/add/', views.add_job, name='add_job'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('jobs/<int:pk>/edit/', views.edit_job, name='edit_job'),
    path('jobs/<int:pk>/delete/', views.delete_job, name='delete_job'),

    # Candidates
    path('candidates/', views.candidate_list, name='candidate_list'),
    path('candidates/add/', views.add_candidate, name='add_candidate'),
    path('candidates/<int:pk>/', views.candidate_detail, name='candidate_detail'),
    path('candidates/<int:pk>/status/', views.update_candidate_status, name='update_candidate_status'),
    path('candidates/<int:pk>/delete/', views.delete_candidate, name='delete_candidate'),

    # Interviews
    path('interviews/', views.interview_list, name='interview_list'),
    path('interviews/schedule/', views.schedule_interview, name='schedule_interview'),
    path('interviews/schedule/<int:candidate_id>/', views.schedule_interview, name='schedule_interview_for'),
    path('interviews/<int:pk>/', views.interview_detail, name='interview_detail'),
    path('interviews/<int:pk>/delete/', views.delete_interview, name='delete_interview'),
]