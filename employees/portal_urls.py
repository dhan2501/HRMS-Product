from django.urls import path
from . import portal_views

urlpatterns = [
    path('', portal_views.portal_dashboard, name='portal_dashboard'),
    path('punch/', portal_views.portal_punch, name='portal_punch'),
    path('attendance/', portal_views.portal_attendance, name='portal_attendance'),
    path('leave/apply/', portal_views.portal_apply_leave, name='portal_apply_leave'),
    path('leave/cancel/<int:pk>/', portal_views.portal_cancel_leave, name='portal_cancel_leave'),
    path('payslips/', portal_views.portal_payslips, name='portal_payslips'),
    path('payslips/<int:pk>/', portal_views.portal_payslip_detail, name='portal_payslip_detail'),
    path('profile/', portal_views.portal_profile, name='portal_profile'),

    # WFH
    path('wfh/', portal_views.portal_wfh, name='portal_wfh'),
    path('wfh/cancel/<int:pk>/', portal_views.portal_cancel_wfh, name='portal_cancel_wfh'),

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

]