import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Employee

print("=== Employee User Creation ===\n")

for emp in Employee.objects.all():
    if emp.user is None:
        first    = emp.first_name.lower().strip().replace(' ', '')
        last     = emp.last_name.lower().strip().replace(' ', '')
        username = f"{first}.{last}"

        if User.objects.filter(username=username).exists():
            username = f"{first}.{emp.employee_id.lower()}"

        password = f"{emp.first_name.capitalize()}@{emp.employee_id}"

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=emp.first_name,
            last_name=emp.last_name,
            email=emp.email,
            is_staff=False,
            is_superuser=False,
        )
        emp.user = user
        emp.save()
        print(f"CREATED  | {emp.full_name}")
        print(f"          Username : {username}")
        print(f"          Password : {password}")
        print()
    else:
        print(f"EXISTS   | {emp.full_name} | Username: {emp.user.username}")

print("\n=== Done ===")