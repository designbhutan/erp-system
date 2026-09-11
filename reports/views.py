import json
from datetime import date
from calendar import month_abbr
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from leave.models import LeaveRequest
from materials.models import MaterialRequest
from vehicles.models import VehicleBooking
from procurement.models import PurchaseOrder


def get_last_6_months():
    today = date.today()
    months = []
    for i in range(5, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        months.append((y, m))
    return months


@login_required
def company_reports(request):
    months = get_last_6_months()
    month_labels = [f"{month_abbr[m]}{str(y)[2:]}" for y, m in months]

    leave_data = []
    for y, m in months:
        total = LeaveRequest.objects.filter(
            status='approved',
            start_date__year=y,
            start_date__month=m,
        ).aggregate(s=Sum('days_requested'))['s'] or 0
        leave_data.append(total)

    mr_status = {
        'pending': MaterialRequest.objects.filter(status='pending').count(),
        'approved': MaterialRequest.objects.filter(status='approved').count(),
        'rejected': MaterialRequest.objects.filter(status='rejected').count(),
        'cancelled': MaterialRequest.objects.filter(status='cancelled').count(),
    }

    booking_data = []
    for y, m in months:
        bookings = VehicleBooking.objects.filter(
            status__in=['approved', 'completed'],
            start_datetime__year=y,
            start_datetime__month=m,
        )
        total_hours = sum(b.duration_hours for b in bookings)
        booking_data.append(round(total_hours, 1))

    suppliers_agg = {}
    for po in PurchaseOrder.objects.select_related('supplier').exclude(status='cancelled'):
        name = po.supplier.name
        suppliers_agg[name] = suppliers_agg.get(name, 0) + float(po.total_amount)
    top_suppliers = sorted(suppliers_agg.items(), key=lambda x: x[1], reverse=True)[:5]
    supplier_labels = [s[0] for s in top_suppliers]
    supplier_values = [s[1] for s in top_suppliers]

    summary = {
        'total_leave_days': LeaveRequest.objects.filter(status='approved').aggregate(s=Sum('days_requested'))['s'] or 0,
        'total_material_requests': MaterialRequest.objects.count(),
        'total_bookings': VehicleBooking.objects.count(),
        'total_pos': PurchaseOrder.objects.count(),
        'total_po_value': sum(float(po.total_amount) for po in PurchaseOrder.objects.exclude(status='cancelled')),
    }

    context = {
        'month_labels': json.dumps(month_labels),
        'leave_data': json.dumps(leave_data),
        'booking_data': json.dumps(booking_data),
        'mr_status': json.dumps(mr_status),
        'supplier_labels': json.dumps(supplier_labels),
        'supplier_values': json.dumps(supplier_values),
        'summary': summary,
    }
    return render(request, 'reports/company.html', context)


@login_required
def my_reports(request):
    user = request.user

    my_leaves = LeaveRequest.objects.filter(user=user)
    my_leave_stats = {
        'approved': my_leaves.filter(status='approved').aggregate(s=Sum('days_requested'))['s'] or 0,
        'pending': my_leaves.filter(status='pending').aggregate(s=Sum('days_requested'))['s'] or 0,
        'rejected_count': my_leaves.filter(status='rejected').count(),
    }

    my_mrs = MaterialRequest.objects.filter(user=user)
    my_mr_stats = {
        'total': my_mrs.count(),
        'approved': my_mrs.filter(status='approved').count(),
        'pending': my_mrs.filter(status='pending').count(),
        'rejected': my_mrs.filter(status='rejected').count(),
    }

    my_bookings = VehicleBooking.objects.filter(user=user)
    my_booking_stats = {
        'total': my_bookings.count(),
        'approved': my_bookings.filter(status='approved').count(),
        'pending': my_bookings.filter(status='pending').count(),
        'completed': my_bookings.filter(status='completed').count(),
    }

    recent_leaves = my_leaves.order_by('-created_at')[:5]
    recent_mrs = my_mrs.order_by('-created_at')[:5]
    recent_bookings = my_bookings.order_by('-created_at')[:5]

    context = {
        'my_leave_stats': my_leave_stats,
        'my_mr_stats': my_mr_stats,
        'my_booking_stats': my_booking_stats,
        'recent_leaves': recent_leaves,
        'recent_mrs': recent_mrs,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'reports/my.html', context)