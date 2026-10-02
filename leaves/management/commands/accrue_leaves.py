from django.core.management.base import BaseCommand

from employees.models import Employee
from leaves import services as leave_services


class Command(BaseCommand):
    help = "Sabhi active employees ke liye leave balances create/refresh karo aur EL monthly accrue karo."

    def handle(self, *args, **options):
        employees = Employee.objects.filter(status='active')
        count = 0
        for employee in employees:
            leave_services.sync_leave_balances_for_employee(employee)
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Leave balances synced for {count} active employee(s)."))