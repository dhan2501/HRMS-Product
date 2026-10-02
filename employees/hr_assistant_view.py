# employees/hr_assistant_view.py
#
# New, standalone Employee Self-Service AI Assistant.
# Completely separate and independent from the old employees/chatbot_view.py
# (HR/Admin tool — data for all employees). This one only shows the
# logged-in employee's own data (attendance, leave, holiday, WFH) — never
# another employee's data.

import json
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from employees.models import Employee
from attendance.models import AttendanceRecord, Holiday, WorkFromHomeRequest
from leaves.models import LeaveRequest, LeaveBalance

from groq import Groq
from django.conf import settings



def _build_employee_context(employee):
    """Only this employee's own data — attendance, leave, holiday, WFH."""
    today = date.today()
    year = today.year

    # --- Today's attendance ---
    today_att = AttendanceRecord.objects.filter(employee=employee, date=today).first()
    today_status = today_att.get_status_display() if today_att else 'Not Marked'
    check_in = today_att.check_in.strftime('%H:%M') if today_att and today_att.check_in else 'N/A'
    check_out = today_att.check_out.strftime('%H:%M') if today_att and today_att.check_out else 'N/A'

    # --- Last 14 days attendance ---
    recent_att = AttendanceRecord.objects.filter(
        employee=employee, date__gte=today - timedelta(days=14), date__lte=today
    ).order_by('-date')
    att_lines = [
        f"• {a.date} | {a.get_status_display()} | In: {a.check_in.strftime('%H:%M') if a.check_in else 'N/A'} "
        f"| Out: {a.check_out.strftime('%H:%M') if a.check_out else 'N/A'}"
        for a in recent_att
    ]

    # --- This month summary ---
    month_att = AttendanceRecord.objects.filter(employee=employee, date__month=today.month, date__year=today.year)
    present_count = month_att.filter(status__in=['present', 'late', 'work_from_home']).count()
    absent_count = month_att.filter(status='absent').count()
    late_count = month_att.filter(status='late').count()

    # --- Leave balance (current year) ---
    balances = LeaveBalance.objects.filter(employee=employee, year=year).select_related('leave_type')
    balance_lines = [
        f"• {b.leave_type.name}: Total {b.total_days} | Used {b.used_days} | "
        f"Pending {b.pending_days} | Available {b.available_days}"
        for b in balances
    ]

    # --- Own leave requests (recent 10) ---
    leave_reqs = LeaveRequest.objects.filter(employee=employee).select_related('leave_type').order_by('-created_at')[:10]
    leave_lines = [
        f"• {lr.leave_type.name} | {lr.start_date} to {lr.end_date} ({lr.days} days) | "
        f"Status: {lr.get_status_display()}"
        for lr in leave_reqs
    ]

    # --- Own WFH requests (recent 10) ---
    wfh_reqs = WorkFromHomeRequest.objects.filter(employee=employee).order_by('-created_at')[:10]
    wfh_lines = [f"• {w.date} | Status: {w.get_status_display()}" for w in wfh_reqs]

    # --- Upcoming holidays (company-wide list, not employee-specific) ---
    upcoming_holidays = Holiday.objects.filter(date__gte=today).order_by('date')[:10]
    holiday_lines = [
        f"• {h.date} | {h.name}" + (" (Optional)" if h.is_optional else "")
        for h in upcoming_holidays
    ]

    return f"""You are HRMS's Employee Self-Service AI Assistant. Only provide information about the attendance, leave, WFH, and holidays of the employee described BELOW.

RULES:
- Only use the data provided below — you do not have any other employee's data.
- If asked about another employee, department headcount, or "who is present today" type questions, politely say you can only help with their own attendance/leave/holiday info.
- You cannot apply for or cancel a new leave or WFH request — tell them to use the "Apply Leave" / "WFH" page on the Portal.
- Match the user's language AND script exactly. If they type in English, reply in English. If they type in Hinglish (Hindi words in Roman/English letters), reply in Hinglish using Roman letters too — never switch to Devanagari script. Only use Devanagari if the user themselves types in Devanagari.
- Keep answers short and clear, use bullet points for lists.

EMPLOYEE: {employee.full_name} ({employee.employee_id})
Department: {employee.department.name if employee.department else 'N/A'}
Designation: {employee.designation.title if employee.designation else 'N/A'}

=== TODAY ({today}) ===
Status: {today_status} | Check-in: {check_in} | Check-out: {check_out}

=== THIS MONTH'S SUMMARY ({today.strftime('%B %Y')}) ===
Present: {present_count} | Absent: {absent_count} | Late: {late_count}

=== LAST 14 DAYS' ATTENDANCE ===
{chr(10).join(att_lines) if att_lines else 'No records found for this period'}

=== LEAVE BALANCE ({year}) ===
{chr(10).join(balance_lines) if balance_lines else 'Leave balance not set yet'}

=== MY LEAVE REQUESTS (recent) ===
{chr(10).join(leave_lines) if leave_lines else 'No leave requests'}

=== MY WFH REQUESTS (recent) ===
{chr(10).join(wfh_lines) if wfh_lines else 'No WFH requests'}

=== UPCOMING HOLIDAYS ===
{chr(10).join(holiday_lines) if holiday_lines else 'No upcoming holidays in the list'}
"""


@login_required
def employee_assistant_api(request):
    """Employee Self-Service AI Assistant — attendance / leave / holiday / WFH, own data only."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        employee = Employee.objects.select_related('department', 'designation').get(user=request.user)
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'No employee profile is linked to this account.'}, status=403)

    try:
        body = json.loads(request.body)
        messages = body.get('messages', [])
        if not messages:
            return JsonResponse({'error': 'No messages'}, status=400)

        clean_messages = [
            {'role': m.get('role'), 'content': m.get('content')}
            for m in messages
            if m.get('role') in ('user', 'assistant') and m.get('content')
        ]
        if not clean_messages:
            return JsonResponse({'error': 'No valid messages'}, status=400)

        system_context = _build_employee_context(employee)

        client = Groq(api_key=settings.GROQ_API_KEY)
        groq_messages = [{'role': 'system', 'content': system_context}] + clean_messages
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            max_tokens=1000,
            messages=groq_messages,
        )
        reply = response.choices[0].message.content
        return JsonResponse({'reply': reply})

    # except Exception:
    #     return JsonResponse({'error': 'Assistant is not available right now. Please try again later.'}, status=500)
    except Exception as e:
        import traceback
        traceback.print_exc()  # full error will show in the terminal
        return JsonResponse({'error': f'DEBUG: {str(e)}'}, status=500)