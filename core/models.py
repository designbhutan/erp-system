from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Employee(models.Model):
    employee_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=150)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    position = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"

    class Meta:
        ordering = ['employee_id']


class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('sedan', 'Sedan'),
        ('pickup', 'Pickup Truck'),
        ('van', 'Van'),
        ('truck', 'Heavy Truck'),
        ('suv', 'SUV'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
    ]

    plate_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    make_model = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    current_location = models.CharField(max_length=200, blank=True)
    last_maintenance = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plate_number} ({self.get_vehicle_type_display()})"

    class Meta:
        ordering = ['plate_number']


class VehicleBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='bookings')
    project_name = models.CharField(max_length=200)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    purpose = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.project_name}"

    class Meta:
        ordering = ['-start_datetime']


class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_projects')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    progress_percent = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['-created_at']


class Material(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, unique=True)
    unit = models.CharField(max_length=20, default='pcs')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_level = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['name']


class Supplier(models.Model):
    name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']