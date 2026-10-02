# """
# Har active employee ke liye ek AttendanceRecord(status='absent') bana deta hai
# agar us din unka koi punch (AttendanceRecord) hi nahi hai — taaki employee
# portal / HR assistant / reports mein "Not Marked" ki jagah "Absent" dikhe.

# Kis din ko SKIP karta hai (in par kabhi absent nahi lagta):
#     - Weekend (Saturday, Sunday)
#     - Holiday (attendance.Holiday)
#     - Approved leave jo us date ko cover karti ho (leaves.LeaveRequest)
#     - Approved WFH request us date ke liye (attendance.WorkFromHomeRequest)
#     - Employee jiska status 'active' nahi hai

# Run manually (yesterday ke liye — default, kyunki din poora complete ho chuka hota hai):
#     python manage.py mark_absentees

# Kisi specific date ke liye:
#     python manage.py mark_absentees --date 2026-08-30

# Recommended: cron / Railway scheduled job se roz raat ~00:15 baje chalao,
# taaki "aaj" ka din poora complete hone ke baad hi absent mark ho
# (warna jo log thoda late punch karte hain unhe galat absent lag jayega).

# Example cron entry (roz raat 00:15 par, previous day ke liye):
#     15 0 * * * cd /path/to/project && /path/to/venv/bin/python manage.py mark_absentees
# """
# from datetime import date, timedelta

# from django.core.management.base import BaseCommand

# from employees.models import Employee
# from attendance.models import AttendanceRecord, Holiday, WorkFromHomeRequest
# from leaves.models import LeaveRequest


# class Command(BaseCommand):
#     help = "Punch-in/out na karne wale active employees ko diye gaye date ke liye 'Absent' mark karta hai."

#     def add_arguments(self, parser):
#         parser.add_argument(
#             '--date',
#             type=str,
#             default=None,
#             help="YYYY-MM-DD format. Default: kal (yesterday), kyunki woh din poora complete ho chuka hota hai.",
#         )

#     def handle(self, *args, **options):
#         if options['date']:
#             target_date = date.fromisoformat(options['date'])
#         else:
#             target_date = date.today() - timedelta(days=1)

#         # Weekend (Sat/Sun) skip
#         if target_date.weekday() in (5, 6):
#             self.stdout.write(f"{target_date} ek weekend hai — skip kar diya.")
#             return

#         # Holiday skip
#         if Holiday.objects.filter(date=target_date).exists():
#             self.stdout.write(f"{target_date} ek holiday hai — skip kar diya.")
#             return

#         active_employees = Employee.objects.filter(status='active')

#         # Jinka pehle se attendance record hai (present/late/wfh/half_day/absent — kuch bhi)
#         already_marked_ids = AttendanceRecord.objects.filter(
#             date=target_date
#         ).values_list('employee_id', flat=True)

#         # Jo approved leave par hain us din
#         on_leave_ids = LeaveRequest.objects.filter(
#             status='approved',
#             start_date__lte=target_date,
#             end_date__gte=target_date,
#         ).values_list('employee_id', flat=True)

#         # Jo approved WFH par hain us din
#         on_wfh_ids = WorkFromHomeRequest.objects.filter(
#             status='approved',
#             date=target_date,
#         ).values_list('employee_id', flat=True)

#         to_mark = active_employees.exclude(
#             id__in=list(already_marked_ids)
#         ).exclude(
#             id__in=list(on_leave_ids)
#         ).exclude(
#             id__in=list(on_wfh_ids)
#         )

#         created = 0
#         for employee in to_mark:
#             AttendanceRecord.objects.create(
#                 employee=employee,
#                 date=target_date,
#                 status='absent',
#             )
#             created += 1

#         self.stdout.write(
#             self.style.SUCCESS(f"{target_date}: {created} employee(s) ko 'Absent' mark kiya gaya.")
#         )

"""
Auto-Absent marking for employees jinhone punch in/out nahi kiya.

Har din ke end me: jis active employee ka us date ke liye koi PunchLog nahi
hai, aur woh weekend/holiday/approved-leave nahi hai, aur AttendanceRecord
pehle se nahi bana hai -- uske liye AttendanceRecord status='absent' save
kar deta hai. Ye same logic employee portal aur admin calendar khulne par
bhi "self-heal" ke roop me chalti hai (attendance/services.py:
backfill_absentees), lekin ye command un employees ke liye zaroori hai jo
kabhi portal khud nahi kholte -- taaki payroll/LOP calculation ke liye
Absent record bina kisi manual action ke ban jaaye.

Run manually:
    python manage.py mark_absentees                     # kal (yesterday) mark karega
    python manage.py mark_absentees --date 2026-08-30    # specific date
    python manage.py mark_absentees --days-back 7        # pichhle 7 din backfill

Recommended: isko roz raat ko (midnight ke thodi der baad) cron se chalao,
taaki har weekday ka Absent record turant ban jaaye.

Example cron entry (daily 00:15 AM par):
    15 0 * * * cd /path/to/project && /path/to/venv/bin/python manage.py mark_absentees
"""
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from employees.models import Employee
from attendance.services import backfill_absentees


class Command(BaseCommand):
    help = (
        "Active employees ke liye 'Absent' AttendanceRecord bana deta hai "
        "un past working day(s) ke liye jinme koi punch nahi hua (aur jo "
        "holiday / weekend / approved leave nahi hai)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--date', type=str, default=None,
            help="YYYY-MM-DD. Default: kal (yesterday).",
        )
        parser.add_argument(
            '--days-back', type=int, default=1,
            help="Kitne pichhle din backfill karne hain (--date se ginte hue peeche). Default 1.",
        )

    def handle(self, *args, **options):
        if options.get('date'):
            end_date = date.fromisoformat(options['date'])
        else:
            end_date = date.today() - timedelta(days=1)

        days_back = max(1, options['days_back'])
        start_date = end_date - timedelta(days=days_back - 1)

        employees = Employee.objects.filter(status='active')
        created_count = backfill_absentees(start_date, end_date, employees=employees)

        if created_count:
            self.stdout.write(self.style.SUCCESS(
                f"Done: {created_count} employee-day record(s) 'Absent' mark/recompute hue "
                f"({start_date} se {end_date} tak)."
            ))
        else:
            self.stdout.write(
                f"Kuch bhi missing nahi mila ({start_date} se {end_date} tak) -- sab records pehle se sahi hain."
            )