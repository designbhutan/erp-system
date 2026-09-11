from django.db import models
from django.contrib.auth.models import User


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]

    po_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey('core.Supplier', on_delete=models.CASCADE, related_name='purchase_orders')
    project = models.ForeignKey('core.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='purchase_orders')
    order_date = models.DateField()
    expected_delivery = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_pos')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_pos')
    approved_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.po_number

    class Meta:
        ordering = ['-created_at']

    @property
    def total_amount(self):
        return sum(line.line_total for line in self.lines.all())


class PurchaseOrderLine(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='lines')
    material = models.ForeignKey('core.Material', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.material.name} x {self.quantity}"

    @property
    def line_total(self):
        return self.quantity * self.unit_price