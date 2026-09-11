from django.contrib import admin
from .models import Department, Employee, Vehicle, VehicleBooking, Project, Material, Supplier


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'department', 'position', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('employee_id', 'full_name', 'position')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'vehicle_type', 'make_model', 'status', 'current_location')
    list_filter = ('vehicle_type', 'status')
    search_fields = ('plate_number', 'make_model')


@admin.register(VehicleBooking)
class VehicleBookingAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'project_name', 'start_datetime', 'end_datetime', 'status')
    list_filter = ('status', 'vehicle')
    search_fields = ('project_name',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'manager', 'start_date', 'end_date', 'budget', 'status', 'progress_percent')
    list_filter = ('status',)
    search_fields = ('code', 'name')


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'unit', 'unit_price', 'stock_quantity', 'reorder_level')
    search_fields = ('code', 'name')


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone')
    search_fields = ('name',)