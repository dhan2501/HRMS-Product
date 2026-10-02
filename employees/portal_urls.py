from django.urls import path
from . import portal_views
from . import hr_assistant_view

urlpatterns = [
    path('', portal_views.portal_dashboard, name='portal_dashboard'),
    path('punch/', portal_views.portal_punch, name='portal_punch'),
    path('attendance/', portal_views.portal_attendance, name='portal_attendance'),
    path('leave/apply/', portal_views.portal_apply_leave, name='portal_apply_leave'),
    path('leave/cancel/<int:pk>/', portal_views.portal_cancel_leave, name='portal_cancel_leave'),
    path('payslips/', portal_views.portal_payslips, name='portal_payslips'),
    path('payslips/<int:pk>/', portal_views.portal_payslip_detail, name='portal_payslip_detail'),

    # Expense Claims
    path('expenses/', portal_views.portal_apply_expense, name='portal_apply_expense'),
    path('expenses/cancel/<int:pk>/', portal_views.portal_cancel_expense, name='portal_cancel_expense'),
    path('expenses/team/', portal_views.portal_team_expenses, name='portal_team_expenses'),
    path('expenses/team/<int:pk>/approve/', portal_views.portal_team_expense_approve, name='portal_team_expense_approve'),
    path('expenses/team/<int:pk>/reject/', portal_views.portal_team_expense_reject, name='portal_team_expense_reject'),

    path('profile/', portal_views.portal_profile, name='portal_profile'),
    path('profile/bank-details/', portal_views.portal_edit_bank_details, name='portal_edit_bank_details'),

    # WFH
    path('wfh/', portal_views.portal_wfh, name='portal_wfh'),
    path('wfh/cancel/<int:pk>/', portal_views.portal_cancel_wfh, name='portal_cancel_wfh'),

    # Team Overview (Reporting Manager: today's attendance + who's on which project)
    path('team-overview/', portal_views.portal_team_overview, name='portal_team_overview'),

    # Team Requests (Reporting Manager approves their team's Leave/WFH)
    path('team-requests/', portal_views.portal_team_requests, name='portal_team_requests'),
    path('team-requests/leave/<int:pk>/approve/', portal_views.portal_team_leave_approve, name='portal_team_leave_approve'),
    path('team-requests/leave/<int:pk>/reject/', portal_views.portal_team_leave_reject, name='portal_team_leave_reject'),
    path('team-requests/wfh/<int:pk>/approve/', portal_views.portal_team_wfh_approve, name='portal_team_wfh_approve'),
    path('team-requests/wfh/<int:pk>/reject/', portal_views.portal_team_wfh_reject, name='portal_team_wfh_reject'),

    # Events & Holidays
    path('events/', portal_views.portal_events, name='portal_events'),

    # Mind Relaxation
    path('wellness/', portal_views.portal_wellness, name='portal_wellness'),

    path('face/enroll/', portal_views.portal_face_enroll, name='portal_face_enroll'),
    path('face/enroll/save/', portal_views.portal_face_enroll_save, name='portal_face_enroll_save'),
    path('face/punch/', portal_views.portal_face_punch, name='portal_face_punch'),
    path('face/punch/verify/', portal_views.portal_face_punch_verify, name='portal_face_punch_verify'),

    # My Projects / Assignments
    path('projects/', portal_views.portal_my_projects, name='portal_my_projects'),
    path('projects/add/', portal_views.portal_add_project, name='portal_add_project'),
    path('projects/<int:pk>/', portal_views.portal_project_detail, name='portal_project_detail'),

    # Notifications (e.g. "teammate is on leave")
    path('notifications/', portal_views.portal_notifications, name='portal_notifications'),


    path('announcements/<int:pk>/json/', portal_views.portal_announcement_json, name='portal_announcement_json'),
    # employees/portal_urls.py — portal_announcement_json url se PEHLE

    path('announcements/', portal_views.portal_announcements, name='portal_announcements'),

    
    # Birthday Calendar
    path('birthdays/', portal_views.portal_birthday_calendar, name='portal_birthday_calendar'),

    # Attendance / Leave Claims
    path('disputes/', portal_views.portal_disputes, name='portal_disputes'),
    path('disputes/raise/', portal_views.portal_raise_dispute, name='portal_raise_dispute'),
    path('disputes/<int:pk>/cancel/', portal_views.portal_cancel_dispute, name='portal_cancel_dispute'),

    # Naya Employee Self-Service AI Assistant (attendance / leave / holiday / WFH)
    path('assistant/api/', hr_assistant_view.employee_assistant_api, name='portal_assistant_api'),
]