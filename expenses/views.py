from functools import wraps
from datetime import date
import calendar

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone

from employees.models import Employee
from .models import ExpenseClaim, ExpenseComment


# ── Access control (same pattern as payroll app) ──────────────────────────────
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


def get_hr_employee(request):
    """Best-effort Employee record for the logged-in staff/HR user (used to
    stamp who reviewed/reimbursed a claim). Staff users don't always have an
    Employee profile, so this can legitimately return None."""
    try:
        return Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return None


def log_action(expense, action, by_employee, comment=''):
    ExpenseComment.objects.create(
        expense=expense, action=action, by_employee=by_employee, comment=comment
    )

def notify_employee(expense, title, message):
    """Drop an in-app Notification for the claim owner so they actually see
    status changes (manager/finance approve or reject, reimbursement) in
    their portal bell instead of having to keep re-checking the page."""
    try:
        from employees.models import Notification
        Notification.objects.create(
            recipient=expense.employee,
            title=title,
            message=message,
            link_name='portal_apply_expense',
        )
    except Exception:
        pass


# ── Finance/HR: Expense Claims list ────────────────────────────────────────────
@admin_required
def expense_requests(request):
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')

    claims = ExpenseClaim.objects.select_related(
        'employee', 'employee__department'
    ).all()

    if search:
        claims = claims.filter(
            Q(employee__first_name__icontains=search) |
            Q(employee__last_name__icontains=search) |
            Q(employee__employee_id__icontains=search) |
            Q(description__icontains=search)
        )
    if status_filter:
        claims = claims.filter(status=status_filter)
    if category_filter:
        claims = claims.filter(category=category_filter)

    all_claims = ExpenseClaim.objects.all()
    pending_count = all_claims.filter(status__in=['pending_manager', 'pending_finance']).count()
    approved_count = all_claims.filter(status='approved').count()
    reimbursed_count = all_claims.filter(status='reimbursed').count()
    total_reimbursed_amount = all_claims.filter(status='reimbursed').aggregate(t=Sum('amount'))['t'] or 0

    return render(request, 'expenses/requests.html', {
        'claims': claims,
        'search': search,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'status_choices': ExpenseClaim.STATUS_CHOICES,
        'category_choices': ExpenseClaim.CATEGORY_CHOICES,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'reimbursed_count': reimbursed_count,
        'total_reimbursed_amount': total_reimbursed_amount,
        'total_count': all_claims.count(),
    })


# ── Finance/HR: Claim Detail ──────────────────────────────────────────────────
@admin_required
def expense_detail(request, pk):
    claim = get_object_or_404(
        ExpenseClaim.objects.select_related(
            'employee', 'employee__department', 'employee__designation',
            'manager_reviewed_by', 'finance_reviewed_by', 'reimbursed_by', 'rejected_by',
        ),
        pk=pk
    )
    timeline = claim.comments.select_related('by_employee').all()

    return render(request, 'expenses/detail.html', {
        'claim': claim,
        'timeline': timeline,
    })


# ── Finance: Approve (pending_finance → approved) ─────────────────────────────
# ── Finance: Approve (pending_finance → approved) ─────────────────────────────
@admin_required
def finance_approve(request, pk):
    claim = get_object_or_404(ExpenseClaim, pk=pk)
    if request.method == 'POST' and claim.status == 'pending_finance':
        hr_employee = get_hr_employee(request)
        claim.status = 'approved'
        claim.finance_reviewed_by = hr_employee
        claim.finance_reviewed_at = timezone.now()
        claim.save()
        log_action(claim, 'finance_approved', hr_employee, request.POST.get('comment', '').strip())
        notify_employee(
            claim, 'Expense claim approved',
            f'Your {claim.get_category_display()} claim of Rs.{claim.amount} has been approved by Finance.'
        )
        messages.success(request, f'Expense claim approved for {claim.employee.full_name}.')
    return redirect('expense_detail', pk=claim.pk)

# ── Finance: Reject (pending_finance → rejected) ──────────────────────────────
# ── Finance: Reject (pending_finance → rejected) ──────────────────────────────
@admin_required
def finance_reject(request, pk):
    claim = get_object_or_404(ExpenseClaim, pk=pk)
    if request.method == 'POST' and claim.status == 'pending_finance':
        hr_employee = get_hr_employee(request)
        reason = request.POST.get('rejection_reason', '').strip()
        claim.status = 'rejected'
        claim.rejected_by = hr_employee
        claim.rejected_at = timezone.now()
        claim.rejection_reason = reason
        claim.save()
        log_action(claim, 'finance_rejected', hr_employee, reason)
        notify_employee(
            claim, 'Expense claim rejected',
            f'Your {claim.get_category_display()} claim of Rs.{claim.amount} was rejected by Finance.' + (f' Reason: {reason}' if reason else '')
        )
        messages.success(request, f'Expense claim rejected for {claim.employee.full_name}.')
    return redirect('expense_detail', pk=claim.pk)


# ── Finance: Mark Reimbursed (approved → reimbursed) ──────────────────────────
@admin_required
def mark_reimbursed(request, pk):
    claim = get_object_or_404(ExpenseClaim, pk=pk)
    if request.method == 'POST' and claim.status == 'approved':
        txn_ref = request.POST.get('transaction_reference', '').strip()
        if not txn_ref:
            messages.error(request, 'Transaction reference is required to mark a claim as reimbursed.')
            return redirect('expense_detail', pk=claim.pk)

        hr_employee = get_hr_employee(request)
        claim.status = 'reimbursed'
        claim.reimbursed_by = hr_employee
        claim.reimbursed_at = timezone.now()
        claim.transaction_reference = txn_ref
        claim.save()
        log_action(claim, 'reimbursed', hr_employee, f'Transaction Ref: {txn_ref}')
        notify_employee(
            claim, 'Expense reimbursed',
            f'Rs.{claim.amount} has been reimbursed to your account. Ref: {txn_ref}'
        )
        messages.success(request, f'Rs.{claim.amount} reimbursed to {claim.employee.full_name}.')
    return redirect('expense_detail', pk=claim.pk)


# ── Reports: Category-wise monthly report ─────────────────────────────────────
@admin_required
def expense_reports(request):
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    claims = ExpenseClaim.objects.filter(
        expense_date__month=month, expense_date__year=year
    ).exclude(status__in=['cancelled', 'rejected'])

    category_breakup = list(
        claims.values('category')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')
    )
    category_map = dict(ExpenseClaim.CATEGORY_CHOICES)
    for row in category_breakup:
        row['label'] = category_map.get(row['category'], row['category'])

    total_amount = claims.aggregate(t=Sum('amount'))['t'] or 0
    reimbursed_amount = claims.filter(status='reimbursed').aggregate(t=Sum('amount'))['t'] or 0
    pending_amount = claims.filter(
        status__in=['pending_manager', 'pending_finance', 'approved']
    ).aggregate(t=Sum('amount'))['t'] or 0

    department_breakup = list(
        claims.values('employee__department__name')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')
    )

    # Month navigation
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    return render(request, 'expenses/reports.html', {
        'month': month,
        'year': year,
        'month_name': calendar.month_name[month],
        'category_breakup': category_breakup,
        'department_breakup': department_breakup,
        'total_amount': total_amount,
        'reimbursed_amount': reimbursed_amount,
        'pending_amount': pending_amount,
        'total_claims': claims.count(),
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    })