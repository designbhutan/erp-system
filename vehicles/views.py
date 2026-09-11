from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from core.models import Vehicle
from .models import VehicleBooking
from .forms import VehicleBookingForm


def is_admin(user):
    return user.is_authenticated and (user.is_superuser or getattr(user.profile, 'is_admin', False))


@login_required
def vehicle_list(request):
    vehicles = Vehicle.objects.all().order_by('plate_number')
    return render(request, 'vehicles/vehicle_list.html', {'vehicles': vehicles})


@login_required
def my_bookings(request):
    bookings = VehicleBooking.objects.filter(user=request.user).select_related('vehicle', 'project')
    return render(request, 'vehicles/my_bookings.html', {'bookings': bookings})


@login_required
def booking_create(request):
    if request.method == 'POST':
        form = VehicleBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            messages.success(request, f"Booking VB#{booking.pk} submitted for approval.")
            return redirect('vehicles_my_bookings')
    else:
        form = VehicleBookingForm()

    return render(request, 'vehicles/booking_form.html', {'form': form})


@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(VehicleBooking, pk=pk, user=request.user)
    if booking.status in ('pending', 'approved'):
        booking.status = 'cancelled'
        booking.save()
        if booking.vehicle.status == 'in_use':
            booking.vehicle.status = 'available'
            booking.vehicle.save()
        messages.info(request, f"Booking VB#{booking.pk} cancelled.")
    else:
        messages.error(request, "You cannot cancel this booking.")
    return redirect('vehicles_my_bookings')


@login_required
@user_passes_test(is_admin)
def pending_bookings(request):
    pending = VehicleBooking.objects.filter(status='pending').select_related('vehicle', 'user', 'project')
    return render(request, 'vehicles/pending.html', {'pending': pending})


@login_required
@user_passes_test(is_admin)
def review_booking(request, pk, action):
    booking = get_object_or_404(VehicleBooking, pk=pk)

    if booking.status != 'pending':
        messages.warning(request, "This booking has already been reviewed.")
        return redirect('vehicles_pending')

    if action == 'approve':
        # Re-check conflict at approval time
        overlapping = VehicleBooking.objects.filter(
            vehicle=booking.vehicle,
            status='approved',
            start_datetime__lt=booking.end_datetime,
            end_datetime__gt=booking.start_datetime,
        ).exclude(pk=booking.pk)

        if overlapping.exists():
            messages.error(request, f"Cannot approve — {booking.vehicle.plate_number} is already booked for that time.")
            return redirect('vehicles_pending')

        booking.status = 'approved'
        booking.vehicle.status = 'in_use'
        booking.vehicle.save()
        messages.success(request, f"VB#{booking.pk} approved. {booking.vehicle.plate_number} is now in use.")

    elif action == 'reject':
        booking.status = 'rejected'
        messages.warning(request, f"VB#{booking.pk} rejected.")

    booking.reviewed_by = request.user
    booking.reviewed_at = timezone.now()
    booking.save()

    return redirect('vehicles_pending')


@login_required
@user_passes_test(is_admin)
def complete_booking(request, pk):
    booking = get_object_or_404(VehicleBooking, pk=pk)
    if booking.status == 'approved':
        booking.status = 'completed'
        booking.save()
        booking.vehicle.status = 'available'
        booking.vehicle.save()
        messages.success(request, f"VB#{booking.pk} marked as completed. {booking.vehicle.plate_number} is now available.")
    return redirect('vehicles_pending')