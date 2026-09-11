from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
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
    status = request.GET.get('status', '')
    qs = Project.objects.select_related('manager').all()
    if status:
        qs = qs.filter(status=status)
    context = {
        'projects': qs,
        'statuses': Project.STATUS_CHOICES,
        'current_status': status,
    }
    return render(request, 'core/project_list.html', context)


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


# ========== NOTIFICATIONS ==========

@login_required
def notifications(request):
    from leave.models import LeaveRequest
    from materials.models import MaterialRequest
    from vehicles.models import VehicleBooking
    from procurement.models import PurchaseOrder

    context = {}

    if is_admin(request.user):
        context['pending_leaves'] = LeaveRequest.objects.filter(status='pending').select_related('user')[:20]
        context['pending_materials'] = MaterialRequest.objects.filter(status='pending').select_related('user')[:20]
        context['pending_bookings'] = VehicleBooking.objects.filter(status='pending').select_related('user', 'vehicle')[:20]
        context['pending_pos'] = PurchaseOrder.objects.filter(status='submitted')[:20]
        context['leave_count'] = LeaveRequest.objects.filter(status='pending').count()
        context['materials_count'] = MaterialRequest.objects.filter(status='pending').count()
        context['bookings_count'] = VehicleBooking.objects.filter(status='pending').count()
        context['pos_count'] = PurchaseOrder.objects.filter(status='submitted').count()
        context['total_count'] = (
            context['leave_count'] + context['materials_count'] +
            context['bookings_count'] + context['pos_count']
        )
    else:
        context['my_leaves'] = LeaveRequest.objects.filter(user=request.user).order_by('-created_at')[:10]
        context['my_materials'] = MaterialRequest.objects.filter(user=request.user).order_by('-created_at')[:10]
        context['my_bookings'] = VehicleBooking.objects.filter(user=request.user).order_by('-created_at')[:10]

    return render(request, 'core/notifications.html', context)


@login_required
def notification_count(request):
    """Returns count for badge — used as context processor helper."""
    from leave.models import LeaveRequest
    from materials.models import MaterialRequest
    from vehicles.models import VehicleBooking
    from procurement.models import PurchaseOrder

    if is_admin(request.user):
        count = (
            LeaveRequest.objects.filter(status='pending').count() +
            MaterialRequest.objects.filter(status='pending').count() +
            VehicleBooking.objects.filter(status='pending').count() +
            PurchaseOrder.objects.filter(status='submitted').count()
        )
    else:
        count = (
            LeaveRequest.objects.filter(user=request.user, status='pending').count() +
            MaterialRequest.objects.filter(user=request.user, status='pending').count() +
            VehicleBooking.objects.filter(user=request.user, status='pending').count()
        )
    return count


# ========== SEARCH ==========

@login_required
def search(request):
    q = request.GET.get('q', '').strip()
    context = {'q': q, 'results_count': 0}

    if q and len(q) >= 2:
        projects = Project.objects.filter(
            Q(name__icontains=q) | Q(code__icontains=q)
        )[:20]
        materials = Material.objects.filter(
            Q(name__icontains=q) | Q(code__icontains=q)
        )[:20]
        vehicles = Vehicle.objects.filter(
            Q(plate_number__icontains=q) | Q(make_model__icontains=q)
        )[:20]
        employees = Employee.objects.filter(
            Q(full_name__icontains=q) | Q(employee_id__icontains=q) | Q(position__icontains=q)
        )[:20]
        suppliers = Supplier.objects.filter(
            Q(name__icontains=q) | Q(contact_person__icontains=q)
        )[:20]

        context.update({
            'projects': projects,
            'materials': materials,
            'vehicles': vehicles,
            'employees': employees,
            'suppliers': suppliers,
            'results_count': (
                projects.count() + materials.count() + vehicles.count() +
                employees.count() + suppliers.count()
            ),
        })

    return render(request, 'core/search.html', context)