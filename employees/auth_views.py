from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.text import slugify
import random
import string
from .models import Employee, Department, Designation


# ── Root Redirect ─────────────────────────────────────────────────────────────
# def root_redirect(request):
#     """
#     / pe aane par:
#     - Not logged in → employee login
#     - Super admin (is_superuser) → admin dashboard
#     - Staff (HR) → admin dashboard
#     - Employee → portal
#     """
#     if not request.user.is_authenticated:
#         return redirect('employee_login')

#     if request.user.is_superuser or request.user.is_staff:
#         return redirect('dashboard')

#     # Check if employee profile exists
#     try:
#         Employee.objects.get(user=request.user)
#         return redirect('portal_dashboard')
#     except Employee.DoesNotExist:
#         return redirect('employee_login')

# def root_redirect(request):
#     if not request.user.is_authenticated:
#         return redirect('employee_login')

#     # Super admin / Staff → Admin Dashboard
#     if request.user.is_superuser or request.user.is_staff:
#         return redirect('dashboard')

#     # Employee check
#     try:
#         emp = Employee.objects.get(user=request.user)
#         if emp.status in ['active', 'on_leave']:
#             return redirect('portal_dashboard')
#         else:
#             from django.contrib.auth import logout
#             logout(request)
#             return redirect('employee_login')
#     except Employee.DoesNotExist:
#         return redirect('employee_login')

def root_redirect(request):
    if not request.user.is_authenticated:
        return redirect('employee_login')
    if request.user.is_superuser or request.user.is_staff:
    
        return redirect('dashboard')
    try:
        emp = Employee.objects.get(user=request.user)
        if emp.status in ['active', 'on_leave']:
            return redirect('portal_dashboard')
        else:
            from django.contrib.auth import logout
            logout(request)
            return redirect('employee_login')
    except Employee.DoesNotExist:
        return redirect('employee_login')


# ── HR Admin Login ─────────────────────────────────────────────────────────────
def admin_login(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user     = authenticate(request, username=username, password=password)

        if user and (user.is_staff or user.is_superuser):
            login(request, user)
            return redirect(request.POST.get('next', '/dashboard/'))
        elif user and not user.is_staff:
            messages.error(request, 'Access denied. Use Employee Login instead.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'auth/admin_login.html', {
        'next': request.GET.get('next', '/dashboard/')
    })


def admin_logout(request):
    logout(request)
    return redirect('admin_login')


# ── Employee Login ─────────────────────────────────────────────────────────────
def employee_login(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('dashboard')
        try:
            Employee.objects.get(user=request.user)
            return redirect('portal_dashboard')
        except Employee.DoesNotExist:
            pass

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user     = authenticate(request, username=username, password=password)

        if user:
            if user.is_superuser or user.is_staff:
                messages.error(request, 'Please use Admin Login for HR access.')
                return redirect('admin_login')
            try:
                employee = Employee.objects.get(user=user)
                if employee.status == 'terminated':
                    messages.error(request, 'Your account has been terminated. Contact HR.')
                elif employee.status == 'inactive':
                    messages.error(request, 'Your account is inactive. Contact HR.')
                else:
                    login(request, user)
                    return redirect('portal_dashboard')
            except Employee.DoesNotExist:
                messages.error(request, 'No employee profile found. Contact HR.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'auth/employee_login.html')


def employee_logout(request):
    logout(request)
    return redirect('employee_login')


# ── Generate Username & Password ──────────────────────────────────────────────
def generate_username(first_name, last_name, employee_id):
    """
    Generate: firstname.lastname or firstname.emp_id if conflict
    Example: dhananjay.gupta or dhananjay.dj001
    """
    base = f"{first_name.lower().strip()}.{last_name.lower().strip()}"
    base = base.replace(' ', '').replace('-', '')

    if not User.objects.filter(username=base).exists():
        return base

    # Try with employee_id
    alt = f"{first_name.lower().strip()}.{employee_id.lower()}"
    if not User.objects.filter(username=alt).exists():
        return alt

    # Add random suffix
    suffix = ''.join(random.choices(string.digits, k=3))
    return f"{base}{suffix}"


def generate_password(first_name, employee_id):
    """
    Format: FirstName@EmpID123
    Example: Dhananjay@DJ001
    """
    return f"{first_name.capitalize()}@{employee_id}"


def create_employee_user(employee):
    """
    Create Django User for an Employee and link it.
    Returns (user, username, password)
    """
    if employee.user:
        return None, None, None  # Already has user

    username = generate_username(
        employee.first_name,
        employee.last_name,
        employee.employee_id
    )
    password = generate_password(employee.first_name, employee.employee_id)

    user = User.objects.create_user(
        username=username,
        password=password,
        first_name=employee.first_name,
        last_name=employee.last_name,
        email=employee.email,
        is_staff=False,
        is_superuser=False,
    )

    employee.user = user
    employee.save(update_fields=['user'])

    return user, username, password