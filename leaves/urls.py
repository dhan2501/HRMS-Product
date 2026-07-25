# from django.urls import path
# from . import views

# urlpatterns = [
#     # Leave Requests
#     path('', views.leave_requests, name='leave_requests'),
#     path('apply/', views.apply_leave, name='apply_leave'),
#     path('<int:pk>/approve/', views.approve_leave, name='approve_leave'),
#     path('<int:pk>/reject/', views.reject_leave, name='reject_leave'),
#     path('<int:pk>/cancel/', views.cancel_leave, name='cancel_leave'),

#     # Leave Types
#     path('types/', views.leave_types, name='leave_types'),
#     path('types/add/', views.add_leave_type, name='add_leave_type'),
#     path('types/<int:pk>/edit/', views.edit_leave_type, name='edit_leave_type'),
#     path('types/<int:pk>/delete/', views.delete_leave_type, name='delete_leave_type'),

#     # Reports
#     path('reports/', views.leave_reports, name='leave_reports'),
# ]


from django.urls import path
from . import views
from . import manager_views

urlpatterns = [
    # Employee leave URLs
    path('', views.leave_requests, name='leave_requests'),
    path('apply/', views.apply_leave, name='apply_leave'),
    path('<int:pk>/approve/', views.approve_leave, name='approve_leave'),
    path('<int:pk>/reject/', views.reject_leave, name='reject_leave'),
    path('<int:pk>/cancel/', views.cancel_leave, name='cancel_leave'),
    path('types/', views.leave_types, name='leave_types'),
    path('types/add/', views.add_leave_type, name='add_leave_type'),
    path('types/<int:pk>/edit/', views.edit_leave_type, name='edit_leave_type'),
    path('types/<int:pk>/delete/', views.delete_leave_type, name='delete_leave_type'),
    path('reports/', views.leave_reports, name='leave_reports'),

    # Manager URLs
    path('manager/', manager_views.manager_leave_dashboard, name='manager_leave_dashboard'),
    path('manager/<int:pk>/detail/', manager_views.manager_leave_detail, name='manager_leave_detail'),
    path('manager/wfh/', manager_views.manager_wfh_dashboard, name='manager_wfh_dashboard'),
    path('manager/wfh/<int:pk>/approve/', manager_views.manager_approve_wfh, name='manager_approve_wfh'),
    path('manager/wfh/<int:pk>/reject/', manager_views.manager_reject_wfh, name='manager_reject_wfh'),

    # Projects
    path('projects/', manager_views.project_list, name='project_list'),
    path('projects/create/', manager_views.create_project, name='create_project'),
    path('projects/<int:pk>/assign/', manager_views.assign_project_members, name='assign_project_members'),
]