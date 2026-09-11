from django.contrib import admin
from .models import VehicleBooking


@admin.register(VehicleBooking)
class VehicleBookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle', 'user', 'start_datetime', 'end_datetime', 'status', 'created_at')
    list_filter = ('status', 'vehicle')
    search_fields = ('user__username', 'project_name', 'destination')