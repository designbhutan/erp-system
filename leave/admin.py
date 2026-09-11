from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import LeaveRequest, Holiday


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    ordering = ('date',)


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'days_requested', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'reason')