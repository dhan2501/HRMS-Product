from django.core.management.base import BaseCommand
from employees.models import Employee


class Command(BaseCommand):
    """
    Debug helper: 'Team Expenses' / 'Team Requests' / 'Team Overview' only
    show up for an employee if someone else's `reporting_manager` field
    points at them. If that field is blank, the manager's portal sidebar
    silently hides the whole "Manage" section — no error, nothing to see.

    Run:  python manage.py audit_reporting_managers
    Optionally scope to one employee:
          python manage.py audit_reporting_managers --employee-id EMP0012
    """
    help = "List employees with no reporting_manager set, and each active employee's current team size."

    def add_arguments(self, parser):
        parser.add_argument('--employee-id', type=str, default=None,
                             help='Only show this employee (by employee_id) and their reportees.')

    def handle(self, *args, **options):
        emp_id = options.get('employee_id')

        if emp_id:
            try:
                emp = Employee.objects.get(employee_id=emp_id)
            except Employee.DoesNotExist:
                self.stderr.write(self.style.ERROR(f'No employee with employee_id={emp_id}'))
                return
            reportees = emp.team_members.all()
            self.stdout.write(f'{emp.full_name} ({emp.employee_id}) has {reportees.count()} direct report(s):')
            for r in reportees:
                self.stdout.write(f'  - {r.full_name} ({r.employee_id}) status={r.status}')
            if not reportees.exists():
                self.stdout.write(self.style.WARNING(
                    '  No one has this employee set as reporting_manager -> '
                    '"Team Requests / Team Expenses" will NOT appear in their portal sidebar.'
                ))
            return

        no_manager = Employee.objects.filter(reporting_manager__isnull=True, status='active').order_by('first_name')
        self.stdout.write(self.style.WARNING(f'\nActive employees with NO reporting_manager set ({no_manager.count()}):'))
        for e in no_manager:
            self.stdout.write(f'  - {e.full_name} ({e.employee_id}) - {e.designation or "no designation"}')

        self.stdout.write('\nEach active employee currently acting as a Reporting Manager, and team size:')
        managers = Employee.objects.filter(status='active')
        any_manager = False
        for e in managers:
            count = e.team_members.count()
            if count:
                any_manager = True
                self.stdout.write(f'  - {e.full_name} ({e.employee_id}): {count} report(s)')
        if not any_manager:
            self.stdout.write(self.style.ERROR('  None. No active employee has any reportees at all.'))

        self.stdout.write(self.style.SUCCESS(
            '\nFix: Employee List -> open the employee -> Edit -> set "Reporting Manager" '
            'to the correct manager -> Save. The manager will then see "Team Overview / '
            'Team Requests / Team Expenses" in their portal sidebar immediately.'
        ))