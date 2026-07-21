from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Employee


# ── HR Admin Login ────────────────────────────────────────────────────────────
def admin_login(request):
    # Already logged in HR admin
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user     = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect(request.POST.get('next', '/dashboard/'))
        elif user is not None and not user.is_staff:
            messages.error(request, 'You are not authorized as HR Admin. Use Employee Login instead.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'auth/admin_login.html', {
        'next': request.GET.get('next', '/dashboard/')
    })


def admin_logout(request):
    logout(request)
    return redirect('admin_login')


# ── Employee Login ────────────────────────────────────────────────────────────
def employee_login(request):
    # Already logged in employee
    if request.user.is_authenticated:
        try:
            Employee.objects.get(user=request.user)
            return redirect('portal_dashboard')
        except Employee.DoesNotExist:
            pass

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user     = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if employee profile exists
            try:
                employee = Employee.objects.get(user=user)
                if employee.status == 'terminated':
                    messages.error(request, 'Your account has been terminated. Contact HR.')
                elif employee.status == 'inactive':
                    messages.error(request, 'Your account is inactive. Contact HR.')
                else:
                    login(request, user)
                    messages.success(request, f'Welcome, {employee.first_name}!')
                    return redirect('portal_dashboard')
            except Employee.DoesNotExist:
                messages.error(request, 'No employee profile linked. Contact HR department.')
        else:
            messages.error(request, 'Invalid Employee ID or Password.')

    return render(request, 'auth/employee_login.html', {
        'next': request.GET.get('next', '/portal/')
    })


def employee_logout(request):
    logout(request)
    return redirect('employee_login')