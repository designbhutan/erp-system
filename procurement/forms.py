from django import forms
from django.utils import timezone
from core.models import Supplier, Project, Material
from .models import PurchaseOrder, PurchaseOrderLine


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['po_number', 'supplier', 'project', 'order_date', 'expected_delivery', 'notes']
        widgets = {
            'po_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., PO-2026-001'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'order_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expected_delivery': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.all().order_by('name')
        self.fields['project'].queryset = Project.objects.all().order_by('code')
        self.fields['project'].required = False
        self.fields['project'].empty_label = "— No project —"
        self.fields['expected_delivery'].required = False
        if not self.instance.pk:
            self.fields['order_date'].initial = timezone.now().date()


class PurchaseOrderLineForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderLine
        fields = ['material', 'quantity', 'unit_price']
        widgets = {
            'material': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['material'].queryset = Material.objects.all().order_by('name')