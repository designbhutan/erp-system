from django.db import models
from django.contrib.auth.models import User
from core.models import Vehicle, Project


class VehicleBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicle_bookings')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='booking_records')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicle_bookings')
    project_name = models.CharField(max_length=200, blank=True, help_text="Free-text if no project selected")
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    destination = models.CharField(max_length=200, blank=True)
    purpose = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_comment = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_vehicle_bookings')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"VB#{self.pk} — {self.vehicle.plate_number} ({self.status})"

    class Meta:
        ordering = ['-created_at']

    @property
    def duration_hours(self):
        delta = self.end_datetime - self.start_datetime
        return round(delta.total_seconds() / 3600, 1)