from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import SignUpForm, LoginForm, ProfileForm, CustomPasswordChangeForm
from .models import Profile
from core.models import Employee, Department


def is_admin(user):
    return user.is_authenticated and (user.is_superuser or getattr(user.profile, 'is_admin', False))


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name or user.username}!")
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next') or 'dashboard'
            return redirect(next_url)
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# ========== PROFILE ==========

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')


@login_required
def profile_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('profile_view')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def password_change(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect('profile_view')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'accounts/password_change.html', {'form': form})


# ========== EMPLOYEE MANAGEMENT ==========

@login_required
@user_passes_test(is_admin)
def employee_list(request):
    employees = Employee.objects.select_related('department').all()
    return render(request, 'accounts/employee_list.html', {'employees': employees})


@login_required
@user_passes_test(is_admin)
def employee_create(request):
    if request.method == 'POST':
        data = request.POST
        try:
            emp = Employee.objects.create(
                employee_id=data['employee_id'],
                full_name=data['full_name'],
                department_id=data.get('department') or None,
                position=data['position'],
                email=data.get('email', ''),
                phone=data.get('phone', ''),
                hire_date=data['hire_date'],
                is_active=data.get('is_active') == 'on',
            )
            messages.success(request, f"Employee {emp.employee_id} added.")
            return redirect('employees_list')
        except Exception as e:
            messages.error(request, f"Error: {e}")
    departments = Department.objects.all()
    return render(request, 'accounts/employee_form.html', {'departments': departments, 'action': 'Create'})


@login_required
@user_passes_test(is_admin)
def employee_edit(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        data = request.POST
        try:
            emp.employee_id = data['employee_id']
            emp.full_name = data['full_name']
            emp.department_id = data.get('department') or None
            emp.position = data['position']
            emp.email = data.get('email', '')
            emp.phone = data.get('phone', '')
            emp.hire_date = data['hire_date']
            emp.is_active = data.get('is_active') == 'on'
            emp.save()
            messages.success(request, f"Employee {emp.employee_id} updated.")
            return redirect('employees_list')
        except Exception as e:
            messages.error(request, f"Error: {e}")
    departments = Department.objects.all()
    return render(request, 'accounts/employee_form.html', {'departments': departments, 'emp': emp, 'action': 'Edit'})


@login_required
@user_passes_test(is_admin)
def employee_delete(request, pk):
    emp = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        emp.delete()
        messages.success(request, "Employee deleted.")
        return redirect('employees_list')
    return render(request, 'accounts/employee_confirm_delete.html', {'emp': emp})


@login_required
@user_passes_test(is_admin)
def users_list(request):
    users = User.objects.select_related('profile').order_by('username')
    return render(request, 'accounts/users_list.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def user_toggle_role(request, pk):
    if request.user.pk == pk:
        messages.error(request, "You cannot change your own role.")
        return redirect('users_list')
    u = get_object_or_404(User, pk=pk)
    profile, _ = Profile.objects.get_or_create(user=u)
    if profile.role == 'admin' and not u.is_superuser:
        profile.role = 'employee'
        u.is_staff = False
        messages.info(request, f"{u.username} demoted to Employee.")
    else:
        profile.role = 'admin'
        u.is_staff = True
        messages.success(request, f"{u.username} promoted to Admin.")
    profile.save()
    u.save()
    return redirect('users_list')