from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from leave.models import LeaveRequest
from materials.models import MaterialRequest
from vehicles.models import VehicleBooking


def is_admin(user):
    return user.is_authenticated and (user.is_superuser or getattr(user.profile, 'is_admin', False))


@login_required
@user_passes_test(is_admin)
def approval_center(request):
    pending_leaves = LeaveRequest.objects.filter(status='pending').select_related('user').order_by('-created_at')
    pending_materials = MaterialRequest.objects.filter(status='pending').select_related('user').prefetch_related('lines__material').order_by('-created_at')
    pending_bookings = VehicleBooking.objects.filter(status='pending').select_related('user', 'vehicle', 'project').order_by('-created_at')

    context = {
        'pending_leaves': pending_leaves,
        'pending_materials': pending_materials,
        'pending_bookings': pending_bookings,
        'leave_count': pending_leaves.count(),
        'materials_count': pending_materials.count(),
        'bookings_count': pending_bookings.count(),
        'total_count': pending_leaves.count() + pending_materials.count() + pending_bookings.count(),
    }
    return render(request, 'approvals/center.html', context)