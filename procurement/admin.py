from django.contrib import admin
from .models import PurchaseOrder, PurchaseOrderLine


class PurchaseOrderLineInline(admin.TabularInline):
    model = PurchaseOrderLine
    extra = 0


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'supplier', 'project', 'order_date', 'status', 'total_amount')
    list_filter = ('status', 'supplier')
    search_fields = ('po_number', 'supplier__name')
    inlines = [PurchaseOrderLineInline]