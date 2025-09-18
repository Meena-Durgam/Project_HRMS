from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max
from django.core.exceptions import PermissionDenied
from .models import Overtime
from .forms import OvertimeForm
from .utils import is_hr_user
from django.contrib.auth import get_user_model
from notifications.utils import notify_roles

User = get_user_model()

@login_required
def overtime_list(request):
    user = request.user

    # Filter based on role
    if user.role == 'company_owner':
        overtimes = Overtime.objects.filter(company=user.company)
    elif user.role == 'employee':
        overtimes = Overtime.objects.filter(company=user.company, employee=user)
    else:
        overtimes = Overtime.objects.none()

    # Group and annotate overtime by employee
    grouped_overtimes = (
        overtimes.values(
            'employee__id',
            'employee__first_name',
            'employee__last_name',
            'assigned_by__email',
        )
        .annotate(
            ot_id=Max('id'),
            total_hours=Sum('hours'),
            latest_date=Max('date'),
            latest_ot_type=Max('ot_type'),
        )
        .order_by('employee__first_name')
    )

    # Forms for all overtimes (edit forms) keyed by overtime id
    overtime_forms = {ot.id: OvertimeForm(instance=ot, user=user) for ot in overtimes}

    # Form for adding new overtime
    add_form = OvertimeForm(user=user)

    hr_employees = User.objects.filter(
        employee_account__department__name__iexact='HR',
        company=user.company
    )

    context = {
        'grouped_overtimes': grouped_overtimes,
        'employee_count': grouped_overtimes.count(),
        'total_hours': overtimes.aggregate(Sum('hours'))['hours__sum'] or 0,
        'employees': User.objects.filter(role='employee', company=user.company),
        'hr_employees': hr_employees,
        'overtime_forms': overtime_forms,
        'add_form': add_form,
    }
    return render(request, 'overtime.html', context)

from django.contrib import messages

@login_required
def add_overtime(request):
    user = request.user

    if not is_hr_user(user) and user.role != 'company_owner':
        messages.error(request, "Only HR users or company owners can add overtime.")
        return redirect('overtime_list')

    if request.method == 'POST':
        form = OvertimeForm(request.POST, user=user)
        if form.is_valid():
            overtime = form.save(commit=False)
            overtime.company = user.company

            if user.role == 'employee':
                overtime.employee = user
                overtime.assigned_by = None
            else:
                assigned_by_id = request.POST.get('assigned_by')
                if assigned_by_id:
                    overtime.assigned_by_id = assigned_by_id
                else:
                    overtime.assigned_by = user

            overtime.save()

            messages.success(request, f"Overtime added successfully for {overtime.employee.get_full_name()}.")

            notify_roles(
                roles=['employee'],
                message=f"{request.user.username} added an overtime record for {overtime.employee.get_full_name()}",
                url='/overtime/',
                sender=request.user
            )
            return redirect('overtime_list')
        else:
            messages.error(request, "There was an error in the form. Please correct it and try again.")

    return redirect('overtime_list')

@login_required
def edit_overtime(request, pk):
    ot = get_object_or_404(Overtime, id=pk)

    if request.method == 'POST':
        form = OvertimeForm(request.POST, instance=ot)
        if form.is_valid():
            updated_ot = form.save(commit=False)
            # Keep the old assigned_by intact (not overwritten by form)
            updated_ot.assigned_by = ot.assigned_by
            updated_ot.save()

            messages.success(request, f"Overtime updated successfully for {updated_ot.employee.get_full_name()}.")

            notify_roles(
                roles=['employee'],
                message=f"{request.user.username} updated overtime for {updated_ot.employee.get_full_name()}",
                url='/overtime/',
                sender=request.user
            )
            return redirect('overtime_list')
        else:
            messages.error(request, "Failed to update overtime. Please check the form for errors.")

    return redirect('overtime_list')



@login_required
def delete_overtime(request, pk):
    ot = get_object_or_404(Overtime, id=pk)
    if request.method == 'POST':
        ot_employee_name = ot.employee.get_full_name()
        ot.delete()

        messages.success(request, f"Overtime record deleted for {ot_employee_name}.")

        notify_roles(
            roles=['employee'],
            message=f"{request.user.username} deleted overtime record of {ot_employee_name}",
            url='/overtime/',
            sender=request.user
        )
        return redirect('overtime_list')

    messages.error(request, "Invalid request method for deleting overtime.")
    return redirect('overtime_list')
