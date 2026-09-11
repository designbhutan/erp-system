from django.db import models
from django.contrib.auth.models import User


class MaterialRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='material_requests')
    project_name = models.CharField(max_length=200, blank=True)
    purpose = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_comment = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_material_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"MR#{self.pk} — {self.user.username} ({self.status})"

    class Meta:
        ordering = ['-created_at']

    @property
    def total_items(self):
        return self.lines.count()


class MaterialRequestLine(models.Model):
    request = models.ForeignKey(MaterialRequest, on_delete=models.CASCADE, related_name='lines')
    material = models.ForeignKey('core.Material', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.material.name} x {self.quantity}"

    @property
    def available_stock(self):
        return self.material.stock_quantity

    @property
    def is_sufficient(self):
        return self.material.stock_quantity >= self.quantity