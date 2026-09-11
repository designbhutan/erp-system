from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import LeaveRequest, calculate_working_days, get_user_leave_stats
from .forms import LeaveRequestForm, ReviewForm


def is_admin(user):
    return user.is_authenticated and (user.is_superuser or getattr(user.profile, 'is_admin', False))


@login_required
def leave_home(request):
    stats = get_user_leave_stats(request.user)
    my_requests = LeaveRequest.objects.filter(user=request.user)
    context = {
        'stats': stats,
        'my_requests': my_requests,
    }
    return render(request, 'leave/leave_home.html', context)


@login_required
def leave_apply(request):
    stats = get_user_leave_stats(request.user)

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.user = request.user
            leave.days_requested = calculate_working_days(leave.start_date, leave.end_date)

            if leave.days_requested == 0:
                messages.error(request, "Your selected dates contain no working days (weekend or holiday).")
                return render(request, 'leave/leave_apply.html', {'form': form, 'stats': stats})

            if leave.days_requested > stats['remaining']:
                messages.error(request, f"Insufficient balance. You requested {leave.days_requested} days but only have {stats['remaining']} remaining.")
                return render(request, 'leave/leave_apply.html', {'form': form, 'stats': stats})

            leave.save()
            messages.success(request, f"Leave request submitted for {leave.days_requested} working days.")
            return redirect('leave_home')
    else:
        form = LeaveRequestForm()

    return render(request, 'leave/leave_apply.html', {'form': form, 'stats': stats})


@login_required
def leave_cancel(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk, user=request.user)
    if leave.status == 'pending':
        leave.status = 'cancelled'
        leave.save()
        messages.info(request, "Leave request cancelled.")
    else:
        messages.error(request, "You can only cancel pending requests.")
    return redirect('leave_home')


@login_required
@user_passes_test(is_admin)
def leave_pending(request):
    pending = LeaveRequest.objects.filter(status='pending').select_related('user')
    return render(request, 'leave/leave_pending.html', {'pending': pending})


@login_required
@user_passes_test(is_admin)
def leave_review(request, pk, action):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if leave.status != 'pending':
        messages.warning(request, "This request has already been reviewed.")
        return redirect('leave_pending')

    if action == 'approve':
        stats = get_user_leave_stats(leave.user)
        if leave.days_requested > stats['remaining']:
            messages.error(request, f"Cannot approve. {leave.user.username} only has {stats['remaining']} days remaining.")
            return redirect('leave_pending')

        leave.status = 'approved'
        leave.save()
        messages.success(request, f"Approved {leave.days_requested} days for {leave.user.username}.")

    elif action == 'reject':
        leave.status = 'rejected'
        leave.save()
        messages.warning(request, f"Rejected leave for {leave.user.username}.")

    leave.reviewed_by = request.user
    leave.reviewed_at = timezone.now()
    leave.save()

    return redirect('leave_pending')