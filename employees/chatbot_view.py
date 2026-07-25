# employees/chatbot_view.py
# Add this to your Django project

import json
import anthropic
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from datetime import date
from employees.models import Employee, Department
from attendance.models import AttendanceRecord
from leaves.models import LeaveRequest
from attendance.models import WorkFromHomeRequest


def build_hrms_context(request):
    """Build real-time HRMS context from Django DB."""
    today = date.today()

    # Employees
    employees = Employee.objects.select_related('department', 'designation').all()
    departments = Department.objects.all()

    # Today attendance
    today_att = AttendanceRecord.objects.filter(date=today).select_related('employee')
    att_map = {a.employee_id: a for a in today_att}

    # Pending requests
    pending_leaves = LeaveRequest.objects.filter(status='pending').select_related('employee', 'leave_type')
    pending_wfh    = WorkFromHomeRequest.objects.filter(status='pending').select_related('employee')

    # Build employee list
    emp_lines = []
    for emp in employees:
        att = att_map.get(emp.id)
        att_status = att.status if att else 'not_marked'
        check_in   = att.check_in.strftime('%H:%M') if att and att.check_in else 'N/A'
        emp_lines.append(
            f"• {emp.full_name} ({emp.employee_id}) | "
            f"{emp.designation.title if emp.designation else 'N/A'} | "
            f"{emp.department.name if emp.department else 'N/A'} | "
            f"Status: {emp.status} | "
            f"Today: {att_status} | Check-in: {check_in} | "
            f"Email: {emp.email} | Phone: {emp.phone or 'N/A'} | "
            f"Joined: {emp.date_joined}"
        )

    # Department summary
    dept_lines = []
    for dept in departments:
        count = dept.employees.filter(status='active').count()
        dept_lines.append(f"• {dept.name} ({dept.code}) - {count} active employees")

    # Pending leaves
    leave_lines = []
    for lr in pending_leaves[:10]:
        leave_lines.append(
            f"• {lr.employee.full_name}: {lr.leave_type.name} | "
            f"{lr.start_date} to {lr.end_date} ({lr.days} days) | PENDING"
        )

    # WFH requests
    wfh_lines = []
    for wfh in pending_wfh[:10]:
        wfh_lines.append(f"• {wfh.employee.full_name}: {wfh.date} | PENDING")

    total     = employees.count()
    active    = employees.filter(status='active').count()
    present   = today_att.filter(status__in=['present', 'late', 'work_from_home']).count()
    on_leave  = today_att.filter(status='absent').count()

    # Get current user's employee info
    current_user_info = ""
    try:
        current_emp = Employee.objects.get(user=request.user)
        current_att = att_map.get(current_emp.id)
        current_user_info = f"""
CURRENT USER: {current_emp.full_name} ({current_emp.employee_id})
- Department: {current_emp.department.name if current_emp.department else 'N/A'}
- Designation: {current_emp.designation.title if current_emp.designation else 'N/A'}
- Today's Status: {current_att.status if current_att else 'Not Marked'}
- Is HR Admin: {'Yes' if request.user.is_staff else 'No'}
"""
    except Employee.DoesNotExist:
        current_user_info = f"CURRENT USER: {request.user.username} (Admin/Staff)"

    context = f"""You are an intelligent HR Assistant for WorkForce HRMS. You have real-time access to HR data. Be helpful, precise, and conversational. Use emojis appropriately.

{current_user_info}

=== LIVE HRMS DATA ({today}) ===

SUMMARY:
- Total Employees: {total} | Active: {active}
- Present Today: {present}/{total}
- Pending Leave Requests: {pending_leaves.count()}
- Pending WFH Requests: {pending_wfh.count()}

ALL EMPLOYEES:
{chr(10).join(emp_lines) if emp_lines else 'No employees found'}

DEPARTMENTS:
{chr(10).join(dept_lines) if dept_lines else 'No departments found'}

PENDING LEAVE REQUESTS:
{chr(10).join(leave_lines) if leave_lines else 'No pending leave requests'}

PENDING WFH REQUESTS:
{chr(10).join(wfh_lines) if wfh_lines else 'No pending WFH requests'}

=== INSTRUCTIONS ===
- Answer based on above real-time data only
- Be specific with names, IDs, dates
- For approve/reject requests: acknowledge but say it needs to be done in the dashboard
- Support both Hindi and English queries
- Keep responses concise but complete
- Format with bullet points for lists
- If asking about a specific employee, give full details"""

    return context


@login_required
@csrf_exempt
def chatbot_api(request):
    """Handle chatbot messages."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        body     = json.loads(request.body)
        messages = body.get('messages', [])
        
        if not messages:
            return JsonResponse({'error': 'No messages'}, status=400)

        system_context = build_hrms_context(request)

        client   = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=system_context,
            messages=messages,
        )

        reply = response.content[0].text
        return JsonResponse({'reply': reply})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)