from django.db import models
from django.contrib.auth.models import User
from datetime import date


class Holiday(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(unique=True)

    def __str__(self):
        return f"{self.name} ({self.date})"

    class Meta:
        ordering = ['date']


class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    days_requested = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_comment = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_leaves')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.start_date} → {self.end_date} ({self.status})"

    class Meta:
        ordering = ['-created_at']


def get_leave_year_bounds(reference_date=None):
    """Returns (start, end) of the leave year containing reference_date.
    Leave year: July 1 → June 30."""
    if reference_date is None:
        reference_date = date.today()
    if reference_date.month >= 7:
        start = date(reference_date.year, 7, 1)
        end = date(reference_date.year + 1, 6, 30)
    else:
        start = date(reference_date.year - 1, 7, 1)
        end = date(reference_date.year, 6, 30)
    return start, end


def calculate_working_days(start_date, end_date):
    """Count days between start and end, excluding Sat/Sun and Holidays."""
    if start_date > end_date:
        return 0
    holiday_dates = set(Holiday.objects.values_list('date', flat=True))
    current = start_date
    count = 0
    while current <= end_date:
        # 5 = Saturday, 6 = Sunday
        if current.weekday() < 5 and current not in holiday_dates:
            count += 1
        current += __import__('datetime').timedelta(days=1)
    return count


def get_user_leave_stats(user):
    """Returns dict with entitlement, used, pending, remaining for current leave year."""
    year_start, year_end = get_leave_year_bounds()

    approved = LeaveRequest.objects.filter(
        user=user, status='approved',
        start_date__gte=year_start, start_date__lte=year_end
    ).aggregate(total=models.Sum('days_requested'))['total'] or 0

    pending = LeaveRequest.objects.filter(
        user=user, status='pending',
        start_date__gte=year_start, start_date__lte=year_end
    ).aggregate(total=models.Sum('days_requested'))['total'] or 0

    entitlement = 21
    return {
        'entitlement': entitlement,
        'used': approved,
        'pending': pending,
        'remaining': entitlement - approved,
        'year_start': year_start,
        'year_end': year_end,
    }