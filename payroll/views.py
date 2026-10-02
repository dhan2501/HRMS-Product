from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
import calendar
from datetime import date
from employees.models import Employee
from .models import SalaryStructure, Payslip
from .payroll_calc import calculate_attendance_payroll

from functools import wraps
from django.shortcuts import redirect
from employees.models import Employee
from django.utils import timezone


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_login')
        if not (request.user.is_staff or request.user.is_superuser):
            try:
                Employee.objects.get(user=request.user)
                return redirect('portal_dashboard')
            except Employee.DoesNotExist:
                return redirect('employee_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def dec(post, key, default=0):
    """
    Safely pull a numeric field from request.POST.
    dict.get(key, default) only falls back when the key is MISSING —
    an empty string '' (blank optional form field) still gets returned
    as-is and blows up DecimalField.to_python(). This coerces '', None,
    and missing keys all to `default`.
    """
    return post.get(key, default) or default


# ── Salary Structure List ─────────────────────────────────────────────────────
@login_required
def salary_structure(request):
    search    = request.GET.get('search', '')
    dept_id   = request.GET.get('department', '')

    structures = SalaryStructure.objects.select_related(
        'employee', 'employee__department', 'employee__designation'
    ).all()

    if search:
        structures = structures.filter(
            Q(employee__first_name__icontains=search) |
            Q(employee__last_name__icontains=search)  |
            Q(employee__employee_id__icontains=search)
        )
    if dept_id:
        structures = structures.filter(employee__department_id=dept_id)

    # Employees without salary structure
    assigned_ids    = SalaryStructure.objects.values_list('employee_id', flat=True)
    unassigned_emps = Employee.objects.filter(status='active').exclude(id__in=assigned_ids)

    from employees.models import Department
    departments = Department.objects.all()

    total_payroll = sum(s.gross_salary for s in structures)

    return render(request, 'payroll/salary_structure.html', {
        'structures':      structures,
        'unassigned_emps': unassigned_emps,
        'departments':     departments,
        'total_payroll':   total_payroll,
        'search':          search,
        'selected_dept':   dept_id,
    })


# ── Add Salary Structure ──────────────────────────────────────────────────────
@login_required
def add_salary(request):
    # Only employees without existing salary structure
    assigned_ids = SalaryStructure.objects.values_list('employee_id', flat=True)
    employees    = Employee.objects.filter(status='active').exclude(id__in=assigned_ids)

    if request.method == 'POST':
        emp_id            = request.POST.get('employee')
        basic             = dec(request.POST, 'basic')
        hra               = dec(request.POST, 'hra')
        special_allowance = dec(request.POST, 'special_allowance')
        pf                = dec(request.POST, 'pf_deduction')
        prof_tax          = dec(request.POST, 'professional_tax')
        overtime_rate     = dec(request.POST, 'overtime_rate_per_hour')
        std_bonus         = dec(request.POST, 'standard_bonus')
        std_incentive     = dec(request.POST, 'standard_incentive')
        tax_regime        = request.POST.get('tax_regime', 'new')
        ded_80c           = dec(request.POST, 'deduction_80c')
        ded_80d           = dec(request.POST, 'deduction_80d')
        eff_from          = request.POST.get('effective_from')

        if not emp_id or not basic or not eff_from:
            messages.error(request, 'Employee, Basic Salary, and Effective From are required.')
        else:
            employee = get_object_or_404(Employee, pk=emp_id)
            SalaryStructure.objects.create(
                employee=employee,
                basic=basic,
                hra=hra,
                special_allowance=special_allowance,
                pf_deduction=pf,
                professional_tax=prof_tax,
                overtime_rate_per_hour=overtime_rate,
                standard_bonus=std_bonus,
                standard_incentive=std_incentive,
                tax_regime=tax_regime,
                deduction_80c=ded_80c,
                deduction_80d=ded_80d,
                effective_from=eff_from,
            )
            messages.success(request, f'Salary structure added for {employee.full_name}!')
            return redirect('salary_structure')

    return render(request, 'payroll/add_salary.html', {
        'employees': employees,
        'today':     date.today(),
    })


# ── Edit Salary Structure ─────────────────────────────────────────────────────
@login_required
def edit_salary(request, pk):
    structure = get_object_or_404(SalaryStructure, pk=pk)

    if request.method == 'POST':
        structure.basic                  = dec(request.POST, 'basic')
        structure.hra                    = dec(request.POST, 'hra')
        structure.special_allowance      = dec(request.POST, 'special_allowance')
        structure.pf_deduction           = dec(request.POST, 'pf_deduction')
        structure.professional_tax       = dec(request.POST, 'professional_tax')
        structure.overtime_rate_per_hour = dec(request.POST, 'overtime_rate_per_hour')
        structure.standard_bonus         = dec(request.POST, 'standard_bonus')
        structure.standard_incentive     = dec(request.POST, 'standard_incentive')
        structure.tax_regime             = request.POST.get('tax_regime', 'new')
        structure.deduction_80c          = dec(request.POST, 'deduction_80c')
        structure.deduction_80d          = dec(request.POST, 'deduction_80d')
        structure.effective_from         = request.POST.get('effective_from')
        structure.save()
        messages.success(request, f'Salary updated for {structure.employee.full_name}!')
        return redirect('salary_structure')

    return render(request, 'payroll/add_salary.html', {
        'structure': structure,
        'is_edit':   True,
        'today':     date.today(),
    })


# ── Delete Salary Structure ───────────────────────────────────────────────────
@login_required
def delete_salary(request, pk):
    structure = get_object_or_404(SalaryStructure, pk=pk)
    if request.method == 'POST':
        name = structure.employee.full_name
        structure.delete()
        messages.success(request, f'Salary structure removed for {name}.')
    return redirect('salary_structure')


# ── Payslip List ──────────────────────────────────────────────────────────────
@login_required
def payslips(request):
    today  = date.today()
    month  = int(request.GET.get('month', today.month))
    year   = int(request.GET.get('year', today.year))

    slips = Payslip.objects.filter(
        month=month, year=year
    ).select_related('employee', 'employee__department')

    total_gross = slips.aggregate(t=Sum('gross_salary'))['t'] or 0
    total_net   = slips.aggregate(t=Sum('net_salary'))['t'] or 0
    paid_count  = slips.filter(status='paid').count()

    # Month navigation
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    return render(request, 'payroll/payslips.html', {
        'slips':       slips,
        'month':       month,
        'year':        year,
        'month_name':  calendar.month_name[month],
        'total_gross': total_gross,
        'total_net':   total_net,
        'paid_count':  paid_count,
        'prev_month':  prev_month,
        'prev_year':   prev_year,
        'next_month':  next_month,
        'next_year':   next_year,
    })


# ── Generate Payslips (Attendance → Payroll automatic calculation) ────────────
@login_required
def generate_payslips(request):
    """
    Generates payslips for the given month/year. For every employee's
    SalaryStructure, this pulls their Attendance records for that month
    and automatically works out:
      - LOP (Loss-of-Pay) days/amount from absences
      - Overtime hours/amount from hours worked beyond their shift
    ESI is auto-computed from the statutory wage ceiling, and any
    recurring Bonus/Incentive configured on the salary structure is
    carried onto the payslip (both can still be fine-tuned afterwards
    via "Edit Payslip" before it's marked paid).
    """
    if request.method == 'POST':
        month = int(request.POST.get('month'))
        year  = int(request.POST.get('year'))

        structures = SalaryStructure.objects.select_related('employee').all()
        created = 0
        skipped = 0

        for s in structures:
            if Payslip.objects.filter(employee=s.employee, month=month, year=year).exists():
                skipped += 1
                continue

            gross = s.gross_salary
            tds   = s.monthly_tds
            esi   = s.esi_deduction

            # ── Attendance → Payroll automatic calculation ──────────────
            attendance = calculate_attendance_payroll(s.employee, s, month, year)

            bonus     = s.standard_bonus
            incentive = s.standard_incentive

            net = (
                gross + attendance['overtime_amount'] + bonus + incentive
                - s.pf_deduction - esi - s.professional_tax - tds - attendance['lop_amount']
            )

            Payslip.objects.create(
                employee=s.employee,
                month=month,
                year=year,
                tax_regime=s.tax_regime,
                basic=s.basic,
                hra=s.hra,
                special_allowance=s.special_allowance,
                pf_deduction=s.pf_deduction,
                esi_deduction=esi,
                professional_tax=s.professional_tax,
                tds=tds,
                payable_days=attendance['payable_days'],
                present_days=attendance['present_days'],
                lop_days=attendance['lop_days'],
                lop_amount=attendance['lop_amount'],
                overtime_hours=attendance['overtime_hours'],
                overtime_amount=attendance['overtime_amount'],
                bonus=bonus,
                incentive=incentive,
                gross_salary=gross,
                net_salary=net,
                status='generated',
            )
            created += 1

        messages.success(request, f'{created} payslip(s) generated for {calendar.month_name[month]} {year}. {skipped} skipped (already exist).')
        return redirect(f'/payroll/payslips/?month={month}&year={year}')

    return redirect('payslips')


# ── Edit Payslip (fine-tune Overtime / Bonus / Incentive / LOP before payment) ─
@login_required
def edit_payslip(request, pk):
    slip = get_object_or_404(Payslip, pk=pk)

    if slip.status == 'paid':
        messages.error(request, 'A paid payslip cannot be edited.')
        return redirect('payslip_detail', pk=slip.pk)

    if request.method == 'POST':
        slip.overtime_hours  = dec(request.POST, 'overtime_hours')
        slip.overtime_amount = dec(request.POST, 'overtime_amount')
        slip.bonus           = dec(request.POST, 'bonus')
        slip.incentive       = dec(request.POST, 'incentive')
        slip.lop_days        = dec(request.POST, 'lop_days')
        slip.lop_amount      = dec(request.POST, 'lop_amount')
        slip.recompute_net_salary()
        slip.save()
        messages.success(request, f'Payslip updated for {slip.employee.full_name}.')
        return redirect('payslip_detail', pk=slip.pk)

    return render(request, 'payroll/edit_payslip.html', {'slip': slip})


# ── Mark Payslip Paid ─────────────────────────────────────────────────────────
@login_required
def mark_paid(request, pk):
    slip = get_object_or_404(Payslip, pk=pk)
    if request.method == 'POST':
        slip.status       = 'paid'
        slip.payment_date = date.today()

        # Auto-approve for release the moment it's marked Paid — employee
        # can print/download immediately, no separate approval step needed.
        slip.is_approved = True
        slip.approved_by = Employee.objects.filter(user=request.user).first()
        slip.approved_at = timezone.now()

        slip.save()
        messages.success(request, f'Payslip marked as paid for {slip.employee.full_name}. Employee can now print/download it.')
    return redirect('payslips')

# ── Payslip Detail ────────────────────────────────────────────────────────────
@login_required
def payslip_detail(request, pk):
    slip = get_object_or_404(Payslip, pk=pk)
    return render(request, 'payroll/payslip_detail.html', {'slip': slip})


# ── Approve Payslip for Release (HR / Super Admin only) ───────────────────────
@admin_required
def approve_payslip(request, pk):
    """
    Final HR/Super Admin sign-off before an employee is allowed to
    print/download their payslip. Only allowed once the payslip is
    already marked Paid.
    """
    slip = get_object_or_404(Payslip, pk=pk)
    if request.method == 'POST':
        if slip.status != 'paid':
            messages.error(request, 'Only a Paid payslip can be approved for release.')
        else:
            approver = Employee.objects.filter(user=request.user).first()
            slip.is_approved = True
            slip.approved_by = approver
            slip.approved_at = timezone.now()
            slip.save()
            messages.success(
                request,
                f'Payslip approved & released for {slip.employee.full_name}. '
                f'They can now print/download it.'
            )
    return redirect('payslip_detail', pk=pk)


# ── Revoke Payslip Approval (HR / Super Admin only) ────────────────────────────
@admin_required
def revoke_payslip_approval(request, pk):
    slip = get_object_or_404(Payslip, pk=pk)
    if request.method == 'POST':
        slip.is_approved = False
        slip.approved_by = None
        slip.approved_at = None
        slip.save()
        messages.success(request, f'Release approval revoked for {slip.employee.full_name}.')
    return redirect('payslip_detail', pk=pk)

# ── Approve Payslip for Release (HR / Super Admin only) ───────────────────────
@admin_required
def approve_payslip(request, pk):
    """
    Final HR/Super Admin sign-off before an employee is allowed to
    print/download their payslip. Only allowed once the payslip is
    already marked Paid.
    """
    slip = get_object_or_404(Payslip, pk=pk)
    if request.method == 'POST':
        if slip.status != 'paid':
            messages.error(request, 'Only a Paid payslip can be approved for release.')
        else:
            approver = Employee.objects.filter(user=request.user).first()
            slip.is_approved = True
            slip.approved_by = approver
            slip.approved_at = timezone.now()
            slip.save()
            messages.success(
                request,
                f'Payslip approved & released for {slip.employee.full_name}. '
                f'They can now print/download it.'
            )
    return redirect(request.META.get('HTTP_REFERER') or reverse('payslip_detail', args=[pk]))


# ── Revoke Payslip Approval (HR / Super Admin only) ────────────────────────────
@admin_required
def revoke_payslip_approval(request, pk):
    slip = get_object_or_404(Payslip, pk=pk)
    if request.method == 'POST':
        slip.is_approved = False
        slip.approved_by = None
        slip.approved_at = None
        slip.save()
        messages.success(request, f'Release approval revoked for {slip.employee.full_name}.')
    return redirect(request.META.get('HTTP_REFERER') or reverse('payslip_detail', args=[pk]))