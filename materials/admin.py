from django.contrib import admin
from .models import MaterialRequest, MaterialRequestLine


class MaterialRequestLineInline(admin.TabularInline):
    model = MaterialRequestLine
    extra = 0


@admin.register(MaterialRequest)
class MaterialRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project_name', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'project_name')
    inlines = [MaterialRequestLineInline]