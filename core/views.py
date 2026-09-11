from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import (
    Department, Employee, Vehicle, VehicleBooking,
    Project, Material, Supplier
)


def is_admin(user):
    return user.is_authenticated and (user.is_superuser or getattr(user.profile, 'is_admin', False))


@login_required
def dashboard(request):
    context = {
        'department_count': Department.objects.count(),
        'employee_count': Employee.objects.filter(is_active=True).count(),
        'vehicle_count': Vehicle.objects.count(),
        'vehicle_available': Vehicle.objects.filter(status='available').count(),
        'booking_count': VehicleBooking.objects.count(),
        'project_count': Project.objects.count(),
        'project_active': Project.objects.filter(status='active').count(),
        'material_count': Material.objects.count(),
        'supplier_count': Supplier.objects.count(),
        'recent_projects': Project.objects.all()[:5],
        'recent_bookings': VehicleBooking.objects.all()[:5],
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def project_list(request):
    projects = Project.objects.select_related('manager').all()
    return render(request, 'core/project_list.html', {'projects': projects})


@login_required
@user_passes_test(is_admin)
def project_create(request):
    if request.method == 'POST':
        d = request.POST
        try:
            project = Project.objects.create(
                name=d['name'],
                code=d['code'],
                description=d.get('description', ''),
                manager_id=d.get('manager') or None,
                start_date=d['start_date'],
                end_date=d.get('end_date') or None,
                budget=d.get('budget') or 0,
                status=d.get('status', 'planning'),
                progress_percent=int(d.get('progress_percent') or 0),
            )
            messages.success(request, f"Project {project.code} created.")
            return redirect('project_list')
        except Exception as e:
            messages.error(request, f"Error: {e}")

    context = {
        'managers': Employee.objects.filter(is_active=True),
        'statuses': Project.STATUS_CHOICES,
        'action': 'Create',
    }
    return render(request, 'core/project_form.html', context)


@login_required
@user_passes_test(is_admin)
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        d = request.POST
        try:
            project.name = d['name']
            project.code = d['code']
            project.description = d.get('description', '')
            project.manager_id = d.get('manager') or None
            project.start_date = d['start_date']
            project.end_date = d.get('end_date') or None
            project.budget = d.get('budget') or 0
            project.status = d.get('status', 'planning')
            project.progress_percent = int(d.get('progress_percent') or 0)
            project.save()
            messages.success(request, f"Project {project.code} updated.")
            return redirect('project_list')
        except Exception as e:
            messages.error(request, f"Error: {e}")

    context = {
        'project': project,
        'managers': Employee.objects.filter(is_active=True),
        'statuses': Project.STATUS_CHOICES,
        'action': 'Edit',
    }
    return render(request, 'core/project_form.html', context)


@login_required
@user_passes_test(is_admin)
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        messages.success(request, "Project deleted.")
        return redirect('project_list')
    return render(request, 'core/project_confirm_delete.html', {'project': project})