import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings')
django.setup()

from attendance.models import ShiftTiming

print("=== Shift Timing Setup ===\n")

# Yahan jitni chahe utni alag-alag shifts add kar sakte ho.
# Har entry ek naya "Shift Timing" record banayegi (agar wo naam se pehle se nahi hai).
SHIFTS = [
    {
        "name": "General Shift",
        "start_time": "09:00",
        "end_time": "18:00",
        "working_hours": 9.00,
        "grace_minutes": 10,
        "is_active": True,
    },
    {
        "name": "Morning Shift",
        "start_time": "07:00",
        "end_time": "15:00",
        "working_hours": 8.00,
        "grace_minutes": 10,
        "is_active": True,
    },
    {
        "name": "Evening Shift",
        "start_time": "15:00",
        "end_time": "23:00",
        "working_hours": 8.00,
        "grace_minutes": 10,
        "is_active": True,
    },
    {
        "name": "Night Shift",
        "start_time": "22:00",
        "end_time": "07:00",
        "working_hours": 9.00,
        "grace_minutes": 15,
        "is_active": True,
    },
    {
        "name": "Half Day Shift",
        "start_time": "09:00",
        "end_time": "13:00",
        "working_hours": 4.00,
        "grace_minutes": 5,
        "is_active": True,
    },
]

for data in SHIFTS:
    shift, created = ShiftTiming.objects.get_or_create(
        name=data["name"],
        defaults={
            "start_time": data["start_time"],
            "end_time": data["end_time"],
            "working_hours": data["working_hours"],
            "grace_minutes": data["grace_minutes"],
            "is_active": data["is_active"],
        },
    )
    if created:
        print(f"CREATED  | {shift.name} | {shift.start_time} - {shift.end_time} | {shift.working_hours}h")
    else:
        print(f"EXISTS   | {shift.name}")

print("\n=== Done ===")