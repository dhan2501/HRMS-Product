# from django.urls import path
# from . import portal_views

# urlpatterns = [
#     path('', portal_views.portal_dashboard, name='portal_dashboard'),
#     path('attendance/', portal_views.portal_attendance, name='portal_attendance'),
#     path('leave/apply/', portal_views.portal_apply_leave, name='portal_apply_leave'),
#     path('leave/cancel/<int:pk>/', portal_views.portal_cancel_leave, name='portal_cancel_leave'),
#     path('payslips/', portal_views.portal_payslips, name='portal_payslips'),
#     path('payslips/<int:pk>/', portal_views.portal_payslip_detail, name='portal_payslip_detail'),
#     path('profile/', portal_views.portal_profile, name='portal_profile'),

#     # WFH
#     path('wfh/', portal_views.portal_wfh, name='portal_wfh'),
#     path('wfh/cancel/<int:pk>/', portal_views.portal_cancel_wfh, name='portal_cancel_wfh'),

# ]

# from django.urls import path
# from . import portal_views

# urlpatterns = [
#     path('', portal_views.portal_dashboard, name='portal_dashboard'),
#     path('attendance/', portal_views.portal_attendance, name='portal_attendance'),
#     path('leave/apply/', portal_views.portal_apply_leave, name='portal_apply_leave'),
#     path('leave/cancel/<int:pk>/', portal_views.portal_cancel_leave, name='portal_cancel_leave'),
#     path('payslips/', portal_views.portal_payslips, name='portal_payslips'),
#     path('payslips/<int:pk>/', portal_views.portal_payslip_detail, name='portal_payslip_detail'),
#     path('profile/', portal_views.portal_profile, name='portal_profile'),

#     # ✅ My Performance
#     path('performance/', portal_views.portal_performance, name='portal_performance'),
#     path('performance/<int:pk>/acknowledge/', portal_views.portal_performance_acknowledge, name='portal_performance_acknowledge'),

#     # WFH
#     path('wfh/', portal_views.portal_wfh, name='portal_wfh'),
#     path('wfh/cancel/<int:pk>/', portal_views.portal_cancel_wfh, name='portal_cancel_wfh'),

# ]

from django.urls import path
from . import portal_views

urlpatterns = [
    path('', portal_views.portal_dashboard, name='portal_dashboard'),
    path('attendance/', portal_views.portal_attendance, name='portal_attendance'),
    path('leave/apply/', portal_views.portal_apply_leave, name='portal_apply_leave'),
    path('leave/cancel/<int:pk>/', portal_views.portal_cancel_leave, name='portal_cancel_leave'),
    path('payslips/', portal_views.portal_payslips, name='portal_payslips'),
    path('payslips/<int:pk>/', portal_views.portal_payslip_detail, name='portal_payslip_detail'),
    path('profile/', portal_views.portal_profile, name='portal_profile'),

    # WFH
    path('wfh/', portal_views.portal_wfh, name='portal_wfh'),
    path('wfh/cancel/<int:pk>/', portal_views.portal_cancel_wfh, name='portal_cancel_wfh'),

    # Events & Holidays
    path('events/', portal_views.portal_events, name='portal_events'),

    # Mind Relaxation
    path('wellness/', portal_views.portal_wellness, name='portal_wellness'),

]