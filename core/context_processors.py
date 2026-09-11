def notification_badge(request):
    """Adds pending_count to every template context."""
    if not request.user.is_authenticated:
        return {'pending_count': 0}

    try:
        from leave.models import LeaveRequest
        from materials.models import MaterialRequest
        from vehicles.models import VehicleBooking
        from procurement.models import PurchaseOrder

        is_admin = request.user.is_superuser or getattr(request.user.profile, 'is_admin', False)

        if is_admin:
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
        return {'pending_count': count}
    except Exception:
        return {'pending_count': 0}