from django import forms
from core.models import Vehicle, Project
from .models import VehicleBooking


class VehicleBookingForm(forms.ModelForm):
    class Meta:
        model = VehicleBooking
        fields = ['vehicle', 'project', 'project_name', 'start_datetime', 'end_datetime', 'destination', 'purpose']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'project_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., PRJ-001 Site A (if no project selected above)'}),
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Where are you going?'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Purpose of the trip'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle'].queryset = Vehicle.objects.exclude(status='retired').order_by('plate_number')
        self.fields['vehicle'].empty_label = "— Select a vehicle —"
        self.fields['project'].queryset = Project.objects.all().order_by('code')
        self.fields['project'].required = False
        self.fields['project'].empty_label = "— No project —"
        self.fields['project_name'].required = False

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_datetime')
        end = cleaned.get('end_datetime')
        vehicle = cleaned.get('vehicle')

        if start and end and start >= end:
            raise forms.ValidationError("End time must be after start time.")

        if vehicle and start and end:
            overlapping = VehicleBooking.objects.filter(
                vehicle=vehicle,
                status__in=['pending', 'approved'],
                start_datetime__lt=end,
                end_datetime__gt=start,
            )
            if self.instance.pk:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            if overlapping.exists():
                conflict = overlapping.first()
                raise forms.ValidationError(
                    f"Conflict: {vehicle.plate_number} is already booked "
                    f"from {conflict.start_datetime:%d %b %Y %H:%M} to {conflict.end_datetime:%d %b %Y %H:%M}."
                )

        return cleaned