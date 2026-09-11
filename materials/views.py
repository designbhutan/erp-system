from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.forms import formset_factory
from core.models import Material
from .models import MaterialRequest, MaterialRequestLine
from .forms import MaterialRequestForm, MaterialRequestLineForm


def is_admin(user):
    return user.is_authenticated and (user.is_superuser or getattr(user.profile, 'is_admin', False))


@login_required
def material_list(request):
    materials = Material.objects.all().order_by('name')
    low_stock = [m for m in materials if m.stock_quantity <= m.reorder_level]
    context = {
        'materials': materials,
        'low_stock_count': len(low_stock),
    }
    return render(request, 'materials/material_list.html', context)


@login_required
def my_requests(request):
    requests = MaterialRequest.objects.filter(user=request.user).prefetch_related('lines__material')
    return render(request, 'materials/my_requests.html', {'requests': requests})


@login_required
def request_create(request):
    LineFormSet = formset_factory(MaterialRequestLineForm, extra=3, min_num=1, validate_min=True)

    if request.method == 'POST':
        main_form = MaterialRequestForm(request.POST)
        line_formset = LineFormSet(request.POST)

        if main_form.is_valid() and line_formset.is_valid():
            mr = main_form.save(commit=False)
            mr.user = request.user
            mr.save()

            has_line = False
            for line_form in line_formset:
                if line_form.cleaned_data and line_form.cleaned_data.get('material'):
                    line = line_form.save(commit=False)
                    line.request = mr
                    line.save()
                    has_line = True

            if not has_line:
                mr.delete()
                messages.error(request, "You must add at least one material.")
                return render(request, 'materials/request_form.html', {
                    'main_form': main_form, 'line_formset': line_formset,
                })

            messages.success(request, f"Request MR#{mr.pk} submitted for approval.")
            return redirect('materials_my_requests')
    else:
        main_form = MaterialRequestForm()
        line_formset = LineFormSet()

    return render(request, 'materials/request_form.html', {
        'main_form': main_form,
        'line_formset': line_formset,
    })


@login_required
def request_cancel(request, pk):
    mr = get_object_or_404(MaterialRequest, pk=pk, user=request.user)
    if mr.status == 'pending':
        mr.status = 'cancelled'
        mr.save()
        messages.info(request, f"Request MR#{mr.pk} cancelled.")
    else:
        messages.error(request, "You can only cancel pending requests.")
    return redirect('materials_my_requests')


@login_required
@user_passes_test(is_admin)
def pending_requests(request):
    pending = MaterialRequest.objects.filter(status='pending').prefetch_related('lines__material', 'user')
    return render(request, 'materials/pending.html', {'pending': pending})


@login_required
@user_passes_test(is_admin)
def review_request(request, pk, action):
    mr = get_object_or_404(MaterialRequest, pk=pk)

    if mr.status != 'pending':
        messages.warning(request, "This request has already been reviewed.")
        return redirect('materials_pending')

    if action == 'approve':
        # Warn if stock insufficient, but allow (option B)
        insufficient = []
        for line in mr.lines.all():
            if line.material.stock_quantity < line.quantity:
                insufficient.append(f"{line.material.name} (need {line.quantity}, have {line.material.stock_quantity})")

        # Deduct stock (allow negative)
        for line in mr.lines.all():
            line.material.stock_quantity -= line.quantity
            line.material.save()

        mr.status = 'approved'
        mr.save()

        if insufficient:
            messages.warning(request, f"MR#{mr.pk} approved. Note: stock went negative for: {', '.join(insufficient)}")
        else:
            messages.success(request, f"MR#{mr.pk} approved. Stock deducted.")

    elif action == 'reject':
        mr.status = 'rejected'
        mr.save()
        messages.warning(request, f"MR#{mr.pk} rejected.")

    mr.reviewed_by = request.user
    mr.reviewed_at = timezone.now()
    mr.save()

    return redirect('materials_pending')