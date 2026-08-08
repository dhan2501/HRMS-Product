from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
import calendar
from datetime import date
from employees.models import Employee
from .models import SalaryStructure, Payslip

from functools import wraps
from django.shortcuts import redirect
from employees.models import Employee


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
        emp_id     = request.POST.get('employee')
        basic      = request.POST.get('basic', 0)
        hra        = request.POST.get('hra', 0)
        special_allowance = request.POST.get('special_allowance', 0)
        pf         = request.POST.get('pf_deduction', 0)
        prof_tax   = request.POST.get('professional_tax', 0)
        tax_regime = request.POST.get('tax_regime', 'new')
        ded_80c    = request.POST.get('deduction_80c', 0) or 0
        ded_80d    = request.POST.get('deduction_80d', 0) or 0
        eff_from   = request.POST.get('effective_from')

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
        structure.basic             = request.POST.get('basic', 0)
        structure.hra               = request.POST.get('hra', 0)
        structure.special_allowance = request.POST.get('special_allowance', 0)
        structure.pf_deduction      = request.POST.get('pf_deduction', 0)
        structure.professional_tax  = request.POST.get('professional_tax', 0)
        structure.tax_regime        = request.POST.get('tax_regime', 'new')
        structure.deduction_80c     = request.POST.get('deduction_80c', 0) or 0
        structure.deduction_80d     = request.POST.get('deduction_80d', 0) or 0
        structure.effective_from    = request.POST.get('effective_from')
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


# ── Generate Payslips ─────────────────────────────────────────────────────────
@login_required
def generate_payslips(request):
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
            net   = gross - s.pf_deduction - s.professional_tax - tds

            Payslip.objects.create(
                employee=s.employee,
                month=month,
                year=year,
                tax_regime=s.tax_regime,
                basic=s.basic,
                hra=s.hra,
                special_allowance=s.special_allowance,
                pf_deduction=s.pf_deduction,
                professional_tax=s.professional_tax,
                tds=tds,
                gross_salary=gross,
                net_salary=net,
                status='generated',
            )
            created += 1

        messages.success(request, f'{created} payslip(s) generated for {calendar.month_name[month]} {year}. {skipped} skipped (already exist).')
        return redirect(f'/payroll/payslips/?month={month}&year={year}')

    return redirect('payslips')


# ── Mark Payslip Paid ─────────────────────────────────────────────────────────
@login_required
def mark_paid(request, pk):
    slip = get_object_or_404(Payslip, pk=pk)
    if request.method == 'POST':
        slip.status       = 'paid'
        slip.payment_date = date.today()
        slip.save()
        messages.success(request, f'Payslip marked as paid for {slip.employee.full_name}.')
    return redirect('payslips')


# ── Payslip Detail ────────────────────────────────────────────────────────────
@login_required
def payslip_detail(request, pk):
    slip = get_object_or_404(Payslip, pk=pk)
    return render(request, 'payroll/payslip_detail.html', {'slip': slip})