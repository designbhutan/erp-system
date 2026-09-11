from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.forms import formset_factory
from .models import PurchaseOrder, PurchaseOrderLine
from .forms import PurchaseOrderForm, PurchaseOrderLineForm


def is_admin(user):
    return user.is_authenticated and (user.is_superuser or getattr(user.profile, 'is_admin', False))


@login_required
@user_passes_test(is_admin)
def po_list(request):
    pos = PurchaseOrder.objects.all().select_related('supplier', 'project')
    return render(request, 'procurement/po_list.html', {'pos': pos})


@login_required
@user_passes_test(is_admin)
def po_create(request):
    LineFormSet = formset_factory(PurchaseOrderLineForm, extra=3, min_num=1, validate_min=True)

    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        formset = LineFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            po = form.save(commit=False)
            po.created_by = request.user
            po.save()

            has_line = False
            for line_form in formset:
                if line_form.cleaned_data and line_form.cleaned_data.get('material'):
                    line = line_form.save(commit=False)
                    line.purchase_order = po
                    line.save()
                    has_line = True

            if not has_line:
                po.delete()
                messages.error(request, "You must add at least one line item.")
                return render(request, 'procurement/po_form.html', {'form': form, 'formset': formset})

            messages.success(request, f"Purchase Order {po.po_number} created as Draft.")
            return redirect('po_detail', pk=po.pk)
    else:
        form = PurchaseOrderForm()
        formset = LineFormSet()

    return render(request, 'procurement/po_form.html', {'form': form, 'formset': formset})


@login_required
@user_passes_test(is_admin)
def po_detail(request, pk):
    po = get_object_or_404(PurchaseOrder, pk=pk)
    return render(request, 'procurement/po_detail.html', {'po': po})


@login_required
@user_passes_test(is_admin)
def po_action(request, pk, action):
    po = get_object_or_404(PurchaseOrder, pk=pk)

    if action == 'submit' and po.status == 'draft':
        po.status = 'submitted'
        po.save()
        messages.success(request, f"{po.po_number} submitted for approval.")

    elif action == 'approve' and po.status == 'submitted':
        po.status = 'approved'
        po.approved_by = request.user
        po.approved_at = timezone.now()
        po.save()
        messages.success(request, f"{po.po_number} approved.")

    elif action == 'receive' and po.status == 'approved':
        # Add each line's quantity to the material stock
        for line in po.lines.all():
            line.material.stock_quantity += line.quantity
            line.material.save()
        po.status = 'received'
        po.received_at = timezone.now()
        po.save()
        messages.success(request, f"{po.po_number} received. Stock updated.")

    elif action == 'cancel' and po.status in ('draft', 'submitted'):
        po.status = 'cancelled'
        po.save()
        messages.warning(request, f"{po.po_number} cancelled.")

    else:
        messages.error(request, f"Cannot perform '{action}' on a {po.get_status_display()} PO.")

    return redirect('po_detail', pk=po.pk)