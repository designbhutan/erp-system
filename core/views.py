from django.shortcuts import render
from .models import (
    Department, Employee, Vehicle, VehicleBooking,
    Project, Material, Supplier, PurchaseOrder
)


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
        'po_count': PurchaseOrder.objects.count(),
        'recent_projects': Project.objects.all()[:5],
        'recent_bookings': VehicleBooking.objects.all()[:5],
    }
    return render(request, 'core/dashboard.html', context)